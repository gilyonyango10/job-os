# Job OS

Personal job-hunting operating system.

```
backend/     FastAPI API
frontend/    Next.js Jobs page
extension/   Browser extension
docs/        Product and engineering docs
```

## Run locally

```bash
# API
cd backend
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 48217

# Web app
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Jobs page: http://127.0.0.1:43180

Requirement extraction uses `AI_PROVIDER` and `AI_API_KEY` in `backend/.env`. Leave the provider as `none` until you want that endpoint enabled. Matching stays deterministic either way.
