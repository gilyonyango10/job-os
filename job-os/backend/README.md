# Job OS API

FastAPI backend for capturing and tracking jobs. SQLite is the local default so the first vertical slice can run without PostgreSQL.

## Run locally

```bash
cd job-os/backend
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 48217
```

Open [http://127.0.0.1:48217/docs](http://127.0.0.1:48217/docs) for the interactive API.

Copy `.env.example` to `.env` if you want to override the database URL or CORS origins. Without an env file, the app stores data in `job_os.db` in this directory and allows the local Jobs page at `http://127.0.0.1:43180`.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness check |
| POST | `/jobs` | Create a job |
| GET | `/jobs` | List jobs |
| GET | `/jobs/{job_id}` | Fetch one job |

New jobs default to `status=DISCOVERED` and `source=manual`.

## Tests

```bash
cd job-os/backend
uv sync --group dev
uv run pytest
```

## Switching to PostgreSQL later

Set `DATABASE_URL` to a SQLAlchemy PostgreSQL URL, for example:

```bash
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/job_os
```

The session layer already branches only on SQLite connection arguments. No application code needs to know which database is in use beyond that URL.
