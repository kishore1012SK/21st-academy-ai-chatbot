# 21st Academy — Self-Hosted AI Chatbot

## 1. What already existed

Your `career-mapping-workshop/` site is a static page (`index.html` + `css/style.css`
+ `js/main.js` + `js/chatbot.js`) for the Career Mapping Workshop event. It already had
a floating chatbot UI (button, popup window, typing dots, quick-reply chips) — the
**only** problem was that `js/chatbot.js` called `https://api.anthropic.com/v1/messages`
directly from the browser with no API key, which can't work in production and would
leak a key to every visitor if one were ever added client-side.

## 2. What changed, and why

| Change | Reason |
|---|---|
| Added `backend/` (FastAPI) | Owns all AI calls server-side. Nothing about your keys or prompts is ever exposed to the browser. |
| `backend` talks only to `Ollama` (`llama3`) at `OLLAMA_BASE_URL` | No OpenAI/Dialogflow/Botpress/Chatbase/Tidio/etc. Fully private, fully owned by you. |
| Rewrote `js/chatbot.js` | Now calls **your own** `/api/chat` instead of Anthropic. UI markup, styling, and every existing feature (typing dots, quick replies) were kept — I only added a clear-chat button, timestamps, copy-to-clipboard, streaming, and auto-reconnect. |
| Appended a few CSS rules to `css/style.css` | Purely additive — styles the new small elements above, using your existing crimson/dark theme variables. Nothing already there was touched. |
| `index.html` | One small addition: a 🗑 clear-chat button next to the existing ✕ close button. |
| `docker-compose.yml`, `nginx/` | Wires your static site + backend + Ollama together for a one-command deploy on any Ubuntu/Linux VPS. |

Nothing in your existing HTML/CSS/JS was rewritten or restructured — only extended.

## 3. Architecture

```
Visitor's browser
   │
   │  fetch('/api/chat')  (same-origin, no key ever exposed)
   ▼
Nginx  ── serves career-mapping-workshop/ as static files
   │  └─ proxies /api/* and /health to the backend
   ▼
FastAPI backend (backend/)
   │  • JWT auth, rate limiting, input validation, CORS
   │  • SQLite (dev) / Postgres (prod) — users, conversations, messages,
   │    documents, feedback
   │  • Local RAG: extract → chunk → embed → cosine search, no vector-DB SaaS
   ▼
Ollama  (http://localhost:11434, or your own Linux server later)
   │  model: llama3 (chat), nomic-embed-text (embeddings)
   ▼
Response streams back to FastAPI → Nginx → browser
```

Moving Ollama to a dedicated Linux server later is a **one-line change**
(`OLLAMA_BASE_URL` in `backend/.env`) — the frontend never needs to change.

## 4. Run it locally (development)

```bash
# 1) Install and start Ollama, then pull the two models used
#    https://ollama.com/download
ollama pull llama3
ollama pull nomic-embed-text
ollama serve   # if not already running as a service

# 2) Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit JWT_SECRET, ADMIN_PASSWORD, etc.
uvicorn main:app --reload --port 8000

# 3) Frontend — serve the static site with any dev server, e.g.:
cd ../career-mapping-workshop
python3 -m http.server 5500
# Open http://127.0.0.1:5500 — the chatbot now talks to http://127.0.0.1:8000/api
# (set window.CHATBOT_API_BASE_URL before chatbot.js loads if the port differs)
```

Visit `http://127.0.0.1:8000/docs` for interactive API docs (Swagger UI).

## 5. Run it with Docker (recommended for a VPS)

```bash
cp backend/.env.example backend/.env   # edit secrets first!
docker compose up -d --build

# Pull the models into the running Ollama container (one-time):
docker exec -it academy-ollama ollama pull llama3
docker exec -it academy-ollama ollama pull nomic-embed-text
```

This starts:
- **ollama** — the local model runtime
- **backend** — FastAPI on :8000 (internal)
- **nginx** — serves the static site on :80 and proxies `/api/*` to the backend

Then point your domain's DNS at the VPS and, when ready, uncomment the HTTPS
server block in `nginx/nginx.conf` after obtaining certificates (e.g. via
certbot) — see the comments in that file.

## 6. API reference

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | — | Backend + Ollama reachability |
| POST | `/api/chat` | — | Send a message, get a reply (`stream: true/false`) |
| GET | `/api/history?session_id=` | — | Fetch a visitor's chat history |
| DELETE | `/api/history?session_id=` | — | Clear a visitor's chat history |
| POST | `/api/feedback` | — | Thumbs up/down on a reply |
| POST | `/api/auth/login` | — | Admin login → JWT |
| POST | `/api/upload` | Bearer JWT (admin) | Upload a PDF/DOCX/TXT/CSV/XLSX into the local knowledge base |

Default bootstrap admin (change immediately via `.env`):
`admin@21stacademy.in` / `ChangeMe123!`

## 7. Security notes

- Passwords are hashed with bcrypt; JWTs are signed with `JWT_SECRET` (set a
  long random value in production — see the comment in `.env.example`).
- `ALLOWED_ORIGINS` in `.env` whitelists exactly which domains may call the
  API — update it to your real domain(s) before going live.
- Rate limits are applied per-IP on `/chat`, `/upload`, and `/auth/login`.
- All uploaded documents and their embeddings stay on disk on your own
  server (`backend/uploads/`, `backend/vector_db/`) — nothing is sent
  anywhere except to your own Ollama instance.

## 8. What I did not build

To keep this an *extension* of your real site rather than a rebuild, I did
not create a separate React admin dashboard UI (document 1's spec) — the
backend already exposes everything an admin panel would need
(`/api/upload`, `/api/history`, `/api/auth/login`) via a documented REST API
at `/docs`, so a small admin frontend can be added later without touching
anything here. Say the word if you'd like that built next.
