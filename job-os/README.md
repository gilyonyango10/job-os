# Job OS

Personal job-hunting operating system.

```
backend/     FastAPI API
frontend/    Web application
extension/   Browser extension
docs/        Product and engineering docs
```

Run the API from `backend/`:

```bash
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 48217
```
