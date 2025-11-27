const Cart = {
    getUserId() {
        const token = localStorage.getItem('token');
        if (!token) return null;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const now = Math.floor(Date.now() / 1000);
            if (payload.exp && payload.exp < now) {
                return null;
            }
            return payload.id;
        } catch (e) {
            return null;
        }
    },

    get KEY() {
        const userId = this.getUserId();
        return userId ? `bookstore_cart_${userId}` : 'bookstore_cart';
    },

    getAll() {
        const cartJson = localStorage.getItem(this.KEY);
        return cartJson ? JSON.parse(cartJson) : [];
    },

    add(product, quantity = 1) {
        const cart = this.getAll();
        const existingItemIndex = cart.findIndex(item => item.id === product.id);

        if (existingItemIndex > -1) {
            cart[existingItemIndex].quantity += quantity;
        } else {
            cart.push({
                id: product.id,
                title: product.title,
                price: product.price,
                image_url: product.image_url,
                quantity: quantity
            });
        }

        this.save(cart);
        this.updateBadge();
    },

    updateQuantity(productId, quantity) {
        const cart = this.getAll();
        const itemIndex = cart.findIndex(item => item.id === productId);

        if (itemIndex > -1) {
            if (quantity <= 0) {
                cart.splice(itemIndex, 1);
            } else {
                cart[itemIndex].quantity = quantity;
            }
            this.save(cart);
            this.updateBadge();
        }
    },

    remove(productId) {
        let cart = this.getAll();
        cart = cart.filter(item => item.id !== productId);
        this.save(cart);
        this.updateBadge();
    },

    clear() {
        localStorage.removeItem(this.KEY);
        this.updateBadge();
    },

    save(cart) {
        localStorage.setItem(this.KEY, JSON.stringify(cart));
    },

    getCount() {
        const cart = this.getAll();
        return cart.reduce((total, item) => total + item.quantity, 0);
    },

    getTotal() {
        const cart = this.getAll();
        return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    },

    updateBadge() {
        const badge = document.getElementById('cartBadge');
        if (badge) {
            // Check if user is logged in
            if (!this.getUserId()) {
                badge.style.display = 'none';
                return;
            }

            const count = this.getCount();
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }
};

// Initialize badge on load
document.addEventListener('DOMContentLoaded', () => {
    Cart.updateBadge();
});
