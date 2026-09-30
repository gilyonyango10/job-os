from uuid import uuid4

from fastapi.testclient import TestClient

SAMPLE_JOB = {
    "title": "Backend Engineer",
    "company": "Northwind Labs",
    "location": "Remote",
    "description": "Build APIs that help candidates move jobs toward interviews.",
    "source": "paste",
    "source_url": "https://example.com/jobs/backend-engineer",
}


def test_create_job_returns_created_record(client: TestClient) -> None:
    response = client.post("/jobs", json=SAMPLE_JOB)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == SAMPLE_JOB["title"]
    assert body["company"] == SAMPLE_JOB["company"]
    assert body["location"] == SAMPLE_JOB["location"]
    assert body["description"] == SAMPLE_JOB["description"]
    assert body["source"] == SAMPLE_JOB["source"]
    assert body["source_url"] == SAMPLE_JOB["source_url"]
    assert body["status"] == "DISCOVERED"
    assert body["id"]
    assert body["created_at"]


def test_create_job_defaults_source_and_status(client: TestClient) -> None:
    response = client.post(
        "/jobs",
        json={
            "title": "Data Analyst",
            "company": "Riverstone",
            "description": "Analyze application funnel performance.",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["source"] == "manual"
    assert body["status"] == "DISCOVERED"
    assert body["location"] is None
    assert body["source_url"] is None


def test_create_job_rejects_missing_title(client: TestClient) -> None:
    payload = {key: value for key, value in SAMPLE_JOB.items() if key != "title"}

    response = client.post("/jobs", json=payload)

    assert response.status_code == 422


def test_list_jobs_returns_created_jobs(client: TestClient) -> None:
    first = client.post("/jobs", json=SAMPLE_JOB)
    second = client.post(
        "/jobs",
        json={
            "title": "Product Designer",
            "company": "Harbor Studio",
            "description": "Design the application pipeline.",
        },
    )

    response = client.get("/jobs")

    assert response.status_code == 200
    body = response.json()
    ids = {job["id"] for job in body}
    assert first.json()["id"] in ids
    assert second.json()["id"] in ids


def test_get_job_returns_single_job(client: TestClient) -> None:
    created = client.post("/jobs", json=SAMPLE_JOB)
    job_id = created.json()["id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json()["id"] == job_id
    assert response.json()["title"] == SAMPLE_JOB["title"]


def test_get_job_returns_404_when_missing(client: TestClient) -> None:
    response = client.get(f"/jobs/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
