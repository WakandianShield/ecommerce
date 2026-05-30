const API_BASE = 'https://ecommerce-production-5088.up.railway.app';
const ACCESS_KEY = 'sg_access_token';
const REFRESH_KEY = 'sg_refresh_token';
const USER_KEY = 'sg_auth_user';
const EXP_KEY = 'sg_access_exp';

function _decodeBase64Url(input) {
    const normalized = input.replace(/-/g, '+').replace(/_/g, '/');
    const pad = normalized.length % 4 === 0 ? '' : '='.repeat(4 - (normalized.length % 4));
    return atob(normalized + pad);
}

function sgDecodeToken(token) {
    if (!token) return null;
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    try {
        return JSON.parse(_decodeBase64Url(parts[1]));
    } catch {
        return null;
    }
}


function sgIsAccessExpired() {
    const exp = localStorage.getItem(EXP_KEY);
    if (!exp) return false;
    return Date.now() > Number(exp);
}

async function sgRefreshAccessToken() {
    const refreshToken = localStorage.getItem(REFRESH_KEY);
    if (!refreshToken) {
        sgClearAuth();
        return null;
    }

    try {
        const res = await fetch(`${API_BASE}/sessions/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (!res.ok) {
            sgClearAuth();
            return null;
        }
        const data = await res.json();
        if (!data.access_token || !data.refresh_token) {
            sgClearAuth();
            return null;
        }
        sgSetAuth(data.access_token, data.refresh_token, data.profile);
        return data.access_token;
    } catch {
        sgClearAuth();
        return null;
    }
}

async function sgGetToken() {
    const token = localStorage.getItem(ACCESS_KEY);
    if (!token) return null;
    if (!sgIsAccessExpired()) return token;
    return await sgRefreshAccessToken();
}

function sgGetUser() {
    const token = localStorage.getItem(ACCESS_KEY);
    if (!token || sgIsAccessExpired()) return null;
    try { return JSON.parse(localStorage.getItem(USER_KEY)); }
    catch { return null; }
}

function sgSetAuth(accessToken, refreshToken, user) {
    const decoded = sgDecodeToken(accessToken);
    const expMs = decoded?.exp ? decoded.exp * 1000 : Date.now() + 60 * 60 * 1000;
    const normalized = { ...user };
    if (normalized.full_name && !normalized.fullName) {
        normalized.fullName = normalized.full_name;
    }
    localStorage.setItem(ACCESS_KEY, accessToken);
    localStorage.setItem(REFRESH_KEY, refreshToken || '');
    localStorage.setItem(USER_KEY, JSON.stringify(normalized));
    localStorage.setItem(EXP_KEY, String(expMs));
}

function sgClearAuth() {
    [ACCESS_KEY, REFRESH_KEY, USER_KEY, EXP_KEY, 'sg_chat_session_id', 'sg_auth_token', 'sg_auth_exp']
        .forEach(k => localStorage.removeItem(k));
}

async function sgLogout() {
    const refreshToken = localStorage.getItem(REFRESH_KEY);
    sgClearAuth();
    if (!refreshToken) return;
    try {
        await fetch(`${API_BASE}/sessions/logout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
    } catch {
        return;
    }
}

async function sgApi(path, { method = 'GET', body, headers = {} } = {}) {
    let token = await sgGetToken();
    const reqHeaders = { 'Content-Type': 'application/json', ...headers };
    if (token) reqHeaders['Authorization'] = `Bearer ${token}`;

    let res = await fetch(`${API_BASE}${path}`, {
        method,
        headers: reqHeaders,
        body: body ? JSON.stringify(body) : undefined,
    });

    if (res.status === 401) {
        token = await sgRefreshAccessToken();
        if (token) {
            reqHeaders['Authorization'] = `Bearer ${token}`;
            res = await fetch(`${API_BASE}${path}`, {
                method,
                headers: reqHeaders,
                body: body ? JSON.stringify(body) : undefined,
            });
        }
    }

    let data = {};
    try { data = await res.json(); } catch { data = {}; }
    if (!res.ok) {
        const detail = data.detail || 'Error al conectar con el servidor.';
        throw new Error(detail);
    }
    return data;
}

function _injectDropdownCSS() {
    if (document.getElementById('sg-dropdown-style')) return;
    const s = document.createElement('style');
    s.id = 'sg-dropdown-style';
    s.textContent = `
        .sg-profile-wrap { position: relative; display: inline-flex; }
        .sg-dropdown {
            position: absolute;
            top: calc(100% + 14px);
            right: 0;
            min-width: 210px;
            background: rgba(8, 10, 18, 0.96);
            backdrop-filter: blur(24px) saturate(160%);
            -webkit-backdrop-filter: blur(24px) saturate(160%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 6px;
            box-shadow: 0 24px 60px rgba(0,0,0,0.6);
            z-index: 4000;
            animation: sgDropIn .2s cubic-bezier(.16,1,.3,1);
        }
        @keyframes sgDropIn {
            from { opacity:0; transform:translateY(-8px) scale(.97); }
            to   { opacity:1; transform:translateY(0)    scale(1);   }
        }
        .sg-dropdown__header {
            padding: 12px 14px 10px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            margin-bottom: 4px;
        }
        .sg-dropdown__name  { font-size:.88rem; font-weight:700; color:#fff; margin:0 0 2px; }
        .sg-dropdown__email { font-size:.74rem; color:rgba(255,255,255,.4); margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:182px; }
        .sg-dropdown__btn {
            display: flex; align-items:center; gap:9px;
            width:100%; padding:10px 14px;
            background:transparent; border:none; border-radius:12px;
            color:rgba(255,255,255,.75); font-size:.84rem; font-weight:600;
            cursor:pointer; transition:.15s; text-align:left; font-family:inherit;
        }
        .sg-dropdown__btn:hover { background:rgba(255,255,255,.06); color:#fff; }
        .sg-dropdown__btn--danger:hover { background:rgba(255,70,70,.12); color:#ff6b6b; }
    `;
    document.head.appendChild(s);
}

function _buildDropdown(wrapper, user) {
    const existing = wrapper.querySelector('.sg-dropdown');
    if (existing) { existing.remove(); return; }

    _injectDropdownCSS();

    const dd = document.createElement('div');
    dd.className = 'sg-dropdown';
    const isAdmin = user.role === 'admin' || user.role === 'operator';
    dd.innerHTML = `
        <div class="sg-dropdown__header">
            <p class="sg-dropdown__name">${user.fullName}</p>
            <p class="sg-dropdown__email">${user.email}</p>
        </div>
        <a class="sg-dropdown__btn" href="../orders/orders.html">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 6h11"></path><path d="M9 12h11"></path><path d="M9 18h11"></path><circle cx="4" cy="6" r="1"></circle><circle cx="4" cy="12" r="1"></circle><circle cx="4" cy="18" r="1"></circle></svg>
            Mis compras
        </a>
        ${isAdmin ? `
        <a class="sg-dropdown__btn" href="../admin/admin.html">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 4v5c0 5-3.5 8-7 9-3.5-1-7-4-7-9V7l7-4z"></path></svg>
            Panel admin
        </a>
        ` : ''}
        <button class="sg-dropdown__btn sg-dropdown__btn--danger" id="sg-logout">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
            Cerrar sesión
        </button>
    `;
    wrapper.appendChild(dd);

    dd.querySelector('#sg-logout').addEventListener('click', async () => {
        await sgLogout();
        window.location.reload();
    });

    setTimeout(() => {
        document.addEventListener('click', function handler(e) {
            if (!wrapper.contains(e.target)) { dd.remove(); document.removeEventListener('click', handler); }
        });
    }, 0);
}

function sgInjectAdminNav(user) {
    if (!user || (user.role !== 'admin' && user.role !== 'operator')) return;
    const navLinks = document.querySelector('.nav-links');
    if (!navLinks) return;
    if (navLinks.querySelector('[aria-label="Admin"]')) return;

    const a = document.createElement('a');
    a.href = '../admin/admin.html';
    a.className = 'nav-icon';
    a.setAttribute('aria-label', 'Admin');
    a.title = 'Panel admin';
    a.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 4v5c0 5-3.5 8-7 9-3.5-1-7-4-7-9V7l7-4z"></path></svg>`;

    const profileLink = navLinks.querySelector('[aria-label="Perfil"]');
    if (profileLink) {
        navLinks.insertBefore(a, profileLink);
    } else {
        navLinks.appendChild(a);
    }
}

async function sgInitDropdown() {
    const token = await sgGetToken();
    if (!token) return;
    const user = sgGetUser();
    if (!user) return;

    _injectDropdownCSS();
    sgInjectAdminNav(user);

    const profileLink = document.querySelector('a[aria-label="Perfil"]');
    if (!profileLink) return;

    const wrap = document.createElement('div');
    wrap.className = 'sg-profile-wrap';
    profileLink.parentNode.insertBefore(wrap, profileLink);
    wrap.appendChild(profileLink);

    profileLink.addEventListener('click', e => {
        e.preventDefault();
        _buildDropdown(wrap, user);
    });
}

document.addEventListener('DOMContentLoaded', () => { sgInitDropdown(); });
