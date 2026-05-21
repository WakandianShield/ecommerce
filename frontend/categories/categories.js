const CART_KEY = 'sg_cart_items';

function getCart() {
    try { return JSON.parse(localStorage.getItem(CART_KEY) || '[]'); }
    catch { return []; }
}

function saveCart(items) {
    localStorage.setItem(CART_KEY, JSON.stringify(items));
    const total = items.reduce((s, i) => s + i.price * i.qty, 0);
    localStorage.setItem('sg_cart_summary', JSON.stringify({ items, total }));
}

function addToCart(name, price, img) {
    const cart = getCart();
    const existing = cart.find(i => i.name === name);
    if (existing) {
        existing.qty++;
    } else {
        cart.push({ name, price, qty: 1, img: img || '' });
    }
    saveCart(cart);
    showToast(`"${name}" agregado al carrito`);
}

function showToast(msg) {
    let toast = document.getElementById('cart-toast');
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toast.classList.remove('show'), 2400);
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.item-card').forEach(card => {
        const btn = card.querySelector('.add-cart-btn');
        const name = card.querySelector('h4')?.textContent?.trim();
        const priceText = card.querySelector('.price')?.textContent?.trim() || '$0';
        const price = parseFloat(priceText.replace(/[^0-9.]/g, '')) || 0;
        const img = card.querySelector('.image-box img')?.getAttribute('src') || '';

        if (btn && name) {
            btn.addEventListener('click', () => addToCart(name, price, img));
        }
    });
});
