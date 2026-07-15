# AI-First CRM — HCP Module (Log Interaction Screen)

An AI-first CRM module for pharmaceutical field representatives to log interactions with
Healthcare Professionals (HCPs) — either through a structured form or a conversational chat
interface powered by a **LangGraph** agent backed by **Groq (gemma2-9b-it)**.

---

## 1. What This Project Does

A field rep can record a meeting/call/email with a doctor in two ways:

1. **Form Mode** — fill in doctor name, hospital, products discussed, notes, follow-up date, etc.
2. **Chat Mode** — type naturally, e.g.:
   > "Met Dr. Sharma at Apollo Hospital, discussed Cardivex and Neurotol, follow up in 2 weeks"

   The LangGraph agent classifies the intent, extracts structured entities (doctor, hospital,
   products, follow-up date, sentiment) using the LLM, summarizes the conversation, and saves a
   structured record to PostgreSQL — all without the rep filling out a single form field.

Both modes write into the same underlying draft state, so a rep can start in Chat Mode and
review/edit the AI-extracted fields in Form Mode before saving, or vice versa.

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Redux Toolkit, React Router |
| Backend | Python, FastAPI |
| AI Agent Framework | LangGraph |
| LLM | Groq — `gemma2-9b-it` (primary), `llama-3.3-70b-versatile` (optional, for reasoning-heavy recommendation tasks) |
| Database | PostgreSQL (via SQLAlchemy ORM) |
| Font | Google Inter |

---

## 3. LangGraph Agent & Tools

The agent sits behind both the Chat interface and (indirectly) the Form submission, ensuring
every interaction — however it was captured — goes through one consistent pipeline: intent
routing → tool execution → structured persistence.

**Graph flow:** `Intent Router` (LLM classifies the message) → one of 5 tool nodes → `Response
Formatter` (LLM writes the conversational reply) → end.

### The 5 Tools

1. **Log Interaction** — Extracts doctor name, hospital, products discussed, follow-up date, and
   sentiment from free text using the LLM, generates a summary, resolves/creates the matching HCP
   record (fuzzy name+hospital matching), and saves the interaction to PostgreSQL.
2. **Edit Interaction** — Parses a natural-language edit instruction (e.g. "push the follow-up to
   next Friday") into a constrained field diff and applies it to an existing record.
3. **Search Interaction** — Parses a natural-language query into structured filters (doctor,
   hospital, product, date range) and retrieves matching interactions.
4. **Summarize Previous Interactions** — Rolls up all past interactions with a given HCP into a
   concise pre-meeting briefing highlighting trends and sentiment trajectory.
5. **Recommend Follow-up Actions** — Suggests a specific next-best-action based on the most recent
   interaction's summary, sentiment, and products discussed.

---

## 4. Project Structure

```
ai-crm-hcp-module/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── config.py            # Environment-driven settings
│   │   ├── database.py          # SQLAlchemy engine/session
│   │   ├── models/               # ORM models (Rep, HCP, Interaction, Chat)
│   │   ├── schemas/              # Pydantic request/response contracts
│   │   ├── routers/              # /hcp, /interaction, /chat endpoints
│   │   ├── services/              # interaction_service, hcp_resolver
│   │   ├── agent/                 # LangGraph graph, state, prompts, tools
│   │   │   └── tools/              # 5 LangGraph tools
│   │   └── utils/                 # JSON parsing helper for LLM output
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── store/                 # Redux Toolkit slices
    │   ├── api/                   # Axios client
    │   ├── components/            # layout, dashboard, logInteraction, common
    │   └── pages/                 # Route-level wrappers
    └── package.json
```

---

## 5. Setup & Run Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ (npm)
- PostgreSQL 14+
- A Groq API key — get one free at https://console.groq.com/keys

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set GROQ_API_KEY and DATABASE_URL

# Create the database (adjust to your local Postgres setup)
psql -U postgres -c "CREATE DATABASE crm_hcp_db;"

uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`. Tables are created automatically on
startup, and a default rep (`id=1`) is seeded so the frontend can post interactions immediately
without a login flow.

Interactive API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm start
```
The app runs at `http://localhost:3000` and expects the backend at `http://localhost:8000`
(configurable via `REACT_APP_API_BASE_URL` if needed).

---

## 6. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat` | Send a message to the LangGraph agent |
| POST | `/interaction` | Create an interaction (Form Mode) |
| PUT | `/interaction/{id}` | Update an interaction |
| GET | `/interaction` | List/search interactions |
| GET | `/interaction/{id}` | Fetch a single interaction |
| GET | `/hcp` | List known HCPs (autocomplete) |

---

## 7. Scope Notes

- Single-tenant: no authentication/login flow is implemented, as it wasn't part of the assignment
  scope. All interactions are attributed to a single seeded rep (`id=1`).
- Alembic is set up for schema migrations, but `main.py` also runs `Base.metadata.create_all()`
  on startup so the project runs out-of-the-box without a manual migration step.

---

## 8. Submission

### GitHub Repository
Frontend and backend code for this project are both included in this single repository
(see [Project Structure](#4-project-structure) above).

**Repository link:** `<PASTE_YOUR_GITHUB_REPO_URL_HERE>`

### Video Walkthrough (10–15 minutes)
The video covers:
- A walkthrough of the frontend (Dashboard, Form Mode, Chat Mode side-by-side)
- A live demo of all 5 LangGraph tools: Log Interaction, Edit Interaction, Search Interaction,
  Summarize Previous Interactions, and Recommend Follow-up Actions
- A simple explanation of the codebase and how the project is structured
  (frontend → Redux → Axios → FastAPI → LangGraph agent → PostgreSQL)
- A brief summary of what was understood from the task requirements

**Video link:** `<PASTE_YOUR_VIDEO_URL_HERE>`