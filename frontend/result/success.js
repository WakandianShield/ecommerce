document.addEventListener('DOMContentLoaded', () => {
    const currentStatus = 'success'; 

    const iconWrapper = document.getElementById('icon-wrapper');
    const title = document.getElementById('status-title');
    const message = document.getElementById('status-message');
    const btnMain = document.getElementById('btn-primary');
    const btnSecondary = document.getElementById('btn-secondary');

    if (currentStatus === 'success') {
        iconWrapper.innerHTML = `<svg width="45" height="45" viewBox="0 0 24 24" fill="none" stroke="#3dd6c1" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
        iconWrapper.style.boxShadow = "0 0 40px rgba(61, 214, 193, 0.25)";
        
        title.textContent = "COMPRA EXITOSA";
        title.style.color = "var(--success)";
        message.textContent = "Tu pedido ha sido confirmado. En breve recibirás los detalles en tu correo electrónico.";
        
        btnMain.style.background = "linear-gradient(135deg, #3dd6c1, #2cb19f)";
        btnMain.style.color = "#05060a";
        btnSecondary.textContent = "Descargar Ticket";

    } else {
        iconWrapper.innerHTML = `<svg width="45" height="45" viewBox="0 0 24 24" fill="none" stroke="#ff4b5c" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
        iconWrapper.style.boxShadow = "0 0 40px rgba(255, 75, 92, 0.25)";
        
        title.textContent = "COMPRA RECHAZADA";
        title.style.color = "var(--error)";
        message.textContent = "Lo sentimos, el pago no pudo procesarse. Por favor, intenta con otro método de pago.";
        
        btnMain.style.background = "linear-gradient(135deg, #ff4b5c, #d43d4c)";
        btnMain.style.color = "white";
        btnMain.textContent = "Reintentar Pago";
        btnMain.href = "../cart/carrito.html";
        btnSecondary.textContent = "Contactar Soporte";
    }

    const now = new Date();
    document.getElementById('current-date').textContent = now.toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' });
});