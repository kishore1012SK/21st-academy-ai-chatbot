// =============================================
//  21ST ACADEMY — CAREER MAPPING WORKSHOP
//  chatbot.js — talks ONLY to our own self-hosted
//  backend (FastAPI -> local Ollama/Llama3).
//  No third-party AI provider is ever contacted.
// =============================================

// --- Config -----------------------------------------------------
// In production, nginx proxies /api/* to the backend on the SAME
// origin as this site, so the default below just works once deployed
// behind the provided nginx config. Override for local dev if your
// backend runs on a different host/port.
const CHATBOT_CONFIG = {
  API_BASE_URL: "https://twolst-academy-ai-chatbot-3.onrender.com/api",
  USE_STREAMING: true,
};

// --- DOM refs -----------------------------------------------------
const chatbotToggle = document.getElementById('chatbotToggle');
const chatbotWindow = document.getElementById('chatbotWindow');
const chatbotCloseBtn = document.getElementById('chatbotCloseBtn');
const chatbotClearBtn = document.getElementById('chatbotClearBtn');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSend = document.getElementById('chatSend');
const chatIcon = document.querySelector('.chat-icon');
const chatClose = document.querySelector('.chat-close');
const botStatus = document.getElementById('botStatus');

let isOpen = false;

// --- Session identity (anonymous, local only) ----------------------
// Lets our backend keep per-visitor conversation memory without any
// login. Nothing here ever leaves our own domain.
function getSessionId() {
  let sid = localStorage.getItem('academy_chat_session_id');
  if (!sid) {
    sid = 'sess_' + crypto.randomUUID();
    localStorage.setItem('academy_chat_session_id', sid);
  }
  return sid;
}
const sessionId = getSessionId();

// Set the first bot bubble's timestamp on load
document.addEventListener('DOMContentLoaded', () => {
  const firstTs = chatMessages.querySelector('.chat-timestamp');
  if (firstTs) firstTs.textContent = formatTime(new Date());
});

// --- Toggle chatbot -------------------------------------------------
function toggleChatbot() {
  isOpen = !isOpen;
  chatbotWindow.classList.toggle('hidden', !isOpen);
  chatIcon.classList.toggle('hidden', isOpen);
  chatClose.classList.toggle('hidden', !isOpen);
  if (isOpen) chatInput.focus();
}
chatbotToggle.addEventListener('click', toggleChatbot);
chatbotCloseBtn.addEventListener('click', toggleChatbot);

// --- Clear chat -------------------------------------------------
chatbotClearBtn.addEventListener('click', async () => {
  if (!confirm('Clear this conversation?')) return;
  try {
    await fetch(`${CHATBOT_CONFIG.API_BASE_URL}/history?session_id=${encodeURIComponent(sessionId)}`, {
      method: 'DELETE',
    });
  } catch (err) {
    // Even if the server call fails, still clear the visible chat.
  }
  chatMessages.innerHTML = '';
  appendMessage('bot', "Hi! 👋 I'm the 21st Academy assistant. How can I help you with the Career Mapping Workshop?");
  showQuickReplies();
});

// --- Send message -------------------------------------------------
async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = '';
  chatSend.disabled = true;
  appendMessage('user', text);

  const typingEl = appendTyping();

  try {
    if (CHATBOT_CONFIG.USE_STREAMING) {
      await sendStreaming(text, typingEl);
    } else {
      await sendNonStreaming(text, typingEl);
    }
    setOnline(true);
  } catch (err) {
    typingEl.remove();
    appendMessage(
      'bot',
      "Sorry, I'm offline right now. Please call us at +91 99 44 74 7090 or email admin@21stacademy.in."
    );
    setOnline(false);
    scheduleReconnectCheck();
  } finally {
    chatSend.disabled = false;
  }
}

async function sendNonStreaming(text, typingEl) {
  const response = await fetch(`${CHATBOT_CONFIG.API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text, session_id: sessionId, stream: false }),
  });

  if (!response.ok) throw new Error(`Backend error ${response.status}`);
  const data = await response.json();
  typingEl.remove();

  const reply = data.response || "I'm having trouble right now. Please contact us at admin@21stacademy.in.";
  appendMessage('bot', reply);
}

async function sendStreaming(text, typingEl) {
  const response = await fetch(`${CHATBOT_CONFIG.API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text, session_id: sessionId, stream: true }),
  });

  if (!response.ok || !response.body) throw new Error(`Backend error ${response.status}`);

  typingEl.remove();
  const bubble = appendMessage('bot', '');
  const contentSpan = bubble.querySelector('.chat-content');

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullText = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    fullText += decoder.decode(value, { stream: true });
    contentSpan.innerHTML = renderMarkdown(fullText);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  if (!fullText.trim()) {
    contentSpan.innerHTML = renderMarkdown(
      "I'm having trouble right now. Please contact us at admin@21stacademy.in."
    );
  }
}

// --- Message rendering -------------------------------------------------
function appendMessage(role, text) {
  const div = document.createElement('div');
  div.className = `chat-msg ${role}`;

  const content = document.createElement('span');
  content.className = 'chat-content';
  content.innerHTML = renderMarkdown(text);
  div.appendChild(content);

  const ts = document.createElement('span');
  ts.className = 'chat-timestamp';
  ts.textContent = formatTime(new Date());
  div.appendChild(ts);

  if (role === 'bot') {
    const copyBtn = document.createElement('button');
    copyBtn.className = 'chat-copy-btn';
    copyBtn.textContent = '📋 Copy';
    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(content.textContent || '');
      copyBtn.textContent = '✓ Copied';
      setTimeout(() => (copyBtn.textContent = '📋 Copy'), 1500);
    });
    div.appendChild(copyBtn);
  }

  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

function appendTyping() {
  const div = document.createElement('div');
  div.className = 'chat-msg bot chat-typing';
  div.innerHTML = '<span></span><span></span><span></span>';
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// --- Minimal, safe Markdown rendering -------------------------------------------------
// Escapes HTML first, THEN applies formatting — so model output can never
// inject markup, only styled text.
function escapeHtml(text) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(text));
  return div.innerHTML;
}

function renderMarkdown(raw) {
  let html = escapeHtml(raw);

  // fenced code blocks ```code```
  html = html.replace(/```([\s\S]*?)```/g, (_, code) => `<pre><code>${code.trim()}</code></pre>`);
  // inline code `code`
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  // bold **text**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // italic *text*
  html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
  // line breaks
  html = html.replace(/\n/g, '<br>');

  return html;
}

// --- Connection status -------------------------------------------------
function setOnline(online) {
  if (!botStatus) return;
  botStatus.textContent = online ? '● Online' : '● Offline';
  botStatus.classList.toggle('offline', !online);
}

let reconnectTimer = null;
function scheduleReconnectCheck() {
  if (reconnectTimer) return;
  reconnectTimer = setInterval(async () => {
    try {
      const res = await fetch(`${CHATBOT_CONFIG.API_BASE_URL.replace(/\/api$/, '')}/health`);
      if (res.ok) {
        setOnline(true);
        clearInterval(reconnectTimer);
        reconnectTimer = null;
      }
    } catch (_) {
      /* still offline, keep trying */
    }
  }, 10000);
}

// --- Input handlers -------------------------------------------------
chatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});
chatSend.addEventListener('click', sendMessage);

// --- Quick reply chips -------------------------------------------------
const quickReplies = [
  'When is the workshop?',
  'Is it free to attend?',
  'Where is the venue?',
  'How do I register?',
];

function showQuickReplies() {
  const chipsDiv = document.createElement('div');
  chipsDiv.className = 'chat-quick-replies';
  quickReplies.forEach((q) => {
    const chip = document.createElement('button');
    chip.textContent = q;
    chip.addEventListener('click', () => {
      chatInput.value = q;
      sendMessage();
      chipsDiv.remove();
    });
    chipsDiv.appendChild(chip);
  });
  chatMessages.appendChild(chipsDiv);
}

setTimeout(showQuickReplies, 600);
