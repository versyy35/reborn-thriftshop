// Sample product data
const products = [
    {
        id: 1,
        name: "Vintage T-Shirt",
        price: 12.99,
        condition: "Good",
        image: "tshirt",
        description: "Comfortable vintage t-shirt"
    },
    {
        id: 2,
        name: "Denim Jeans",
        price: 24.50,
        condition: "Excellent",
        image: "jeans",
        description: "Classic blue denim jeans"
    },
    {
        id: 3,
        name: "Coffee Table",
        price: 45.00,
        condition: "Good",
        image: "table",
        description: "Wooden coffee table"
    },
    {
        id: 4,
        name: "Leather Bag",
        price: 18.75,
        condition: "Fair",
        image: "bag",
        description: "Vintage leather bag"
    },
    {
        id: 5,
        name: "Book Collection",
        price: 15.25,
        condition: "Good",
        image: "books",
        description: "Set of 5 classic novels"
    },
    {
        id: 6,
        name: "Plant Pot",
        price: 8.99,
        condition: "Like New",
        image: "pot",
        description: "Ceramic plant pot"
    }
];

// Product images using emoji icons
const productImages = {
    "tshirt": `<div class="text-6xl flex justify-center items-center h-32">👕</div>`,
    "jeans": `<div class="text-6xl flex justify-center items-center h-32">👖</div>`,
    "table": `<div class="text-6xl flex justify-center items-center h-32">🪑</div>`,
    "bag": `<div class="text-6xl flex justify-center items-center h-32">👜</div>`,
    "books": `<div class="text-6xl flex justify-center items-center h-32">📚</div>`,
    "pot": `<div class="text-6xl flex justify-center items-center h-32">🪴</div>`
};

// Cart state
let cart = [];
let cartOpen = false;

// DOM elements
const productsContainer = document.getElementById('products-container');
const cartButton = document.getElementById('cart-button');
const cartSidebar = document.getElementById('cart-sidebar');
const closeCartButton = document.getElementById('close-cart');
const overlay = document.getElementById('overlay');
const cartItemsContainer = document.getElementById('cart-items');
const emptyCartMessage = document.getElementById('empty-cart-message');
const cartSubtotal = document.getElementById('cart-subtotal');
const cartCount = document.getElementById('cart-count');
const checkoutButton = document.getElementById('checkout-button');
const continueShoppingButton = document.getElementById('continue-shopping');
const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');

// Checkout elements
const checkoutModal = document.getElementById('checkout-modal');
const closeCheckoutButton = document.getElementById('close-checkout');
const shippingStep = document.getElementById('shipping-step');
const paymentStep = document.getElementById('payment-step');
const confirmationStep = document.getElementById('confirmation-step');
const shippingForm = document.getElementById('shipping-form');
const paymentForm = document.getElementById('payment-form');
const backToShippingButton = document.getElementById('back-to-shipping');
const paymentSubtotal = document.getElementById('payment-subtotal');
const paymentTotal = document.getElementById('payment-total');
const continueShoppingConfirmation = document.getElementById('continue-shopping-confirmation');
const orderNumber = document.getElementById('order-number');

// Initialize the page
function init() {
    renderProducts();
    setupEventListeners();
}

// Render all products
function renderProducts() {
    productsContainer.innerHTML = '';
    
    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.className = 'bg-white rounded shadow p-4';
        
        productCard.innerHTML = `
            <div class="bg-green-50 rounded p-2 mb-3">
                ${productImages[product.image]}
            </div>
            <h3 class="text-lg font-semibold text-green-800 mb-1">${product.name}</h3>
            <div class="flex justify-between items-center mb-2">
                <span class="text-lg font-bold text-green-600">RM ${product.price.toFixed(2)}</span>
                <span class="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">${product.condition}</span>
            </div>
            <p class="text-gray-600 text-sm mb-3">${product.description}</p>
            <button class="add-to-cart-btn w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 transition" data-id="${product.id}">
                Add to Cart
            </button>
        `;
        
        productsContainer.appendChild(productCard);
    });
}

// Set up event listeners
function setupEventListeners() {
    // Add to cart buttons
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', () => {
            const productId = parseInt(button.getAttribute('data-id'));
            addToCart(productId);
        });
    });
    
    // Cart toggle
    cartButton.addEventListener('click', toggleCart);
    closeCartButton.addEventListener('click', toggleCart);
    overlay.addEventListener('click', toggleCart);
    continueShoppingButton.addEventListener('click', toggleCart);
    
    // Checkout button
    checkoutButton.addEventListener('click', () => {
        if (cart.length > 0) {
            openCheckout();
        }
    });
    
    // Mobile menu toggle
    mobileMenuButton.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
    });
    
    // Checkout form events
    closeCheckoutButton.addEventListener('click', closeCheckout);
    shippingForm.addEventListener('submit', function(e) {
        e.preventDefault();
        goToPaymentStep();
    });
    backToShippingButton.addEventListener('click', goToShippingStep);
    paymentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        completeOrder();
    });
    continueShoppingConfirmation.addEventListener('click', () => {
        closeCheckout();
        resetCart();
    });
}

// Add product to cart
function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    
    if (product) {
        // Check if product is already in cart
        const existingItem = cart.find(item => item.id === productId);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({
                ...product,
                quantity: 1
            });
        }
        
        updateCart();
        
        // Show cart if it's not already open
        if (!cartOpen) {
            toggleCart();
        }
    }
}

// Update cart UI
function updateCart() {
    // Update cart count
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    cartCount.textContent = totalItems;
    
    // Enable/disable checkout button
    checkoutButton.disabled = totalItems === 0;
    
    // Show/hide empty cart message
    if (totalItems === 0) {
        emptyCartMessage.classList.remove('hidden');
    } else {
        emptyCartMessage.classList.add('hidden');
    }
    
    // Update cart items
    renderCartItems();
    
    // Update subtotal
    updateSubtotal();
}

// Render cart items
function renderCartItems() {
    // Clear previous items but keep the empty message
    const items = cartItemsContainer.querySelectorAll('.cart-item');
    items.forEach(item => item.remove());
    
    // Add current items
    cart.forEach(item => {
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item flex items-start border-b border-gray-200 py-3';
        
        cartItem.innerHTML = `
            <div class="h-12 w-12 bg-green-50 rounded overflow-hidden mr-3 flex-shrink-0">
                ${productImages[item.image]}
            </div>
            <div class="flex-grow">
                <div class="flex justify-between">
                    <h4 class="font-medium text-green-800">${item.name}</h4>
                    <span class="font-medium text-green-600">RM ${(item.price * item.quantity).toFixed(2)}</span>
                </div>
                <div class="flex justify-between items-center mt-1">
                    <div class="flex items-center border rounded">
                        <button class="decrease-quantity px-2 py-0.5 text-gray-600 hover:bg-gray-100" data-id="${item.id}">-</button>
                        <span class="px-2">${item.quantity}</span>
                        <button class="increase-quantity px-2 py-0.5 text-gray-600 hover:bg-gray-100" data-id="${item.id}">+</button>
                    </div>
                    <button class="remove-item text-gray-500 hover:text-red-500" data-id="${item.id}">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            </div>
        `;
        
        cartItemsContainer.insertBefore(cartItem, emptyCartMessage);
        
        // Add event listeners for cart item buttons
        cartItem.querySelector('.decrease-quantity').addEventListener('click', () => {
            decreaseQuantity(item.id);
        });
        
        cartItem.querySelector('.increase-quantity').addEventListener('click', () => {
            increaseQuantity(item.id);
        });
        
        cartItem.querySelector('.remove-item').addEventListener('click', () => {
            removeFromCart(item.id);
        });
    });
}

// Update cart subtotal
function updateSubtotal() {
    const subtotal = cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    cartSubtotal.textContent = `RM ${subtotal.toFixed(2)}`;
    
    // Also update payment page totals
    paymentSubtotal.textContent = `RM ${subtotal.toFixed(2)}`;
    paymentTotal.textContent = `RM ${(subtotal + 5).toFixed(2)}`;
}

// Toggle cart sidebar
function toggleCart() {
    cartOpen = !cartOpen;
    
    if (cartOpen) {
        cartSidebar.classList.remove('translate-x-full');
        overlay.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
    } else {
        cartSidebar.classList.add('translate-x-full');
        overlay.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }
}

// Increase item quantity
function increaseQuantity(productId) {
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity += 1;
        updateCart();
    }
}

// Decrease item quantity
function decreaseQuantity(productId) {
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity -= 1;
        
        if (item.quantity <= 0) {
            removeFromCart(productId);
        } else {
            updateCart();
        }
    }
}

// Remove item from cart
function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCart();
}

// Open checkout modal
function openCheckout() {
    // Close cart first
    toggleCart();
    
    // Reset checkout to first step
    goToShippingStep();
    
    // Show checkout modal
    checkoutModal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
}

// Close checkout modal
function closeCheckout() {
    checkoutModal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
}

// Go to shipping step
function goToShippingStep() {
    shippingStep.classList.remove('hidden');
    paymentStep.classList.add('hidden');
    confirmationStep.classList.add('hidden');
}

// Go to payment step
function goToPaymentStep() {
    shippingStep.classList.add('hidden');
    paymentStep.classList.remove('hidden');
    confirmationStep.classList.add('hidden');
}

// Complete order
function completeOrder() {
    shippingStep.classList.add('hidden');
    paymentStep.classList.add('hidden');
    confirmationStep.classList.remove('hidden');
    
    // Generate random order number
    const randomNum = Math.floor(10000 + Math.random() * 90000);
    orderNumber.textContent = `RB-${randomNum}`;
}

// Reset cart after order
function resetCart() {
    cart = [];
    updateCart();
}

// Initialize the page
init();