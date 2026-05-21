const SG_API = 'http://localhost:8000/graphql';
const TOKEN_KEY = 'sg_auth_token';
const USER_KEY  = 'sg_auth_user';
const EXP_KEY   = 'sg_auth_exp';


function sgGetToken() {
    const exp = localStorage.getItem(EXP_KEY);
    if (exp && Date.now() > Number(exp)) {
        sgClearAuth();
        return null;
    }
    return localStorage.getItem(TOKEN_KEY);
}

function sgGetUser() {
    if (!sgGetToken()) return null;
    try { return JSON.parse(localStorage.getItem(USER_KEY)); }
    catch { return null; }
}

function sgSetAuth(token, user) {
    const expMs = Date.now() + 14 * 24 * 60 * 60 * 1000;
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY,  JSON.stringify(user));
    localStorage.setItem(EXP_KEY,   String(expMs));
}

function sgClearAuth() {
    [TOKEN_KEY, USER_KEY, EXP_KEY].forEach(k => localStorage.removeItem(k));
}

async function sgGql(query, variables = {}) {
    const token = sgGetToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(SG_API, {
        method: 'POST',
        headers,
        body: JSON.stringify({ query, variables }),
    });
    const json = await res.json();
    if (json.errors?.length) throw new Error(json.errors.map(e => e.message).join(' | '));
    return json.data;
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
    dd.innerHTML = `
        <div class="sg-dropdown__header">
            <p class="sg-dropdown__name">${user.fullName}</p>
            <p class="sg-dropdown__email">${user.email}</p>
        </div>
        <button class="sg-dropdown__btn sg-dropdown__btn--danger" id="sg-logout">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
            Cerrar sesión
        </button>
    `;
    wrapper.appendChild(dd);

    dd.querySelector('#sg-logout').addEventListener('click', () => {
        sgClearAuth();
        window.location.reload();
    });

    setTimeout(() => {
        document.addEventListener('click', function handler(e) {
            if (!wrapper.contains(e.target)) { dd.remove(); document.removeEventListener('click', handler); }
        });
    }, 0);
}

function sgInitDropdown() {
    const user = sgGetUser();
    if (!user) return;

    _injectDropdownCSS();

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

document.addEventListener('DOMContentLoaded', sgInitDropdown);
