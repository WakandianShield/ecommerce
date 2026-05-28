const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const chatStatus = document.getElementById('chatStatus');
const faqQuick = document.querySelector('.faq-quick');

const SESSION_KEY = 'sg_chat_session_id';

let sessionId = localStorage.getItem(SESSION_KEY);
let socket = null;

function appendMessage(content, sender) {
    const bubble = document.createElement('div');
    bubble.className = `message ${sender}`;
    bubble.textContent = content;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function connect() {
    const wsBase = API_BASE.replace(/^http/, 'ws');
    const url = sessionId ? `${wsBase}/realtime/chat?session_id=${sessionId}` : `${wsBase}/realtime/chat`;
    socket = new WebSocket(url);

    socket.addEventListener('open', () => {
        chatStatus.textContent = 'Conectado';
    });

    socket.addEventListener('close', () => {
        chatStatus.textContent = 'Desconectado';
    });

    socket.addEventListener('message', (event) => {
        let payload = null;
        try { payload = JSON.parse(event.data); } catch { payload = null; }
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
    });
}

function sendMessage(text) {
    const message = text.trim();
    if (!message) return;
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        appendMessage('El chat aun se esta conectando. Intenta de nuevo en un momento.', 'assistant');
        return;
    }
    socket.send(message);
    chatInput.value = '';
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(chatInput.value);
});

if (faqQuick) {
    faqQuick.addEventListener('click', (event) => {
        const button = event.target.closest('[data-question]');
        if (!button) return;
        sendMessage(button.dataset.question || button.textContent);
    });
}

connect();
