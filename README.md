# Autonomous Research Agent

An end-to-end AI research system that takes an open topic, investigates web sources, extracts evidence-backed insights, synthesizes a final answer, and exports a polished PDF report.

Built as a production-style full-stack project (FastAPI + React) with async execution, persistent run history, and recruiter-friendly engineering decisions.

---

## Why This Project

Most “AI research” demos stop at a single LLM prompt.  
This project implements a real workflow:

1. start async research jobs,
2. gather and process multiple sources,
3. structure intermediate outputs (steps, insights, confidence),
4. persist full run state in SQLite,
5. generate downloadable reports (PDF + JSON),
6. provide full run observability in a frontend UI.

---

## Core Features

- **Async agent workflow** (non-blocking start, background execution).
- **Source-level insight extraction** (1 LLM insight per page).
- **Typed backend contracts** with Swagger-ready schemas.
- **SQLite persistence** for runs, steps, findings, reports, and errors.
- **ReportLab PDF generation** with structured, polished layout.
- **Run lifecycle management** (`start`, `track`, `download report`, `delete`).
- **React UI** for research and history views.
- **Markdown rendering** in report content (`react-markdown` + `remark-gfm`).

---

## Technical Architecture

### Backend (FastAPI)

**Flow**
1. `POST /research/start` creates a run and schedules background execution.
2. Agent searches the web, extracts page content, and generates insights.
3. Findings are validated/deduplicated and synthesized into a final summary.
4. A structured report + PDF artifact is generated.
5. Run state is persisted and exposed via API.

**Design highlights**
- Async/non-blocking orchestration.
- Defensive fallbacks when external LLM calls fail.
- Persisted state model (not in-memory only).
- File-safe PDF serving and deletion logic.

### Frontend (React + Vite)

- **Research page**: start runs, watch steps, view summary/insights, download report.
- **History page**: inspect previous runs, open PDF, delete runs.
- Markdown-capable report rendering for better readability.

---

## API Surface

### Health
- `GET /api/v1/health`

### Research
- `POST /api/v1/research/start`
- `GET /api/v1/research/run/{run_id}`
- `GET /api/v1/research/report/{run_id}`
- `GET /api/v1/research/report/{run_id}/pdf`

### Runs
- `GET /api/v1/runs/`
- `DELETE /api/v1/runs/{run_id}`

Swagger docs:
- `http://localhost:8000/docs`

---

## Example Request

`POST /api/v1/research/start`

```json
{
  "topic": "AI regulation trends in LATAM",
  "max_iterations": 5
}
```

---

## Local Setup

### Backend

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:
- `http://localhost:5173`

---

## Environment Variables (Backend)

See `backend/.env.example`.

Key variables:
- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL`
- `OPENROUTER_CHAT_MODEL`
- `LLM_TEMPERATURE`
- `LLM_TIMEOUT_SECONDS`
- `LLM_MAX_RETRIES`
- `DATABASE_URL`
- `REPORTS_DIR`
- `ALLOWED_ORIGINS`

---

## Engineering Decisions Worth Highlighting

- **Async by default**: research runs do not block HTTP requests.
- **Persistence-first**: all run lifecycle data is stored in SQLite.
- **Strong API contracts**: pydantic schemas drive response consistency.
- **Graceful degradation**: deterministic fallbacks avoid hard failures.
- **Artifact pipeline**: report generation includes downloadable PDF outputs.
- **Security-conscious file handling**: report path validation before serving files.

---

## Current Status

This project is **functional end-to-end** and ready for demos:
- backend workflows run,
- frontend integrates full run lifecycle,
- report generation and download are implemented,
- history persistence works across sessions.

---

## Suggested Next Iterations

- Add authentication + multi-user run ownership.
- Add source citation quality scoring and quote extraction.
- Add background queue layer (Redis/Celery/RQ) for horizontal scaling.
- Add tests (unit/integration/e2e) and CI pipeline.
- Add containerized one-command local environment.

---

## License

MIT
