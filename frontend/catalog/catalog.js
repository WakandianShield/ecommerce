const grid = document.getElementById('catalogGrid');
const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const clearBtn = document.getElementById('clearFilters');
const cartCount = document.getElementById('cartCount');

const CART_KEY = 'sg_cart_items';

let products = [];

function formatMoney(cents) {
    const value = (Number(cents) || 0) / 100;
    return `$${value.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
}

function getCart() {
    try { return JSON.parse(localStorage.getItem(CART_KEY) || '[]'); }
    catch { return []; }
}

function saveCart(items) {
    localStorage.setItem(CART_KEY, JSON.stringify(items));
}

function updateCartCount() {
    const cart = getCart();
    const totalQty = cart.reduce((sum, item) => sum + (Number(item.qty) || 0), 0);
    cartCount.textContent = totalQty;
}

function addToCart(product) {
    const imageUrl = product.image_url
        ? (product.image_url.startsWith('/') ? `${API_BASE}${product.image_url}` : product.image_url)
        : '';
    const cart = getCart();
    const existing = cart.find((item) => item.product_id === product.id);
    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({
            product_id: product.id,
            name: product.name,
            price: (Number(product.price_cents) || 0) / 100,
            qty: 1,
            img: imageUrl,
        });
    }
    saveCart(cart);
    updateCartCount();
}

function renderProducts(list) {
    if (!list.length) {
        grid.innerHTML = '<div class="state-card">No hay productos disponibles.</div>';
        return;
    }

    grid.innerHTML = list.map((product) => {
        const imageUrl = product.image_url
            ? (product.image_url.startsWith('/') ? `${API_BASE}${product.image_url}` : product.image_url)
            : '';
        const hasImage = Boolean(imageUrl);
        const stock = Number(product.stock) || 0;
        const disabled = stock <= 0;
        return `
            <article class="product-card">
                <div class="product-media">
                    ${hasImage ? `<img src="${imageUrl}" alt="${product.name}">` : `<div class="product-placeholder">${product.name.slice(0, 1)}</div>`}
                </div>
                <div class="product-body">
                    <div>
                        <h3 class="product-title">${product.name}</h3>
                        <div class="product-meta">
                            <span>${product.category || 'Sin categoria'}</span>
                            <span>Stock: ${stock}</span>
                        </div>
                    </div>
                    <div class="product-price">${formatMoney(product.price_cents)}</div>
                    <div class="product-actions">
                        <button class="btn-primary ${disabled ? 'btn-disabled' : ''}" data-id="${product.id}" ${disabled ? 'disabled' : ''}>Agregar</button>
                    </div>
                </div>
            </article>
        `;
    }).join('');
}

function applyFilters() {
    const query = searchInput.value.trim().toLowerCase();
    const category = categoryFilter.value;

    const filtered = products.filter((product) => {
        const text = `${product.name} ${product.description || ''} ${product.category || ''}`.toLowerCase();
        const matchesQuery = !query || text.includes(query);
        const matchesCategory = !category || product.category === category;
        return matchesQuery && matchesCategory;
    });

    renderProducts(filtered);
}

function buildCategories() {
    const categories = [...new Set(products.map(p => p.category).filter(Boolean))].sort();
    categoryFilter.innerHTML = '<option value="">Todas las categorias</option>';
    categories.forEach((category) => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });
}

async function loadCatalog() {
    try {
        const data = await sgApi('/products');
        products = Array.isArray(data) ? data.filter(p => p.is_active !== false) : [];
        buildCategories();
        applyFilters();
    } catch (err) {
        grid.innerHTML = `<div class="state-card">${err.message}</div>`;
    }
}

grid.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-id]');
    if (!btn) return;
    const product = products.find((item) => item.id === btn.dataset.id);
    if (product) addToCart(product);
});

searchInput.addEventListener('input', applyFilters);
categoryFilter.addEventListener('change', applyFilters);
clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    categoryFilter.value = '';
    applyFilters();
});

updateCartCount();
loadCatalog();
