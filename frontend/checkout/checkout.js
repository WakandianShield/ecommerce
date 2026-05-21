document.addEventListener('DOMContentLoaded', () => {
    const stateSelect = document.getElementById('state');
    const citySelect = document.getElementById('city');
    const cardNumber = document.getElementById('card-number');
    const expiry = document.getElementById('expiry');
    const orderItems = document.getElementById('orderItems');
    const orderTotal = document.getElementById('orderTotal');

    const formatMoney = (value) => {
        const amount = Number(value) || 0;
        return `$${amount.toLocaleString('es-ES')}`;
    };

    const renderSummary = () => {
        if (!orderItems || !orderTotal) return;
        const stored = localStorage.getItem('sg_cart_summary');
        if (!stored) {
            orderItems.innerHTML = '<p class="order-empty">No se encontraron productos del carrito.</p>';
            orderTotal.textContent = formatMoney(0);
            return;
        }

        try {
            const data = JSON.parse(stored);
            const items = Array.isArray(data.items) ? data.items : [];
            if (!items.length) {
                orderItems.innerHTML = '<p class="order-empty">No se encontraron productos del carrito.</p>';
                orderTotal.textContent = formatMoney(0);
                return;
            }

            orderItems.innerHTML = items.map((item) => {
                const qty = Number(item.qty) || 1;
                const price = Number(item.price) || 0;
                const lineTotal = price * qty;
                return `
                    <div class="order-item">
                        <span>
                            ${item.name || 'Producto'}
                            <span class="order-qty">x${qty}</span>
                        </span>
                        <strong>${formatMoney(lineTotal)}</strong>
                    </div>
                `;
            }).join('');

            const total = items.reduce((sum, item) => {
                const qty = Number(item.qty) || 1;
                const price = Number(item.price) || 0;
                return sum + price * qty;
            }, 0);

            orderTotal.textContent = formatMoney(total);
        } catch (error) {
            orderItems.innerHTML = '<p class="order-empty">No se encontraron productos del carrito.</p>';
            orderTotal.textContent = formatMoney(0);
        }
    };

    const mexicoData = {
        "Jalisco": ["Guadalajara", "Zapopan", "Tlaquepaque", "Puerto Vallarta"],
        "CDMX": ["Coyoacán", "Benito Juárez", "Miguel Hidalgo", "Cuauhtémoc"],
        "Nuevo León": ["Monterrey", "San Pedro", "Santa Catarina", "Guadalupe"]
    };

    stateSelect.addEventListener('change', (e) => {
        const cities = mexicoData[e.target.value] || [];
        citySelect.innerHTML = '<option value="" disabled selected>Ciudad</option>';
        cities.forEach(city => {
            const opt = document.createElement('option');
            opt.value = city;
            opt.textContent = city;
            citySelect.appendChild(opt);
        });
        citySelect.disabled = false;
    });

    cardNumber.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        e.target.value = value.replace(/(\d{4})(?=\d)/g, '$1 ').trim();
    });

    expiry.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 2) {
            e.target.value = value.slice(0, 2) + '/' + value.slice(2, 4);
        } else {
            e.target.value = value;
        }
    });

    renderSummary();

    document.getElementById('checkout-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = document.getElementById('submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Procesando…';

        try {
            if (typeof sgGetToken === 'function' && sgGetToken()) {
                const stored = localStorage.getItem('sg_cart_summary');
                if (stored) {
                    const data = JSON.parse(stored);
                    const items = Array.isArray(data.items) ? data.items : [];
                    const total = Number(data.total) || 0;

                    const address  = document.getElementById('address').value.trim();
                    const state    = document.getElementById('state').value;
                    const city     = document.getElementById('city').value;
                    const shipping = `${address}, ${city}, ${state}`;

                    const CREATE_ORDER = `
                        mutation CreateOrder($items: [OrderItemInput!]!, $shippingAddress: String!, $totalCents: Int!) {
                            createOrderFromItems(items: $items, shippingAddress: $shippingAddress, totalCents: $totalCents) {
                                id
                                status
                                totalCents
                            }
                        }
                    `;

                    await sgGql(CREATE_ORDER, {
                        items: items.map(i => ({
                            name:       i.name,
                            priceCents: Math.round(Number(i.price) * 100),
                            quantity:   Number(i.qty) || 1,
                        })),
                        shippingAddress: shipping,
                        totalCents:      Math.round(total * 100),
                    });
                }
            }
        } catch (err) {
            console.error('Error al guardar la orden:', err);
        }

        localStorage.removeItem('sg_cart_items');
        localStorage.removeItem('sg_cart_summary');
        window.location.href = '../result/success.html';
    });
});