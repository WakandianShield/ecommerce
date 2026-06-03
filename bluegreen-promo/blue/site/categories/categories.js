const CART_KEY = 'sg_cart_items';
const STOCK_MODAL_ID = 'sg-stock-modal';

function getCart() {
    try { return JSON.parse(localStorage.getItem(CART_KEY) || '[]'); }
    catch { return []; }
}

function saveCart(items) {
    localStorage.setItem(CART_KEY, JSON.stringify(items));
    const total = items.reduce((s, i) => s + i.price * i.qty, 0);
    localStorage.setItem('sg_cart_summary', JSON.stringify({ items, total }));
}

function normalizeKey(value) {
    return (value || '')
        .normalize('NFKD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

function getCartQtyByName(name) {
    const key = normalizeKey(name);
    const cart = getCart();
    const item = cart.find((i) => normalizeKey(i.name) === key);
    return item ? Number(item.qty) || 0 : 0;
}

function addToCart(name, price, img, productId) {
    const cart = getCart();
    const key = normalizeKey(name);
    const existing = cart.find(i => normalizeKey(i.name) === key);
    if (existing) {
        existing.qty++;
        if (productId && !existing.product_id) existing.product_id = productId;
    } else {
        cart.push({ product_id: productId || null, name, price, qty: 1, img: img || '' });
    }
    saveCart(cart);
    showToast(`"${name}" agregado al carrito`);
}

function showToast(msg) {
    let toast = document.getElementById('cart-toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toast.classList.remove('show'), 2400);
}

function ensureStockModal() {
    let modal = document.getElementById(STOCK_MODAL_ID);
    if (modal) return modal;

    modal = document.createElement('div');
    modal.id = STOCK_MODAL_ID;
    modal.className = 'sg-modal';
    modal.innerHTML = `
        <div class="sg-modal__card" role="dialog" aria-modal="true" aria-labelledby="sg-modal-title">
            <h3 id="sg-modal-title" class="sg-modal__title">Stock insuficiente</h3>
            <p class="sg-modal__body">No hay stock suficiente para agregar mas unidades.</p>
            <div class="sg-modal__actions">
                <button type="button" class="sg-modal__btn" data-action="close">Cerrar</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    modal.addEventListener('click', (event) => {
        if (event.target === modal) hideStockModal();
    });

    const closeBtn = modal.querySelector('[data-action="close"]');
    if (closeBtn) {
        closeBtn.addEventListener('click', hideStockModal);
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') hideStockModal();
    });

    return modal;
}

function showStockModal({ title, message }) {
    const modal = ensureStockModal();
    const titleEl = modal.querySelector('.sg-modal__title');
    const bodyEl = modal.querySelector('.sg-modal__body');
    if (titleEl) titleEl.textContent = title;
    if (bodyEl) bodyEl.textContent = message;
    modal.classList.add('is-visible');
}

function hideStockModal() {
    const modal = document.getElementById(STOCK_MODAL_ID);
    if (modal) modal.classList.remove('is-visible');
}

function ensureFullNavbar() {
    const navLinks = document.querySelector('nav .nav-links');
    if (!navLinks) return;

    const cartLink = navLinks.querySelector('a[aria-label="Carrito"]');
    const hasCatalog = navLinks.querySelector('a[aria-label="Catalogo"]');
    const hasChat = navLinks.querySelector('a[aria-label="Chat"]');

    if (!hasCatalog) {
        const catalogLink = document.createElement('a');
        catalogLink.href = '../catalog/catalog.html';
        catalogLink.className = 'nav-icon';
        catalogLink.setAttribute('aria-label', 'Catalogo');
        catalogLink.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>';
        navLinks.insertBefore(catalogLink, cartLink || navLinks.firstChild);
    }

    if (!hasChat) {
        const chatLink = document.createElement('a');
        chatLink.href = '../chat/chat.html';
        chatLink.className = 'nav-icon';
        chatLink.setAttribute('aria-label', 'Chat');
        chatLink.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a4 4 0 0 1-4 4H7l-4 4V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"></path></svg>';
        navLinks.insertBefore(chatLink, cartLink || navLinks.firstChild);
    }
}

function getCategoryName() {
    return document.querySelector('.category-title')?.textContent?.trim() || '';
}

async function loadStockMap() {
    if (typeof sgApi !== 'function') return null;
    const categoryKey = normalizeKey(getCategoryName());
    if (!categoryKey) return null;

    try {
        const data = await sgApi('/products');
        const products = Array.isArray(data) ? data : [];
        const map = new Map();
        products.forEach((product) => {
            const productCategory = normalizeKey(product.category);
            if (productCategory !== categoryKey) return;
            const nameKey = normalizeKey(product.name);
            if (nameKey) map.set(nameKey, product);
        });
        return map;
    } catch {
        return null;
    }
}

function ensureStockLabel(card) {
    let label = card.querySelector('.product-stock');
    if (label) return label;
    const details = card.querySelector('.item-details');
    const priceAction = details?.querySelector('.price-action');
    if (!details || !priceAction) return null;
    label = document.createElement('div');
    label.className = 'product-stock';
    details.insertBefore(label, priceAction);
    return label;
}

function getCardStock(card) {
    const raw = card.dataset.stock;
    if (raw === undefined || raw === '') return null;
    const value = Number(raw);
    return Number.isFinite(value) ? value : null;
}

function updateCardAvailability(card, name, stock) {
    const btn = card.querySelector('.add-cart-btn');
    if (!btn) return;
    if (stock === null || stock === undefined || Number.isNaN(stock)) {
        btn.disabled = false;
        btn.classList.remove('is-disabled');
        return;
    }

    const cartQty = getCartQtyByName(name);
    const disabled = stock <= 0 || cartQty >= stock;
    btn.disabled = disabled;
    btn.classList.toggle('is-disabled', disabled);
}

function applyStockToCard(card, name, product) {
    const label = ensureStockLabel(card);
    if (!label) return;

    if (!product) {
        label.textContent = 'Stock: --';
        label.classList.remove('product-stock--out');
        card.dataset.stock = '';
        updateCardAvailability(card, name, null);
        return;
    }

    const stock = Number(product.stock);
    const normalizedStock = Number.isFinite(stock) ? stock : 0;
    card.dataset.stock = String(normalizedStock);
    card.dataset.productId = product.id;
    label.textContent = `Stock: ${normalizedStock}`;
    label.classList.toggle('product-stock--out', normalizedStock <= 0);
    updateCardAvailability(card, name, normalizedStock);
}

document.addEventListener('DOMContentLoaded', async () => {
    ensureFullNavbar();

    const cards = Array.from(document.querySelectorAll('.item-card'));
    const stockMap = await loadStockMap();

    cards.forEach((card) => {
        const name = card.querySelector('h4')?.textContent?.trim();
        if (!name) return;
        const product = stockMap ? stockMap.get(normalizeKey(name)) : null;
        applyStockToCard(card, name, product || null);
    });

    cards.forEach((card) => {
        const btn = card.querySelector('.add-cart-btn');
        const name = card.querySelector('h4')?.textContent?.trim();
        const priceText = card.querySelector('.price')?.textContent?.trim() || '$0';
        const price = parseFloat(priceText.replace(/[^0-9.]/g, '')) || 0;
        const img = card.querySelector('.image-box img')?.getAttribute('src') || '';

        if (btn && name) {
            btn.addEventListener('click', () => {
                const stock = getCardStock(card);
                const cartQty = getCartQtyByName(name);
                if (stock !== null && cartQty + 1 > stock) {
                    showStockModal({
                        title: 'Stock insuficiente',
                        message: `Solo hay ${stock} unidades disponibles.`,
                    });
                    return;
                }

                addToCart(name, price, img, card.dataset.productId || null);
                updateCardAvailability(card, name, stock);
            });
        }
    });
});
