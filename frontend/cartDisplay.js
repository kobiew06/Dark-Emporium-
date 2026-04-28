// This function renders all cart items and the running total.
function displayCart() {

    const table =
        document.getElementById(
            "cart-items"
        );

    let total = 0;

    table.innerHTML = "";

    if (cart.length === 0) {

        table.innerHTML =
            "<tr><td colspan='5'>Cart is empty</td></tr>";

        document.getElementById(
            "cart-total"
        ).innerText =
            "Total: $0.00";

        return;
    }

    cart.forEach(item => {

        const row =
            document.createElement("tr");

        const itemTotal =
            item.price * item.quantity;

        total += itemTotal;

        row.innerHTML = `
        <td>${item.name}</td>
        <td>$${item.price.toFixed(2)}</td>
        <td>
            <button onclick="changeQuantity('${item.id}', -1)">-</button>
            <span style="margin:0 8px;">${item.quantity}</span>
            <button onclick="changeQuantity('${item.id}', 1)">+</button>
        </td>
        <td>$${itemTotal.toFixed(2)}</td>
        <td>
            <button onclick="removeItem('${item.id}')">Remove</button>
        </td>
        `;

        table.appendChild(row);

    });

    document.getElementById(
        "cart-total"
    ).innerText =
        "Total: $" +
        total.toFixed(2);

}

// This function updates quantity by +1 or -1 and prevents quantities below 1.
function changeQuantity(id, delta) {

    const item =
        cart.find(
            product =>
                product.id === id
        );

    if (!item) {
        return;
    }

    item.quantity += delta;

    if (item.quantity <= 0) {
        cart = cart.filter(product => product.id !== id);
    }

    saveCart();
    updateCartCount();
    displayCart();

}

// This function removes a single item from the cart.
function removeItem(id) {

    cart =
        cart.filter(
            item =>
                item.id !== id
        );

    saveCart();
    updateCartCount();
    displayCart();

}

// This function removes all items from the cart.
function clearCart() {

    cart = [];

    saveCart();
    updateCartCount();
    displayCart();

}

// This function submits checkout details and cart items to the backend.
async function completeSale(event) {
    event.preventDefault();

    const message = document.getElementById("checkout-message");
    const email = document.getElementById("checkout-email").value.trim();
    const phone = document.getElementById("checkout-phone").value.trim();
    const suburb = document.getElementById("checkout-suburb").value.trim();

    if (cart.length === 0) {
        message.innerText = "Your cart is empty.";
        return;
    }

    const payload = {
        email,
        phone,
        suburb,
        items: cart.map(item => ({
            id: Number(item.id),
            quantity: Number(item.quantity)
        }))
    };

    try {
        const response = await fetch("/api/checkout", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            message.innerText = data.message || "Checkout failed.";
            return;
        }

        message.innerText =
            "Sale #" +
            data.sale_id +
            " completed. Total: $" +
            Number(data.total_sell).toFixed(2);

        clearCart();
        document.getElementById("checkout-form").reset();
    } catch (error) {
        message.innerText = "Could not connect to backend.";
    }
}

// This listener connects the checkout form to the sale submission function.
document.addEventListener("DOMContentLoaded", () => {
    const checkoutForm = document.getElementById("checkout-form");
    if (checkoutForm) {
        checkoutForm.addEventListener("submit", completeSale);
    }
});

// This initial render displays any previously saved cart data.
displayCart();