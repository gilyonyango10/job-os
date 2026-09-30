# Job OS frontend

Minimal Jobs and Candidate Profile pages. They talk to the FastAPI backend through a small typed API client.

## Run locally

Start the API first:

```bash
cd job-os/backend
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 48217
```

Then start the web app:

```bash
cd job-os/frontend
cp .env.example .env.local
npm install
npm run dev
```

Open http://127.0.0.1:43180 for jobs and http://127.0.0.1:43180/profile for the candidate profile.

`NEXT_PUBLIC_API_URL` selects the backend. The local default is `http://127.0.0.1:48217`.
