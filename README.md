# autonomous_research_agent
An agentic AI system that takes open-ended objectives (e.g., analyze a company, review documents, assess risks) and autonomously decomposes them into executable steps.

## Backend V1 (Swagger Test Ready)

### What V1 does
- Starts a research run from a topic.
- Executes an agentic pipeline:
  - plan research
  - web search
  - content extraction
  - summarization + insight extraction
  - finding validation (dedupe + evidence strength)
  - synthesis + report generation
- Stores run state in memory and exposes status/history endpoints.
- Returns typed JSON responses documented in Swagger.

### Run backend locally
```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open Swagger docs:
- `http://localhost:8000/docs`

### Required/optional env vars
- `OPENROUTER_API_KEY` (optional but recommended for LLM synthesis)
- `OPENROUTER_BASE_URL` (optional, default is OpenRouter)
- `OPENROUTER_CHAT_MODEL` (optional, default `openrouter/free`)

Without `OPENROUTER_API_KEY`, V1 still works using fallback deterministic synthesis.

### Main endpoints
- `POST /api/v1/research/start`
- `GET /api/v1/research/run/{run_id}`
- `GET /api/v1/runs/`
- `GET /api/v1/health`

### Example request (`POST /api/v1/research/start`)
```json
{
  "topic": "AI regulation trends in LATAM",
  "max_iterations": 5
}
```

### Example response fields
- `run_id`, `topic`, `status`
- `steps[]`
- `summary`
- `findings[]` with `evidence_strength` and `citations`
- `report`
- `created_at`, `completed_at`, `error`
