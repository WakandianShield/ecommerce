const tabs = document.querySelectorAll('[data-tab]');
const sections = document.querySelectorAll('[data-section]');

const productForm = document.getElementById('productForm');
const productList = document.getElementById('productList');
const productReset = document.getElementById('productReset');
const refreshProducts = document.getElementById('refreshProducts');

const ordersList = document.getElementById('adminOrdersList');
const refreshOrders = document.getElementById('refreshOrders');

const chatSessions = document.getElementById('chatSessions');
const chatMessages = document.getElementById('chatMessages');
const refreshChat = document.getElementById('refreshChat');

let products = [];
let activeSession = null;

function formatMoney(cents) {
    const value = (Number(cents) || 0) / 100;
    return `$${value.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
}

function setActiveTab(tab) {
    tabs.forEach((btn) => btn.classList.toggle('active', btn.dataset.tab === tab));
    sections.forEach((section) => section.classList.toggle('active', section.dataset.section === tab));
}

tabs.forEach((btn) => {
    btn.addEventListener('click', () => setActiveTab(btn.dataset.tab));
});

function resetProductForm() {
    productForm.reset();
    document.getElementById('productId').value = '';
    document.getElementById('productActive').checked = true;
}

function fillProductForm(product) {
    document.getElementById('productId').value = product.id;
    document.getElementById('productName').value = product.name || '';
    document.getElementById('productDescription').value = product.description || '';
    document.getElementById('productCategory').value = product.category || '';
    document.getElementById('productPrice').value = ((Number(product.price_cents) || 0) / 100).toFixed(2);
    document.getElementById('productStock').value = Number(product.stock) || 0;
    document.getElementById('productActive').checked = Boolean(product.is_active);
}

function renderProducts() {
    if (!products.length) {
        productList.innerHTML = '<div class="list-item">No hay productos registrados.</div>';
        return;
    }

    productList.innerHTML = products.map((product) => `
        <div class="list-item" data-id="${product.id}">
            <strong>${product.name}</strong>
            <span class="badge">${product.category || 'Sin categoria'}</span>
            <div>Precio: ${formatMoney(product.price_cents)} | Stock: ${product.stock}</div>
            <div class="list-actions">
                <button class="btn ghost" data-action="edit">Editar</button>
                <button class="btn ghost" data-action="delete">Eliminar</button>
            </div>
        </div>
    `).join('');
}

async function loadProducts() {
    try {
        const data = await sgApi('/products');
        products = Array.isArray(data) ? data : [];
        renderProducts();
    } catch (err) {
        productList.innerHTML = `<div class="list-item">${err.message}</div>`;
    }
}

async function uploadImage(productId, file) {
    const token = await sgGetToken();
    if (!token) throw new Error('No autorizado');

    const form = new FormData();
    form.append('file', file);

    const res = await fetch(`${API_BASE}/products/${productId}/image`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: form,
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error al subir imagen');
    return data;
}

productForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const productId = document.getElementById('productId').value;
    const payload = {
        name: document.getElementById('productName').value.trim(),
        description: document.getElementById('productDescription').value.trim(),
        category: document.getElementById('productCategory').value.trim(),
        price_cents: Math.round(Number(document.getElementById('productPrice').value) * 100),
        stock: Number(document.getElementById('productStock').value),
        is_active: document.getElementById('productActive').checked,
    };

    try {
        let product;
        if (productId) {
            product = await sgApi(`/products/${productId}`, { method: 'PUT', body: payload });
        } else {
            product = await sgApi('/products', { method: 'POST', body: payload });
        }

        const file = document.getElementById('productImage').files[0];
        if (file) {
            await uploadImage(product.id, file);
        }

        resetProductForm();
        await loadProducts();
    } catch (err) {
        alert(err.message);
    }
});

productReset.addEventListener('click', resetProductForm);
refreshProducts.addEventListener('click', loadProducts);

productList.addEventListener('click', async (e) => {
    const item = e.target.closest('[data-id]');
    if (!item) return;
    const id = item.dataset.id;
    const action = e.target.dataset.action;
    const product = products.find((p) => p.id === id);

    if (action === 'edit' && product) {
        fillProductForm(product);
    }

    if (action === 'delete') {
        if (!confirm('Eliminar producto?')) return;
        try {
            await sgApi(`/products/${id}`, { method: 'DELETE' });
            await loadProducts();
        } catch (err) {
            alert(err.message);
        }
    }
});

function renderOrders(orders) {
    if (!orders.length) {
        ordersList.innerHTML = '<div class="order-card">No hay ordenes.</div>';
        return;
    }

    ordersList.innerHTML = orders.map((order) => {
        const items = order.items.map((item) => `${item.name} x${item.quantity}`).join(', ');
        return `
            <div class="order-card" data-id="${order.id}">
                <h4>Orden ${order.id.slice(0, 8)}</h4>
                <div class="order-items">${items}</div>
                <p>Total: ${formatMoney(order.total_cents)}</p>
                <select class="status-select">
                    ${['created', 'paid', 'shipped', 'delivered', 'canceled'].map((status) => `
                        <option value="${status}" ${order.status === status ? 'selected' : ''}>${status}</option>
                    `).join('')}
                </select>
                <button class="btn primary" data-action="update">Actualizar estado</button>
            </div>
        `;
    }).join('');
}

async function loadOrders() {
    try {
        const data = await sgApi('/orders/admin');
        renderOrders(Array.isArray(data) ? data : []);
    } catch (err) {
        ordersList.innerHTML = `<div class="order-card">${err.message}</div>`;
    }
}

ordersList.addEventListener('click', async (e) => {
    const card = e.target.closest('[data-id]');
    if (!card) return;
    if (e.target.dataset.action !== 'update') return;

    const orderId = card.dataset.id;
    const status = card.querySelector('.status-select').value;
    try {
        await sgApi(`/orders/${orderId}/status`, { method: 'PUT', body: { status } });
        await loadOrders();
    } catch (err) {
        alert(err.message);
    }
});

refreshOrders.addEventListener('click', loadOrders);

function renderSessions(sessions) {
    if (!sessions.length) {
        chatSessions.innerHTML = '<div class="list-item">No hay sesiones activas.</div>';
        return;
    }

    chatSessions.innerHTML = sessions.map((session) => `
        <div class="list-item" data-session="${session}">
            <strong>${session}</strong>
            <div class="list-actions">
                <button class="btn ghost" data-action="open">Ver</button>
            </div>
        </div>
    `).join('');
}

function renderChatMessages(messages) {
    if (!messages.length) {
        chatMessages.innerHTML = '<div class="chat-bubble">Sin mensajes.</div>';
        return;
    }

    chatMessages.innerHTML = messages.map((msg) => `
        <div class="chat-bubble">
            <strong>${msg.sender}:</strong> ${msg.content}
        </div>
    `).join('');
}

async function loadSessions() {
    try {
        const data = await sgApi('/realtime/sessions');
        const sessions = Array.isArray(data.sessions) ? data.sessions : [];
        renderSessions(sessions);
    } catch (err) {
        chatSessions.innerHTML = `<div class="list-item">${err.message}</div>`;
    }
}

async function loadSessionMessages(sessionId) {
    try {
        const data = await sgApi(`/realtime/sessions/${sessionId}`);
        renderChatMessages(Array.isArray(data.messages) ? data.messages : []);
        activeSession = sessionId;
    } catch (err) {
        chatMessages.innerHTML = `<div class="chat-bubble">${err.message}</div>`;
    }
}

chatSessions.addEventListener('click', (e) => {
    const card = e.target.closest('[data-session]');
    if (!card) return;
    const sessionId = card.dataset.session;
    loadSessionMessages(sessionId);
});

refreshChat.addEventListener('click', () => {
    loadSessions();
    if (activeSession) loadSessionMessages(activeSession);
});

async function init() {
    const token = await sgGetToken();
    const user = sgGetUser();
    if (!token || !user || !['admin', 'operator'].includes(user.role)) {
        window.location.href = '../home/index.html';
        return;
    }

    document.getElementById('adminName').textContent = user.fullName || user.email;

    await loadProducts();
    await loadOrders();
    await loadSessions();
}

init();
