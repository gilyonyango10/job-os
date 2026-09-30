# Job OS

Personal job-hunting operating system. The first slice captures jobs in a FastAPI backend and a React Jobs page.

```
job-os/
  backend/     FastAPI API (health + jobs)
  frontend/    Next.js Jobs page
  extension/   Browser extension
  docs/        Product and engineering docs
```

## Run locally

Terminal 1 — API:

```bash
cd job-os/backend
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 48217
```

Terminal 2 — web app:

```bash
cd job-os/frontend
cp .env.example .env.local
npm install
npm run dev
```

- Jobs page: http://127.0.0.1:43180
- API docs: http://127.0.0.1:48217/docs

`NEXT_PUBLIC_API_URL` points the frontend at the backend. `CORS_ORIGINS` on the API must include the frontend origin.

## Docs

- `job-os/docs/PRODUCT.md` — product vision
- `job-os/docs/ENGINEERING.md` — stack and development principles
