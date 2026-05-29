const chatMessages = document.getElementById('chatMessages');
const chatForm     = document.getElementById('chatForm');
const chatInput    = document.getElementById('chatInput');
const chatStatus   = document.getElementById('chatStatus');
const faqQuick     = document.querySelector('.faq-quick');

const SESSION_KEY = 'sg_chat_session_id';

let sessionId   = localStorage.getItem(SESSION_KEY);
let socket      = null;
let reconnectTimer = null;
let reconnectDelay = 2000;

/* ── Append a message bubble ── */
function appendMessage(content, sender) {
    removeTyping();

    const wrap = document.createElement('div');
    wrap.className = `message-wrap ${sender}`;

    if (sender === 'assistant') {
        const avatar = document.createElement('div');
        avatar.className = 'msg-avatar';
        avatar.textContent = '🎵';
        wrap.appendChild(avatar);
    }

    const bubble = document.createElement('div');
    bubble.className = `message ${sender}`;
    bubble.textContent = content;
    wrap.appendChild(bubble);

    chatMessages.appendChild(wrap);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/* ── Typing indicator ── */
function showTyping() {
    if (document.getElementById('typingIndicator')) return;
    const wrap = document.createElement('div');
    wrap.className = 'typing-indicator';
    wrap.id = 'typingIndicator';

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = '🎵';

    const dots = document.createElement('div');
    dots.className = 'typing-dots';
    dots.innerHTML = '<span></span><span></span><span></span>';

    wrap.appendChild(avatar);
    wrap.appendChild(dots);
    chatMessages.appendChild(wrap);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTyping() {
    document.getElementById('typingIndicator')?.remove();
}

/* ── Status helpers ── */
function setStatus(text, connected = false) {
    chatStatus.textContent = text;
    chatStatus.className = 'status' + (connected ? ' connected' : '');
}

/* ── WebSocket ── */
function connect() {
    clearTimeout(reconnectTimer);
    setStatus('Conectando…');

    const wsBase = API_BASE.replace(/^http/, 'ws');
    const url = sessionId
        ? `${wsBase}/realtime/chat?session_id=${sessionId}`
        : `${wsBase}/realtime/chat`;

    socket = new WebSocket(url);

    socket.addEventListener('open', () => {
        setStatus('Conectado', true);
        reconnectDelay = 2000;
    });

    socket.addEventListener('close', () => {
        setStatus('Reconectando…');
        reconnectTimer = setTimeout(connect, reconnectDelay);
        reconnectDelay = Math.min(reconnectDelay * 1.5, 15000);
    });

    socket.addEventListener('error', () => {
        socket.close();
    });

    socket.addEventListener('message', (event) => {
        let payload = null;
        try { payload = JSON.parse(event.data); } catch { return; }
        if (!payload) return;

        if (payload.type === 'session') {
            sessionId = payload.session_id;
            localStorage.setItem(SESSION_KEY, sessionId);
            return;
        }

        if (payload.type === 'message' && payload.message) {
            const sender = payload.message.sender === 'assistant' ? 'assistant' : 'user';
            appendMessage(payload.message.content, sender);
        }

        if (payload.type === 'error') {
            removeTyping();
        }
    });
}

/* ── Send ── */
function sendMessage(text) {
    const message = text.trim();
    if (!message) return;
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        appendMessage('Conectando… intenta de nuevo en un momento.', 'assistant');
        return;
    }
    socket.send(message);
    chatInput.value = '';
    showTyping();
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(chatInput.value);
});

if (faqQuick) {
    faqQuick.addEventListener('click', (event) => {
        const button = event.target.closest('[data-question]');
        if (!button) return;
        sendMessage(button.dataset.question || button.textContent.trim());
    });
}

connect();
