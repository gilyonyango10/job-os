# Job OS API

FastAPI backend for capturing and tracking jobs. SQLite is the local default so the first vertical slice can run without PostgreSQL.

## Run locally

```bash
cd job-os/backend
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 48217
```

Open [http://127.0.0.1:48217/docs](http://127.0.0.1:48217/docs) for the interactive API.

Copy `.env.example` to `.env` if you want to override the database URL, CORS origins, or AI settings. Without an env file, the app stores data in `job_os.db` in this directory, allows the local Jobs page at `http://127.0.0.1:43180`, and leaves requirement extraction unconfigured.

Re-running extraction skips requirements with the same name and never deletes existing (including manual) rows. Review extracted requirements in the UI, then click Analyze Job separately.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness check |
| POST | `/jobs` | Create a job |
| GET | `/jobs` | List jobs |
| GET | `/jobs/{job_id}` | Fetch one job |
| POST | `/jobs/{job_id}/requirements` | Add a job requirement |
| GET | `/jobs/{job_id}/requirements` | List job requirements |
| PUT | `/jobs/{job_id}/requirements/{id}` | Update a requirement |
| DELETE | `/jobs/{job_id}/requirements/{id}` | Delete a requirement |
| POST | `/jobs/{job_id}/extract-requirements` | Extract requirements from the job description |
| GET | `/jobs/{job_id}/analysis` | Compare requirements with the profile |
| GET | `/profile` | Get or create the candidate profile |
| PUT | `/profile` | Update name, email, location, and summary |
| POST/PUT/DELETE | `/profile/education` | Education records |
| POST/PUT/DELETE | `/profile/experience` | Experience records |
| POST/PUT/DELETE | `/profile/skills` | Skills |
| POST/PUT/DELETE | `/profile/projects` | Projects |
| POST/PUT/DELETE | `/profile/certifications` | Certifications |

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
