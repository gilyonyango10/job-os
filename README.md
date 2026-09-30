# Job OS

Personal job-hunting operating system. The first slice is a FastAPI backend that stores jobs in SQLite.

```
job-os/
  backend/     FastAPI API (health + jobs)
  frontend/    Web application
  extension/   Browser extension
  docs/        Product and engineering docs
```

## Run the API

```bash
cd job-os/backend
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 48217
```

- API docs: http://127.0.0.1:48217/docs
- Health: `GET /health`
- Jobs: `POST /jobs`, `GET /jobs`, `GET /jobs/{job_id}`

See `job-os/backend/README.md` for tests and the PostgreSQL switch path.

## Docs

- `job-os/docs/PRODUCT.md` — product vision
- `job-os/docs/ENGINEERING.md` — stack and development principles
