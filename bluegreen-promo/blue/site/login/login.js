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

    function showError(msg) {
        errBox.textContent = msg;
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

        if (!email || !password) return;
        if (mode === 'signup' && !fullName) {
            showError('Por favor ingresa tu nombre completo.');
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
            showError(err.message || 'Error al conectar con el servidor.');
        } finally {
            setLoading(false);
        }
    });
});
