# AI Appointment Booking Assignment Starter (Python-First)

If you are strongest in Python, this repo now provides a **Python-only demo path**:

- `py_frontend/` → Streamlit chatbot UI (auth + session + chat)
- `py_backend/` → FastAPI API layer (`/api/auth/*`, `/api/chatbot/*`)
- `ai_service/` → FastAPI + LangChain appointment assistant (`/chat`)
- `database/` → PostgreSQL schema with `users`, `appointments`, `chat_sessions`

It also still contains the previous Node/React scaffold under `backend/` and `frontend/` if you need strict stack matching.

---

## Important interview note

Your assignment rubric explicitly asks for **React/Next.js frontend** and **Node.js Express backend**.

Using Streamlit + FastAPI can still work for a prototype demo if you:
1. state this was a deliberate time-box trade-off,
2. show clear architecture and service boundaries,
3. explain exactly how you would swap Streamlit→React and FastAPI→Express in production.

---

## Python-first Architecture

```text
[Streamlit UI]
  -> /api/auth/signup, /api/auth/login
  -> /api/chatbot/token
  -> /api/chatbot/message

[FastAPI backend (py_backend)]
  -> JWT auth + in-memory users/sessions
  -> short-lived chatbot token endpoint
  -> chat proxy to AI service

[FastAPI AI service (ai_service)]
  -> multi-turn slot filling
  -> availability simulation
  -> appointment confirmation
  -> JSONL logs
```

---

## 1) Run AI service

```bash
cd ai_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload --port 8000
```

Notes:
- If `OPENAI_API_KEY` is missing, the service falls back to deterministic prompts.
- Logs are written to `ai_service/chat_logs.jsonl`.

---

## 2) Run Python backend

```bash
cd py_backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload --port 7000
```

Endpoints:
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/chatbot/token`
- `POST /api/chatbot/message`

---

## 3) Run Streamlit frontend

```bash
cd py_frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

Open: `http://localhost:8501`

---

## 4) Database deliverable

Schema file: `database/schema.sql`

Apply with:
```bash
psql <connection_string> -f database/schema.sql
```

Includes:
- normalized tables (`users`, `appointments`, `chat_sessions`)
- useful indexes (including GIN for JSON transcript)
- sample seed inserts

---

## Demo flow (5 minutes)

1. Start AI service (8000), backend (7000), then Streamlit (8501).
2. Sign up and log in from Streamlit.
3. Send booking details progressively:
   - `service: haircut`
   - `date: 2026-01-03`
   - `time: 11:00`
   - `name: Alex`
   - `phone: +1-555-0100`
4. Show confirmation response and appointment ID.
5. Show `ai_service/chat_logs.jsonl` and `database/schema.sql`.

---

## What to say in interview

- “I used a Python-first stack to maximize delivery speed and reliability in 1–2 days.”
- “I preserved service boundaries so migrating UI to React and API to Express is straightforward.”
- “The AI orchestration and booking flow remain identical across framework swaps.”
