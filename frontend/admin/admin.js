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
let chatPollInterval = null;
let lastMessageCount = 0;
let chatSessionsSocket = null;
let activeChatSocket = null;
let chatMessageIds = new Set();

function startChatPolling(sessionId) {
    stopChatPolling();
    connectActiveChatSocket(sessionId);
}

function stopChatPolling() {
    if (chatPollInterval) {
        clearInterval(chatPollInterval);
        chatPollInterval = null;
    }
    if (activeChatSocket) {
        activeChatSocket.close();
        activeChatSocket = null;
    }
}

function formatMoney(cents) {
    const value = (Number(cents) || 0) / 100;
    return `$${value.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
}

const tabLoaders = {
    products: () => loadProducts(),
    orders:   () => loadOrders(),
    chat:     () => loadSessions(),
};

function setActiveTab(tab) {
    tabs.forEach((btn) => btn.classList.toggle('active', btn.dataset.tab === tab));
    sections.forEach((section) => section.classList.toggle('active', section.dataset.section === tab));
}

tabs.forEach((btn) => {
    btn.addEventListener('click', () => {
        if (btn.dataset.tab !== 'chat') stopChatPolling();
        setActiveTab(btn.dataset.tab);
        tabLoaders[btn.dataset.tab]?.();
    });
});

const adminReplyBtn = document.getElementById('adminReplyBtn');
const adminReplyInput = document.getElementById('adminReplyInput');

async function sendAdminReply() {
    const content = adminReplyInput.value.trim();
    if (!content || !activeSession) return;
    adminReplyBtn.disabled = true;
    try {
        const data = await sgApi(`/realtime/sessions/${activeSession}/reply`, {
            method: 'POST',
            body: { content },
        });
        adminReplyInput.value = '';
        if (data.message) appendChatMessage(data.message);
    } catch (err) {
        alert(err.message);
    } finally {
        adminReplyBtn.disabled = false;
    }
}

adminReplyBtn.addEventListener('click', sendAdminReply);

adminReplyInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        sendAdminReply();
    }
});

function clearImagePreview() {
    const preview = document.getElementById('imagePreview');
    const placeholder = document.getElementById('imagePlaceholder');
    preview.src = '';
    preview.hidden = true;
    placeholder.style.display = '';
}

function resetProductForm() {
    productForm.reset();
    document.getElementById('productId').value = '';
    document.getElementById('productActive').checked = true;
    document.getElementById('formTitle').textContent = 'Nuevo producto';
    clearImagePreview();
}

document.getElementById('productImage').addEventListener('change', (e) => {
    const file = e.target.files[0];
    const preview = document.getElementById('imagePreview');
    const placeholder = document.getElementById('imagePlaceholder');
    if (!file) { clearImagePreview(); return; }
    preview.src = URL.createObjectURL(file);
    preview.hidden = false;
    placeholder.style.display = 'none';
});

function fillProductForm(product) {
    document.getElementById('productId').value = product.id;
    document.getElementById('productName').value = product.name || '';
    document.getElementById('productDescription').value = product.description || '';
    document.getElementById('productCategory').value = product.category || '';
    document.getElementById('productPrice').value = ((Number(product.price_cents) || 0) / 100).toFixed(2);
    document.getElementById('productStock').value = Number(product.stock) || 0;
    document.getElementById('productActive').checked = Boolean(product.is_active);
    document.getElementById('formTitle').textContent = 'Editar producto';
    if (product.image_url) {
        const preview = document.getElementById('imagePreview');
        const placeholder = document.getElementById('imagePlaceholder');
        preview.src = product.image_url;
        preview.hidden = false;
        placeholder.style.display = 'none';
    }
}

function renderProducts() {
    if (!products.length) {
        productList.innerHTML = '<div class="list-item">No hay productos registrados.</div>';
        return;
    }

    productList.innerHTML = products.map((product) => {
        const thumb = product.image_url
            ? `<img class="list-thumb" src="${product.image_url}" alt="${product.name}">`
            : `<div class="list-thumb-placeholder" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg></div>`;
        const dotClass = product.is_active ? 'active' : 'inactive';
        return `
        <div class="list-item" data-id="${product.id}">
            <div class="list-item-inner">
                ${thumb}
                <div class="list-info">
                    <div style="display:flex;align-items:center;gap:6px">
                        <strong>${product.name}</strong>
                        <span class="status-dot ${dotClass}"></span>
                    </div>
                    <div style="margin-top:4px">
                        <span class="badge">${product.category || 'Sin categoria'}</span>
                    </div>
                    <div style="font-size:0.78rem;color:var(--muted);margin-top:5px">
                        ${formatMoney(product.price_cents)} &nbsp;·&nbsp; Stock: ${product.stock}
                    </div>
                </div>
            </div>
            <div class="list-actions">
                <button class="btn ghost sm" data-action="edit">Editar</button>
                <button class="btn danger sm" data-action="delete">Eliminar</button>
            </div>
        </div>`;
    }).join('');
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

const statusLabels = { created: 'Creada', paid: 'Pagada', shipped: 'Enviada', delivered: 'Entregada', canceled: 'Cancelada' };

function renderOrders(orders) {
    if (!orders.length) {
        ordersList.innerHTML = '<div class="order-card" style="grid-column:1/-1;text-align:center;color:var(--muted)">No hay ordenes.</div>';
        return;
    }

    ordersList.innerHTML = orders.map((order) => {
        const pills = order.items.map((item) =>
            `<span class="order-item-pill">${item.name} ×${item.quantity}</span>`
        ).join('');
        const statusClass = order.status || 'created';
        const statusOptions = ['created', 'paid', 'shipped', 'delivered', 'canceled'].map((s) =>
            `<option value="${s}" ${order.status === s ? 'selected' : ''}>${statusLabels[s] || s}</option>`
        ).join('');
        return `
        <div class="order-card" data-id="${order.id}">
            <div class="order-card-head">
                <span class="order-id">#${order.id.slice(0, 8).toUpperCase()}</span>
                <span class="order-total">${formatMoney(order.total_cents)}</span>
            </div>
            <div class="order-items">${pills}</div>
            <div class="order-footer">
                <span class="status-badge ${statusClass}">${statusLabels[statusClass] || statusClass}</span>
                <select class="status-select">${statusOptions}</select>
                <button class="btn primary sm" data-action="update">Guardar</button>
            </div>
        </div>`;
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
    const emptyState = document.getElementById('chatEmptyState');
    if (!sessions.length) {
        chatSessions.innerHTML = '<p style="font-size:0.8rem;color:var(--muted);padding:8px">Sin sesiones activas.</p>';
        return;
    }
    chatSessions.innerHTML = sessions.map((session) => `
        <div class="session-item ${session === activeSession ? 'active' : ''}" data-session="${session}">
            <span class="session-dot"></span>
            <span class="session-name">${session}</span>
        </div>
    `).join('');
}

function appendChatMessage(msg) {
    if (!msg || chatMessageIds.has(msg.id)) return;
    chatMessageIds.add(msg.id);
    const isUser = msg.sender === 'customer';
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${isUser ? 'user-msg' : 'admin-msg'}`;

    const text = document.createElement('p');
    text.className = 'bubble-text';
    text.textContent = msg.content;

    bubble.appendChild(text);
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderChatMessages(messages) {
    const emptyState = document.getElementById('chatEmptyState');
    if (emptyState) emptyState.style.display = 'none';
    chatMessageIds = new Set();
    chatMessages.innerHTML = '';
    if (!messages.length) {
        chatMessages.innerHTML = '<p style="font-size:0.8rem;color:var(--muted);padding:8px">Sin mensajes en esta sesion.</p>';
        return;
    }
    messages.forEach(appendChatMessage);
}

async function connectSessionsSocket() {
    const token = await sgGetToken();
    if (!token || chatSessionsSocket) return;
    const wsBase = API_BASE.replace(/^http/, 'ws');
    chatSessionsSocket = new WebSocket(`${wsBase}/realtime/admin/sessions?token=${encodeURIComponent(token)}`);
    chatSessionsSocket.addEventListener('message', (event) => {
        let payload = null;
        try { payload = JSON.parse(event.data); } catch { return; }
        if (payload.type === 'sessions' && Array.isArray(payload.sessions)) {
            renderSessions(payload.sessions);
        }
    });
    chatSessionsSocket.addEventListener('close', () => {
        chatSessionsSocket = null;
    });
}

async function connectActiveChatSocket(sessionId) {
    const token = await sgGetToken();
    if (!token) return;
    if (activeChatSocket) activeChatSocket.close();
    const wsBase = API_BASE.replace(/^http/, 'ws');
    const socket = new WebSocket(`${wsBase}/realtime/admin/chat?session_id=${encodeURIComponent(sessionId)}&token=${encodeURIComponent(token)}`);
    activeChatSocket = socket;
    socket.addEventListener('message', (event) => {
        let payload = null;
        try { payload = JSON.parse(event.data); } catch { return; }
        if (payload.type === 'history' && Array.isArray(payload.messages)) {
            lastMessageCount = payload.messages.length;
            renderChatMessages(payload.messages);
        }
        if (payload.type === 'message' && payload.message) {
            lastMessageCount += 1;
            appendChatMessage(payload.message);
        }
    });
    socket.addEventListener('close', () => {
        if (activeChatSocket === socket && activeSession === sessionId) activeChatSocket = null;
    });
}

async function loadSessions() {
    try {
        connectSessionsSocket();
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
        const messages = Array.isArray(data.messages) ? data.messages : [];
        renderChatMessages(messages);
        lastMessageCount = messages.length;
        activeSession = sessionId;
        document.getElementById('chatReply').hidden = false;
        startChatPolling(sessionId);
    } catch (err) {
        chatMessages.innerHTML = `<div class="chat-bubble">${err.message}</div>`;
    }
}

chatSessions.addEventListener('click', (e) => {
    const card = e.target.closest('[data-session]');
    if (!card) return;
    document.querySelectorAll('.session-item').forEach((s) => s.classList.remove('active'));
    card.classList.add('active');
    const sessionId = card.dataset.session;
    const label = document.getElementById('activeChatLabel');
    if (label) label.textContent = sessionId;
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

    const nameEl = document.getElementById('adminName');
    if (nameEl) nameEl.textContent = user.fullName || user.email;

    await loadProducts();
    await loadOrders();
    await loadSessions();
    await connectSessionsSocket();
}

init();
