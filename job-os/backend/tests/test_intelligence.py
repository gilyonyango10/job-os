from fastapi.testclient import TestClient

JOB = {
    "title": "Analytics Engineer",
    "company": "Harbor Studio",
    "location": "Remote",
    "description": "Build reliable reporting and forecasting tools.",
}


def _create_job(client: TestClient) -> str:
    response = client.post("/jobs", json=JOB)
    assert response.status_code == 201
    return response.json()["id"]


def _add_requirement(
    client: TestClient,
    job_id: str,
    name: str,
    *,
    category: str = "skill",
    importance: str = "required",
    description: str | None = None,
) -> dict:
    response = client.post(
        f"/jobs/{job_id}/requirements",
        json={
            "name": name,
            "category": category,
            "importance": importance,
            "description": description,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_requirement_for_job(client: TestClient) -> None:
    job_id = _create_job(client)

    body = _add_requirement(client, job_id, "Python", category="technology")

    assert body["name"] == "Python"
    assert body["category"] == "technology"
    assert body["importance"] == "required"
    assert body["job_id"] == job_id
    assert body["id"]


def test_list_requirements_for_job(client: TestClient) -> None:
    job_id = _create_job(client)
    first = _add_requirement(client, job_id, "Python")
    second = _add_requirement(client, job_id, "SQL", importance="preferred")

    response = client.get(f"/jobs/{job_id}/requirements")

    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
    assert first["id"] in ids
    assert second["id"] in ids


def test_update_requirement(client: TestClient) -> None:
    job_id = _create_job(client)
    created = _add_requirement(client, job_id, "Python")

    response = client.put(
        f"/jobs/{job_id}/requirements/{created['id']}",
        json={
            "name": "TypeScript",
            "category": "skill",
            "importance": "preferred",
            "description": "Used in the product UI",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "TypeScript"
    assert body["importance"] == "preferred"
    assert body["description"] == "Used in the product UI"


def test_delete_requirement(client: TestClient) -> None:
    job_id = _create_job(client)
    created = _add_requirement(client, job_id, "Python")

    deleted = client.delete(f"/jobs/{job_id}/requirements/{created['id']}")
    remaining = client.get(f"/jobs/{job_id}/requirements")

    assert deleted.status_code == 204
    assert remaining.json() == []


def test_requirement_routes_return_404_for_unknown_job(client: TestClient) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    created = client.post(
        f"/jobs/{missing}/requirements",
        json={"name": "Python", "category": "skill", "importance": "required"},
    )
    listed = client.get(f"/jobs/{missing}/requirements")
    analysis = client.get(f"/jobs/{missing}/analysis")

    assert created.status_code == 404
    assert listed.status_code == 404
    assert analysis.status_code == 404


def test_strong_evidence_matching_and_evidence(client: TestClient) -> None:
    job_id = _create_job(client)
    _add_requirement(client, job_id, "Python")
    client.post("/profile/skills", json={"name": "Python", "category": "technical"})
    client.post(
        "/profile/projects",
        json={
            "name": "Operational Cost Forecasting Model",
            "description": "Forecast operational cost.",
            "technologies": "Python, FastAPI",
        },
    )

    analysis = client.get(f"/jobs/{job_id}/analysis").json()
    match = analysis["strong_evidence"][0]

    assert match["classification"] == "STRONG_EVIDENCE"
    assert match["requirement_name"] == "Python"
    assert "Python listed as a candidate skill" in match["evidence"]
    assert "Python used in Operational Cost Forecasting Model" in match["evidence"]
    assert analysis["gaps"] == []


def test_transferable_matching(client: TestClient) -> None:
    job_id = _create_job(client)
    _add_requirement(client, job_id, "React")
    client.post("/profile/skills", json={"name": "TypeScript", "category": "technical"})

    analysis = client.get(f"/jobs/{job_id}/analysis").json()

    assert analysis["strong_evidence"] == []
    assert len(analysis["transferable"]) == 1
    match = analysis["transferable"][0]
    assert match["classification"] == "TRANSFERABLE"
    assert match["requirement_name"] == "React"
    assert any("TypeScript listed as a candidate skill" in item for item in match["evidence"])
    assert any("may transfer to React" in item for item in match["evidence"])


def test_gap_detection_and_empty_profile(client: TestClient) -> None:
    job_id = _create_job(client)
    _add_requirement(client, job_id, "AWS")
    client.get("/profile")

    analysis = client.get(f"/jobs/{job_id}/analysis").json()

    assert analysis["strong_evidence"] == []
    assert analysis["transferable"] == []
    assert len(analysis["gaps"]) == 1
    assert analysis["gaps"][0]["requirement_name"] == "AWS"
    assert analysis["gaps"][0]["evidence"] == []
    assert analysis["required_gaps"][0]["requirement_name"] == "AWS"


def test_required_versus_preferred_gaps(client: TestClient) -> None:
    job_id = _create_job(client)
    _add_requirement(client, job_id, "Tableau", importance="required")
    _add_requirement(client, job_id, "Docker", importance="preferred")
    client.post("/profile/skills", json={"name": "Python", "category": "technical"})

    analysis = client.get(f"/jobs/{job_id}/analysis").json()
    required_names = {item["requirement_name"] for item in analysis["required_gaps"]}
    preferred_names = {item["requirement_name"] for item in analysis["preferred_gaps"]}

    assert required_names == {"Tableau"}
    assert preferred_names == {"Docker"}
    assert {item["requirement_name"] for item in analysis["gaps"]} == {"Tableau", "Docker"}


def test_multiple_requirements_and_analysis_endpoint(client: TestClient) -> None:
    job_id = _create_job(client)
    _add_requirement(client, job_id, "Python")
    _add_requirement(client, job_id, "React")
    _add_requirement(client, job_id, "AWS", importance="preferred")
    client.post("/profile/skills", json={"name": "Python", "category": "technical"})
    client.post("/profile/skills", json={"name": "JavaScript", "category": "technical"})

    response = client.get(f"/jobs/{job_id}/analysis")
    analysis = response.json()
    names = {item["name"] for item in analysis["requirements"]}

    assert response.status_code == 200
    assert analysis["job"]["id"] == job_id
    assert names == {"Python", "React", "AWS"}
    assert {item["requirement_name"] for item in analysis["strong_evidence"]} == {"Python"}
    assert {item["requirement_name"] for item in analysis["transferable"]} == {"React"}
    assert {item["requirement_name"] for item in analysis["gaps"]} == {"AWS"}
    assert analysis["required_gaps"] == []
    assert {item["requirement_name"] for item in analysis["preferred_gaps"]} == {"AWS"}


def test_unrelated_skills_are_not_matches(client: TestClient) -> None:
    job_id = _create_job(client)
    _add_requirement(client, job_id, "Java")
    _add_requirement(client, job_id, "Kubernetes")
    client.post("/profile/skills", json={"name": "Python", "category": "technical"})
    client.post("/profile/skills", json={"name": "SQL", "category": "technical"})

    analysis = client.get(f"/jobs/{job_id}/analysis").json()

    assert analysis["strong_evidence"] == []
    assert analysis["transferable"] == []
    assert {item["requirement_name"] for item in analysis["gaps"]} == {"Java", "Kubernetes"}


def test_tableau_is_not_transferable_from_power_bi(client: TestClient) -> None:
    job_id = _create_job(client)
    _add_requirement(client, job_id, "Tableau")
    client.post("/profile/skills", json={"name": "Power BI", "category": "technical"})

    analysis = client.get(f"/jobs/{job_id}/analysis").json()

    assert analysis["strong_evidence"] == []
    assert analysis["transferable"] == []
    assert analysis["gaps"][0]["requirement_name"] == "Tableau"
