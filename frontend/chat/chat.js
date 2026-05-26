const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const chatStatus = document.getElementById('chatStatus');

const SESSION_KEY = 'sg_chat_session_id';

let sessionId = localStorage.getItem(SESSION_KEY);

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
    const ws = new WebSocket(url);

    ws.addEventListener('open', () => {
        chatStatus.textContent = 'Conectado';
    });

    ws.addEventListener('close', () => {
        chatStatus.textContent = 'Desconectado';
    });

    ws.addEventListener('message', (event) => {
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

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;
        ws.send(text);
        chatInput.value = '';
    });
}

connect();
