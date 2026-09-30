from uuid import uuid4

from fastapi.testclient import TestClient

PROFILE = {
    "full_name": "Ada Okonkwo",
    "email": "ada@example.com",
    "location": "Nairobi",
    "professional_summary": "Backend engineer focused on practical job-search systems.",
}

EDUCATION = {
    "institution": "University of Nairobi",
    "degree": "BSc",
    "field_of_study": "Computer Science",
    "start_date": "2016-09-01",
    "end_date": "2020-06-30",
}

EXPERIENCE = {
    "company": "Northwind Labs",
    "title": "Backend Engineer",
    "start_date": "2021-01-11",
    "end_date": None,
    "description": "Built APIs that move applications toward interviews.",
}

SKILL = {"name": "Python", "category": "technical"}

PROJECT = {
    "name": "Job OS",
    "description": "Personal operating system for a job search.",
    "technologies": "Python, FastAPI, React",
}

CERTIFICATION = {
    "name": "AWS Certified Developer",
    "issuer": "Amazon",
    "date": "2023-04-15",
}


def test_get_profile_creates_empty_profile(client: TestClient) -> None:
    response = client.get("/profile")

    assert response.status_code == 200
    body = response.json()
    assert body["id"]
    assert body["full_name"] == ""
    assert body["education"] == []
    assert body["experience"] == []
    assert body["skills"] == []
    assert body["projects"] == []
    assert body["certifications"] == []


def test_put_profile_updates_basic_information(client: TestClient) -> None:
    response = client.put("/profile", json=PROFILE)

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == PROFILE["full_name"]
    assert body["email"] == PROFILE["email"]
    assert body["location"] == PROFILE["location"]
    assert body["professional_summary"] == PROFILE["professional_summary"]


def test_education_create_update_and_delete(client: TestClient) -> None:
    created = client.post("/profile/education", json=EDUCATION)
    assert created.status_code == 201
    item_id = created.json()["id"]
    assert created.json()["institution"] == EDUCATION["institution"]

    listed = client.get("/profile")
    assert item_id in {item["id"] for item in listed.json()["education"]}

    updated = client.put(
        f"/profile/education/{item_id}",
        json={**EDUCATION, "degree": "MSc"},
    )
    assert updated.status_code == 200
    assert updated.json()["degree"] == "MSc"

    deleted = client.delete(f"/profile/education/{item_id}")
    assert deleted.status_code == 204
    remaining = client.get("/profile")
    assert remaining.json()["education"] == []


def test_experience_create_update_and_delete(client: TestClient) -> None:
    created = client.post("/profile/experience", json=EXPERIENCE)
    assert created.status_code == 201
    item_id = created.json()["id"]

    updated = client.put(
        f"/profile/experience/{item_id}",
        json={**EXPERIENCE, "title": "Senior Backend Engineer"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Senior Backend Engineer"
    assert updated.json()["end_date"] is None

    deleted = client.delete(f"/profile/experience/{item_id}")
    assert deleted.status_code == 204
    assert client.get("/profile").json()["experience"] == []


def test_skill_create_update_and_delete(client: TestClient) -> None:
    created = client.post("/profile/skills", json=SKILL)
    assert created.status_code == 201
    item_id = created.json()["id"]

    updated = client.put(
        f"/profile/skills/{item_id}",
        json={"name": "TypeScript", "category": "technical"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "TypeScript"

    deleted = client.delete(f"/profile/skills/{item_id}")
    assert deleted.status_code == 204
    assert client.get("/profile").json()["skills"] == []


def test_project_create_update_and_delete(client: TestClient) -> None:
    created = client.post("/profile/projects", json=PROJECT)
    assert created.status_code == 201
    item_id = created.json()["id"]

    updated = client.put(
        f"/profile/projects/{item_id}",
        json={**PROJECT, "technologies": "Python, FastAPI"},
    )
    assert updated.status_code == 200
    assert updated.json()["technologies"] == "Python, FastAPI"

    deleted = client.delete(f"/profile/projects/{item_id}")
    assert deleted.status_code == 204
    assert client.get("/profile").json()["projects"] == []


def test_certification_create_update_and_delete(client: TestClient) -> None:
    created = client.post("/profile/certifications", json=CERTIFICATION)
    assert created.status_code == 201
    item_id = created.json()["id"]

    updated = client.put(
        f"/profile/certifications/{item_id}",
        json={**CERTIFICATION, "issuer": "Amazon Web Services"},
    )
    assert updated.status_code == 200
    assert updated.json()["issuer"] == "Amazon Web Services"

    deleted = client.delete(f"/profile/certifications/{item_id}")
    assert deleted.status_code == 204
    assert client.get("/profile").json()["certifications"] == []


def test_nested_item_not_found(client: TestClient) -> None:
    missing = str(uuid4())
    response = client.put(
        f"/profile/education/{missing}",
        json=EDUCATION,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Education not found"

    response = client.delete(f"/profile/skills/{missing}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Skill not found"


def test_education_requires_institution(client: TestClient) -> None:
    response = client.post("/profile/education", json={"degree": "BSc"})
    assert response.status_code == 422


def test_profile_includes_all_collections(client: TestClient) -> None:
    client.put("/profile", json=PROFILE)
    client.post("/profile/education", json=EDUCATION)
    client.post("/profile/experience", json=EXPERIENCE)
    client.post("/profile/skills", json=SKILL)
    client.post("/profile/projects", json=PROJECT)
    client.post("/profile/certifications", json=CERTIFICATION)

    response = client.get("/profile")
    body = response.json()
    assert body["full_name"] == PROFILE["full_name"]
    assert len(body["education"]) == 1
    assert len(body["experience"]) == 1
    assert len(body["skills"]) == 1
    assert len(body["projects"]) == 1
    assert len(body["certifications"]) == 1
