const ordersList = document.getElementById('ordersList');

function formatMoney(cents) {
    const value = (Number(cents) || 0) / 100;
    return `$${value.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
}

function renderOrders(orders) {
    if (!orders.length) {
        ordersList.innerHTML = '<div class="state-card">Aun no tienes ordenes registradas.</div>';
        return;
    }

    ordersList.innerHTML = orders.map((order) => {
        const itemsHtml = order.items.map((item) => `
            <div class="order-item">
                <span>${item.name} x${item.quantity}</span>
                <span>${formatMoney(item.unit_price_cents * item.quantity)}</span>
            </div>
        `).join('');
        return `
            <article class="order-card">
                <div class="order-top">
                    <div>
                        <h3>Orden #${order.id.slice(0, 8)}</h3>
                        <div class="order-status">${order.status}</div>
                    </div>
                    <div>
                        <p>Envio: ${order.shipping_address}</p>
                    </div>
                </div>
                <div class="order-items">${itemsHtml}</div>
                <div class="order-total">Total: ${formatMoney(order.total_cents)}</div>
            </article>
        `;
    }).join('');
}

async function loadOrders() {
    const token = await sgGetToken();
    if (!token) {
        window.location.href = '../login/login.html';
        return;
    }

    try {
        const orders = await sgApi('/orders');
        renderOrders(Array.isArray(orders) ? orders : []);
    } catch (err) {
        ordersList.innerHTML = `<div class="state-card">${err.message}</div>`;
    }
}

loadOrders();
