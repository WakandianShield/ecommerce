const GRAPHQL_URL = "http://localhost:8000/graphql";
const STORAGE = { userId: "med_user_id", cartId: "med_cart_id" };
const SHIPPING_FEE = 490;

const QUERIES = {
	cart: `
		query Cart($id: ID!) {
			cart(id: $id) {
				id status
				items {
					id quantity unitPriceCents
					product { id name priceCents isPrescription }
				}
			}
		}
	`,
};

const MUTATIONS = {
	createUser: `
		mutation CreateUser($email: String!, $fullName: String!) {
			createUser(email: $email, fullName: $fullName) { id }
		}
	`,
	createCart: `
		mutation CreateCart($userId: ID!) {
			createCart(userId: $userId) { id }
		}
	`,
	setQty: `
		mutation SetQty($cartItemId: ID!, $quantity: Int!) {
			setCartItemQuantity(cartItemId: $cartItemId, quantity: $quantity) { id }
		}
	`,
	remove: `
		mutation RemoveFromCart($cartId: ID!, $productId: ID!) {
			removeFromCart(cartId: $cartId, productId: $productId) { id }
		}
	`,
};

const $ = (sel) => document.querySelector(sel);

let state = { cart: null, cartId: null };

function showToast(msg) {
	const el = $("#toast");
	el.textContent = msg;
	el.classList.add("is-visible");
	clearTimeout(showToast._t);
	showToast._t = setTimeout(() => el.classList.remove("is-visible"), 2600);
}

async function gql(query, variables = {}) {
	const res = await fetch(GRAPHQL_URL, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ query, variables }),
	});
	const json = await res.json();
	if (json.errors) throw new Error(json.errors.map((e) => e.message).join(" | "));
	return json.data;
}

function formatMoney(cents) {
	return `$${(cents / 100).toFixed(2)}`;
}

async function ensureUserAndCart() {
	let userId = localStorage.getItem(STORAGE.userId);
	if (!userId) {
		const data = await gql(MUTATIONS.createUser, {
			email: `invitado-${Date.now()}@farmaciaaurora.com`,
			fullName: "Invitado",
		});
		userId = data.createUser.id;
		localStorage.setItem(STORAGE.userId, userId);
	}
	let cartId = localStorage.getItem(STORAGE.cartId);
	if (!cartId) {
		const data = await gql(MUTATIONS.createCart, { userId });
		cartId = data.createCart.id;
		localStorage.setItem(STORAGE.cartId, cartId);
	}
	state.cartId = cartId;
}

async function loadCart() {
	const cartId = localStorage.getItem(STORAGE.cartId);
	if (!cartId) { renderEmpty(); return; }
	state.cartId = cartId;
	const data = await gql(QUERIES.cart, { id: cartId });
	if (!data.cart || data.cart.status !== "open") {
		localStorage.removeItem(STORAGE.cartId);
		await ensureUserAndCart();
		renderEmpty();
		return;
	}
	state.cart = data.cart;
	renderCart();
}

function renderEmpty() {
	$("#cartContent").innerHTML = `
		<div class="confirm-card text-center" style="animation:fadeUp .35s ease">
			<div class="confirm-icon" style="font-size:2.5rem">🛒</div>
			<h2 class="confirm-title">Tu carrito está vacío</h2>
			<p class="confirm-subtitle">Explora nuestro catálogo y agrega medicamentos.</p>
			<a href="../home/index.html" class="btn btn--primary mt-2">Ir al catálogo</a>
		</div>
	`;
}

function renderCart() {
	const items = state.cart?.items || [];
	if (!items.length) { renderEmpty(); return; }

	const subtotal = items.reduce((acc, i) => acc + i.unitPriceCents * i.quantity, 0);
	const total = subtotal + SHIPPING_FEE;

	const rowsHTML = items.map((item) => `
		<div class="cart-table-row" data-item-id="${item.id}" data-product-id="${item.product.id}" data-qty="${item.quantity}">
			<div>
				<p class="cart-product-name">
					${item.product.name}
					${item.product.isPrescription ? '<span class="badge badge--rx" style="margin-left:.3rem;font-size:.65rem">Rx</span>' : ""}
				</p>
				<p class="cart-product-sub">${formatMoney(item.unitPriceCents)} por unidad</p>
			</div>
			<span>${formatMoney(item.unitPriceCents)}</span>
			<div class="qty-control">
				<button class="qty-btn" data-action="dec">−</button>
				<span>${item.quantity}</span>
				<button class="qty-btn" data-action="inc">+</button>
			</div>
			<div style="display:flex;align-items:center;gap:.75rem">
				<strong style="color:var(--green)">${formatMoney(item.unitPriceCents * item.quantity)}</strong>
				<button class="remove-btn" data-action="remove" title="Quitar">✕</button>
			</div>
		</div>
	`).join("");

	$("#cartContent").innerHTML = `
		<div style="animation:fadeUp .35s ease">
			<div class="cart-table">
				<div class="cart-table-row cart-table-row--head">
					<span>Producto</span><span>Precio</span><span>Cantidad</span><span>Subtotal</span>
				</div>
				${rowsHTML}
			</div>

			<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;margin-top:1.5rem;flex-wrap:wrap">
				<a href="../home/index.html" class="btn btn--ghost">← Seguir comprando</a>
				<div class="cart-summary-box">
					<p class="eyebrow" style="margin-bottom:.75rem">Resumen del pedido</p>
					<div class="summary-row"><span>Subtotal</span><strong>${formatMoney(subtotal)}</strong></div>
					<div class="summary-row"><span>Envío</span><strong>${formatMoney(SHIPPING_FEE)}</strong></div>
					<div class="summary-row summary-row--total" style="margin-top:.5rem;padding-top:.5rem;border-top:1px solid var(--border)">
						<span>Total</span><strong>${formatMoney(total)}</strong>
					</div>
					<a href="../checkout/checkout.html" class="btn btn--primary btn--full" style="margin-top:1rem">
						Proceder al pago →
					</a>
					<p style="font-size:.72rem;color:var(--muted);text-align:center;margin-top:.5rem">
						Tarifa de envío fija: ${formatMoney(SHIPPING_FEE)}
					</p>
				</div>
			</div>
		</div>
	`;
}

async function handleItemAction(event) {
	const btn = event.target.closest("[data-action]");
	if (!btn) return;
	const row = btn.closest("[data-item-id]");
	if (!row) return;

	const itemId = row.dataset.itemId;
	const productId = row.dataset.productId;
	const qty = Number(row.dataset.qty);
	const action = btn.dataset.action;

	try {
		if (action === "inc") {
			await gql(MUTATIONS.setQty, { cartItemId: itemId, quantity: qty + 1 });
		} else if (action === "dec") {
			await gql(MUTATIONS.setQty, { cartItemId: itemId, quantity: qty - 1 });
		} else if (action === "remove") {
			await gql(MUTATIONS.remove, { cartId: state.cartId, productId });
		}
		await loadCart();
	} catch (err) {
		showToast(err.message);
	}
}

async function init() {
	try {
		await ensureUserAndCart();
		await loadCart();
	} catch (err) {
		showToast("Error al cargar el carrito: " + err.message);
	}
	document.querySelector("#cartContent").addEventListener("click", handleItemAction);
}

init();
