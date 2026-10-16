# AskSQL – SQL Chatbot for Business Data

Ask questions in plain English. Get the SQL, a chart and a table back.

Example: you type *"Which product sold the most last month?"*. The app writes safe SQL, runs it on the database and shows the answer as a chart.

## Features

- **English to SQL** using an LLM: **Google Gemini** (free tier, default) or **Claude**.
- **Auto charts**: number card, line, bar, pie or scatter, chosen from the shape of the result.
- **Shows the SQL**, so you can check what was run.
- **Follow-up questions**: "now only for Karnataka" works because the chat remembers.
- **Auto-fix**: if the SQL fails, the error goes back to the LLM. It tries again, up to 2 more times.
- **RAG context**: only the tables, glossary terms and past good queries that match the question go into the prompt.
- **Business glossary**: terms like "revenue" and "active customer" have fixed meanings.
- **Upload CSV**: load your own file as a table and ask questions about it.
- **Explain answer**: a short summary of the result in simple English.
- **Feedback**: a thumbs up saves the question and SQL as a good example for later questions.
- **Cost and speed tracking**: tokens, cost and time for every question.
- **Evaluation**: 40 test questions with an accuracy report, shown on a dashboard page.

## Safety

| Layer | What it does |
|---|---|
| SQL validator (SQLGlot) | Allows only one SELECT. Blocks DELETE, DROP, UPDATE, INSERT, ALTER and PRAGMA. |
| Table allow-list | Queries can use only the business tables. |
| Read-only connection | The database itself refuses any write. |
| Row limit | Adds `LIMIT 1000` to every query. |
| Timeout | Stops a query after 10 seconds. |
| Rate limit | 30 questions per minute per user. |
| Prompt guard | User text is treated as data and cannot change the rules. |
| Audit log | Every question and SQL is saved. You can see them on the History page. |

## Architecture

```
 User ──► Next.js frontend (chat, Plotly charts)
               │  /api
               ▼
         FastAPI backend ──── cache (in memory)
               │
   1. Retriever (RAG) ── finds tables, glossary, good past queries
   2. Prompt builder ─── rules + schema + example rows + chat history + question
   3. LLM (Gemini/Claude) returns one SELECT query
   4. Validator ──────── SQLGlot: SELECT only, allowed tables, LIMIT
   5. Runner ─────────── read-only SQLite connection, 10 s timeout
         └─ on error: send the error back to the LLM and retry (max 2 times)
   6. Chart picker ───── number / line / bar / pie / scatter / table
   7. Save ───────────── history, logs, feedback (app.db)
```

- `business.db`: the data you ask about (customers, products, orders, order_items). Sample data from an Indian online store is created on first start.
- `app.db`: chat history, query logs, feedback and approved queries.

To keep the project simple and easy to run, it uses **SQLite** instead of PostgreSQL, a small **TF-IDF search** instead of pgvector, and an **in-memory cache** instead of Redis. The flow is the same as in the project description.

## Tech stack

| Part | Tools |
|---|---|
| Frontend | Next.js 14, Tailwind CSS, Plotly.js |
| Backend | FastAPI (Python) |
| LLM | Gemini (`gemini-3.8-flash`, free tier) or Claude (`claude-opus-5-5`) |
| Database | SQLite |
| SQL safety | SQLGlot |
| Testing | Pytest and an evaluation script |

## Folder structure

```
backend/
  app/
    main.py            FastAPI app
    config.py          settings (model, limits, paths)
    routes/            chat, history, feedback, upload, schema, eval report
    services/
      retriever.py     RAG search + schema docs + glossary
      prompt.py        prompt builder
      llm.py           Gemini / Claude client, token and cost tracking
      validator.py     SQLGlot safety checks
      runner.py        read-only query runner with timeout
      charts.py        chart picker
      pipeline.py      runs all the steps for one question
    db/                sample data (seed.py) and app database (app_db.py)
  eval/                questions.json (40 questions) + run_eval.py
  tests/               pytest tests
frontend/
  app/                 pages: chat, history, data, evaluation
  components/          AnswerCard, ChartView, DataTable, SqlView, Header
```

## How to run

You need **Python 3.10+**, **Node.js 18+** and a **Gemini API key** (free).

### 0. Get a free Gemini API key

1. Go to https://aistudio.google.com/apikey and sign in with a Google account.
2. Click **Create API key** and copy it.

No credit card is needed. The free tier has daily and per-minute limits, and Google may use free-tier data to improve its products, so do not upload private data.

### 1. Backend

```bash
cd backend
pip install -r requirements.txt

# set your API key
export GEMINI_API_KEY=your-key             # macOS / Linux / Git Bash
$env:GEMINI_API_KEY="your-key"             # Windows PowerShell (this terminal only)
setx GEMINI_API_KEY "your-key"             # Windows, permanent (open a new terminal after)

uvicorn app.main:app --reload --port 8000
```

**Use Claude instead (paid):** set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY=your-key`.
**Use another model:** set `LLM_MODEL`, for example `LLM_MODEL=gemini-2.5-flash`.

The sample database is created the first time the backend starts. API docs: http://localhost:8000/docs

### 2. Frontend (in a new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 and ask a question.

If the backend is not on port 8000, set `BACKEND_URL` (for example `BACKEND_URL=http://localhost:9000`) before `npm run dev`.

## How to test

### Unit and API tests (no API key needed, the LLM is mocked)

```bash
cd backend
pytest
```

The tests check the SQL validator, the chart picker, the chat flow, auto-fix, blocking of DELETE, feedback and CSV upload.

### Accuracy evaluation (uses the real LLM)

```bash
cd backend
python -m eval.run_eval                 # full app: RAG + glossary + examples
python -m eval.run_eval --mode basic    # basic prompt, for comparison
python -m eval.run_eval --limit 5       # quick run on 5 questions
```

Each question makes 1 to 3 LLM calls. On the Gemini free tier this is free, but a full run can hit the per-minute limit; the app waits and retries automatically. With Claude it costs about $1 to $2 per full run.

The report is saved to `backend/eval/report.json`. Open the **Evaluation** page in the app to see accuracy, time, cost and failed cases.

### Try these questions in the app

- Which product sold the most last month?
- Show monthly revenue for this year → then: *now only for Karnataka*
- What is the revenue share of each product category?
- How many active customers do we have?
- Delete all orders *(blocked: only read queries are allowed)*

## Reset the data

Stop the backend and delete the `backend/data` folder. Fresh sample data is created on the next start.
