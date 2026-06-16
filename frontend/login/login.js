document.addEventListener('DOMContentLoaded', async () => {
    if (typeof sgGetToken === 'function') {
        const token = await sgGetToken();
        if (token) {
            window.location.replace('../home/index.html');
            return;
        }
    }

    const btnLogin  = document.getElementById('btn-login');
    const btnSignup = document.getElementById('btn-signup');
    const nameGroup = document.getElementById('name-group');
    const nameInput = document.getElementById('full-name');
    const emailInput= document.getElementById('email');
    const passInput = document.getElementById('password');
    const submitBtn = document.getElementById('submit-btn');
    const errBox    = document.getElementById('auth-error');
    const titleEl   = document.getElementById('main-title');
    const descEl    = document.getElementById('main-desc');

    let mode = 'login';

    function setMode(m) {
        mode = m;
        if (m === 'signup') {
            btnSignup.classList.add('tab-active');
            btnLogin.classList.remove('tab-active');
            titleEl.textContent  = 'Bienvenido';
            descEl.textContent   = 'Crea tu cuenta';
            submitBtn.textContent = 'Crear Cuenta';
            nameGroup.style.display = '';
            nameInput.required = true;
        } else {
            btnLogin.classList.add('tab-active');
            btnSignup.classList.remove('tab-active');
            titleEl.textContent  = 'Bienvenido';
            descEl.textContent   = 'Ingresa a tu zona de confort';
            submitBtn.textContent = 'Iniciar Sesión';
            nameGroup.style.display = 'none';
            nameInput.required = false;
        }
        hideError();
    }

    function showError(type, msg) {
        errBox.innerHTML = `
            <strong style="display: block; font-size: 0.75rem; text-transform: uppercase; color: #dc2626; margin-bottom: 2px;">Error de ${type}</strong>
            <span style="font-size: 0.9rem; color: #4b5563;">${msg}</span>
        `;
        errBox.style.display = '';
    }

    function hideError() {
        errBox.style.display = 'none';
        errBox.textContent = '';
    }

    function setLoading(on) {
        submitBtn.disabled = on;
        submitBtn.textContent = on
            ? 'Cargando…'
            : (mode === 'signup' ? 'Crear Cuenta' : 'Iniciar Sesión');
    }

    btnLogin.addEventListener('click',  () => setMode('login'));
    btnSignup.addEventListener('click', () => setMode('signup'));

    const LOGIN_ENDPOINT = '/sessions';
    const REGISTER_ENDPOINT = '/profiles';

    document.getElementById('auth-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();

        const email    = emailInput.value.trim();
        const password = passInput.value;
        const fullName = nameInput.value.trim();

        if (!email || !password) {
            showError('Entrada', 'El correo y la contraseña son obligatorios.');
            return;
        }

        if (password.length < 6) {
            showError('Validación', 'La contraseña es demasiado corta (mínimo 6 caracteres).');
            return;
        }

        if (mode === 'signup' && !fullName) {
            showError('Validación', 'Debes ingresar tu nombre completo para registrarte.');
            return;
        }

        setLoading(true);
        try {
            let data;
            if (mode === 'login') {
                data = await sgApi(LOGIN_ENDPOINT, { method: 'POST', body: { email, password } });
            } else {
                data = await sgApi(REGISTER_ENDPOINT, { method: 'POST', body: { email, password, full_name: fullName } });
            }
            const { access_token, refresh_token, profile } = data;
            sgSetAuth(access_token, refresh_token, profile);
            window.location.replace('../home/index.html');
        } catch (err) {
            const msg = err.message || '';
            let type = 'Servidor';

            if (msg.includes('401') || msg.toLowerCase().includes('invalid')) type = 'Credenciales';
            else if (msg.includes('409') || msg.toLowerCase().includes('exists')) type = 'Registro';
            else if (msg.toLowerCase().includes('fetch') || msg.toLowerCase().includes('network')) type = 'Conexión';
            else if (msg.toLowerCase().includes('password') || msg.toLowerCase().includes('email')) type = 'Validación';

            showError(type, msg || 'Ocurrió un problema al procesar tu solicitud.');
        } finally {
            setLoading(false);
        }
    });
});
