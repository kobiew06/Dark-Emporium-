// This function fetches completed sales and updates admin summary tables.
async function loadSales() {
    const message = document.getElementById("admin-message");
    const salesBody = document.getElementById("sales-body");
    const salesItems = document.getElementById("sales-items");

    const adminKey = document.getElementById("admin-key").value.trim();

    message.innerText = "";
    salesBody.innerHTML = "";
    salesItems.innerHTML = "";

    try {
        const response = await fetch(
            "/api/admin/sales?admin_key=" + encodeURIComponent(adminKey)
        );

        const data = await response.json();

        if (!response.ok) {
            message.innerText = data.message || "Failed to load sales.";
            return;
        }

        if (data.length === 0) {
            message.innerText = "No completed sales yet.";
            return;
        }

        data.forEach(sale => {
            const row = document.createElement("tr");
            row.innerHTML =
                "<td>" + sale.sale_id + "</td>" +
                "<td>" + sale.email + "</td>" +
                "<td>" + sale.phone + "</td>" +
                "<td>" + sale.suburb + "</td>" +
                "<td>$" + Number(sale.total_cost).toFixed(2) + "</td>" +
                "<td>$" + Number(sale.total_sell).toFixed(2) + "</td>" +
                "<td>$" + Number(sale.profit).toFixed(2) + "</td>" +
                "<td>" + sale.created_at + "</td>";
            salesBody.appendChild(row);

            const detailBlock = document.createElement("div");
            detailBlock.style.marginBottom = "20px";

            const title = document.createElement("h3");
            title.innerText = "Sale #" + sale.sale_id + " Items";
            detailBlock.appendChild(title);

            const list = document.createElement("ul");
            sale.items.forEach(item => {
                const listItem = document.createElement("li");
                listItem.innerText =
                    item.title +
                    " | Qty: " + item.quantity +
                    " | Cost: $" + Number(item.cost_price).toFixed(2) +
                    " | Sell: $" + Number(item.sell_price).toFixed(2) +
                    " | Line Cost: $" + Number(item.line_cost).toFixed(2) +
                    " | Line Sell: $" + Number(item.line_sell).toFixed(2);
                list.appendChild(listItem);
            });

            detailBlock.appendChild(list);
            salesItems.appendChild(detailBlock);
        });
    } catch (error) {
        message.innerText = "Could not connect to backend.";
    }
}

// This listener connects the button to the admin sales fetch action.
document.addEventListener("DOMContentLoaded", () => {
    document
        .getElementById("load-sales")
        .addEventListener("click", loadSales);
});
