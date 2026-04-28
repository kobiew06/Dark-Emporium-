let cart =
    JSON.parse(
        localStorage.getItem("cart")
    ) || [];


// Add click events to buttons
document.addEventListener(
    "DOMContentLoaded",
    () => {

        const buttons =
            document.querySelectorAll(
                ".btn-add"
            );

        buttons.forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    const id =
                        button.dataset.id;

                    const name =
                        button.dataset.name;

                    const price =
                        parseFloat(
                            button.dataset.price
                        );

                    addToCart(
                        id,
                        name,
                        price
                    );

                }
            );

        });

        updateCartCount();

    }
);


// Add item function
function addToCart(
    id,
    name,
    price
) {

    const existing =
        cart.find(
            item =>
                item.id === id
        );

    if (existing) {

        existing.quantity++;

    } else {

        cart.push({

            id: id,
            name: name,
            price: price,
            quantity: 1

        });

    }

    saveCart();

    updateCartCount();

    alert(name + " added!");

}


// Save cart
function saveCart() {

    localStorage.setItem(
        "cart",
        JSON.stringify(cart)
    );

}


// Update cart number in header
function updateCartCount() {

    const cartBtn =
        document.querySelector(
            ".cart-btn"
        );

    if (!cartBtn) return;

    let count = 0;

    cart.forEach(item => {

        count += item.quantity;

    });

    cartBtn.innerHTML =
        "🛒 Cart (" +
        count +
        ")";

}