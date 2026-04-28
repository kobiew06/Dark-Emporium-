"""
- Static frontend file serving.
- Product retrieval API.
- Checkout API with server-side validation.
- Admin sales summary API.
- SQLite database initialization from schema.sql.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory


# path for root project folder 
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# This path points to the frontend 
FRONTEND_DIR = PROJECT_ROOT / "frontend"
# This path points to the SQL schema/seed file used to build the SQLite database.
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
# This path is the SQLite database file that stores products and completed sales.
DB_PATH = PROJECT_ROOT / "database" / "shop.db"

# admin key
ADMIN_KEY = "admin"


# The Flask app serves frontend files directly from the existing frontend folder.
app = Flask(__name__, static_folder=None)


# patterns for validating details.
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_PATTERN = re.compile(r"^[0-9 +()-]{7,20}$")
SUBURB_PATTERN = re.compile(r"^[A-Za-z0-9 .'-]{2,60}$")


# This helper opens SQLite with row access by column name for cleaner code.
def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# This helper executes schema.sql when the database does not yet exist.
def initialize_database() -> None:
    if DB_PATH.exists():
        return

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(DB_PATH) as connection:
        connection.executescript(schema_sql)
        connection.commit()


# This helper validates shopper delivery details and returns field-level errors.
def validate_delivery_details(payload: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    email = str(payload.get("email", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    suburb = str(payload.get("suburb", "")).strip()

    if not EMAIL_PATTERN.fullmatch(email):
        errors["email"] = "Enter a valid email address."

    if not PHONE_PATTERN.fullmatch(phone):
        errors["phone"] = "Enter a valid phone number."

    if not SUBURB_PATTERN.fullmatch(suburb):
        errors["suburb"] = "Enter a valid suburb."

    return errors


# This helper validates cart items payload and extracts product IDs with quantities.
def validate_items(items: Any) -> tuple[list[tuple[int, int]], str | None]:
    if not isinstance(items, list) or not items:
        return [], "Cart items are required."

    normalized_items: list[tuple[int, int]] = []

    for item in items:
        if not isinstance(item, dict):
            return [], "Each cart item must be an object."

        try:
            product_id = int(item.get("id"))
            quantity = int(item.get("quantity"))
        except (TypeError, ValueError):
            return [], "Each cart item must include numeric id and quantity."

        if quantity < 1 or quantity > 99:
            return [], "Quantity must be between 1 and 99."

        normalized_items.append((product_id, quantity))

    return normalized_items, None


# This route serves the existing home page from the frontend folder.
@app.get("/")
def home() -> Any:
    return send_from_directory(FRONTEND_DIR, "index.html")


# This route serves all existing frontend files (HTML, JS, assets if added later).
@app.get("/<path:filename>")
def static_files(filename: str) -> Any:
    return send_from_directory(FRONTEND_DIR, filename)


# This endpoint returns products so frontend pages can use DB-driven data if needed.
@app.get("/api/products")
def get_products() -> Any:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, description, category, cost_price, sell_price, image_url
            FROM products
            ORDER BY id
            """
        ).fetchall()

    products = [dict(row) for row in rows]
    return jsonify(products)


# This endpoint processes checkout and stores both sale summary and line-item cost/sell details.
@app.post("/api/checkout")
def checkout() -> Any:
    payload = request.get_json(silent=True) or {}

    delivery_errors = validate_delivery_details(payload)
    if delivery_errors:
        return jsonify({"message": "Validation failed.", "errors": delivery_errors}), 400

    normalized_items, item_error = validate_items(payload.get("items"))
    if item_error:
        return jsonify({"message": item_error}), 400

    product_ids = [product_id for product_id, _ in normalized_items]
    placeholders = ", ".join(["?"] * len(product_ids))

    with get_connection() as connection:
        product_rows = connection.execute(
            f"""
            SELECT id, title, cost_price, sell_price
            FROM products
            WHERE id IN ({placeholders})
            """,
            product_ids,
        ).fetchall()

        products_by_id = {row["id"]: row for row in product_rows}

        line_items: list[dict[str, Any]] = []
        total_cost = 0.0
        total_sell = 0.0

        for product_id, quantity in normalized_items:
            product = products_by_id.get(product_id)
            if product is None:
                return jsonify({"message": f"Product id {product_id} was not found."}), 400

            line_cost = float(product["cost_price"]) * quantity
            line_sell = float(product["sell_price"]) * quantity
            total_cost += line_cost
            total_sell += line_sell

            line_items.append(
                {
                    "product_id": product_id,
                    "title": product["title"],
                    "quantity": quantity,
                    "cost_price": float(product["cost_price"]),
                    "sell_price": float(product["sell_price"]),
                    "line_cost": line_cost,
                    "line_sell": line_sell,
                }
            )

        cursor = connection.execute(
            """
            INSERT INTO sales (email, phone, suburb, total_cost, total_sell)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(payload.get("email", "")).strip(),
                str(payload.get("phone", "")).strip(),
                str(payload.get("suburb", "")).strip(),
                round(total_cost, 2),
                round(total_sell, 2),
            ),
        )
        sale_id = cursor.lastrowid

        for line in line_items:
            connection.execute(
                """
                INSERT INTO sale_items (
                    sale_id,
                    product_id,
                    quantity,
                    cost_price,
                    sell_price,
                    line_cost,
                    line_sell
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sale_id,
                    line["product_id"],
                    line["quantity"],
                    line["cost_price"],
                    line["sell_price"],
                    round(line["line_cost"], 2),
                    round(line["line_sell"], 2),
                ),
            )

        connection.commit()

    return jsonify(
        {
            "message": "Sale completed successfully.",
            "sale_id": sale_id,
            "total_sell": round(total_sell, 2),
        }
    )


# This endpoint gives admins a full sales summary including purchaser and margin information.
@app.get("/api/admin/sales")
def admin_sales_summary() -> Any:
    admin_key = request.args.get("admin_key", "")
    if admin_key != ADMIN_KEY:
        return jsonify({"message": "Unauthorized admin access."}), 403

    with get_connection() as connection:
        sales_rows = connection.execute(
            """
            SELECT id, email, phone, suburb, total_cost, total_sell, created_at
            FROM sales
            ORDER BY id DESC
            """
        ).fetchall()

        summary: list[dict[str, Any]] = []

        for sale in sales_rows:
            item_rows = connection.execute(
                """
                SELECT
                    si.product_id,
                    p.title,
                    si.quantity,
                    si.cost_price,
                    si.sell_price,
                    si.line_cost,
                    si.line_sell
                FROM sale_items si
                JOIN products p ON p.id = si.product_id
                WHERE si.sale_id = ?
                ORDER BY si.id
                """,
                (sale["id"],),
            ).fetchall()

            items = [dict(item) for item in item_rows]

            total_cost = float(sale["total_cost"])
            total_sell = float(sale["total_sell"])

            summary.append(
                {
                    "sale_id": sale["id"],
                    "email": sale["email"],
                    "phone": sale["phone"],
                    "suburb": sale["suburb"],
                    "total_cost": total_cost,
                    "total_sell": total_sell,
                    "profit": round(total_sell - total_cost, 2),
                    "created_at": sale["created_at"],
                    "items": items,
                }
            )

    return jsonify(summary)


# This endpoint helps verify the backend is online during demos.
@app.get("/api/health")
def health() -> Any:
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
