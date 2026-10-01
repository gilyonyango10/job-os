import inspect
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.ai.errors import AIProviderNotConfigured, AIResponseInvalid, EmptyJobDescription
from app.ai.factory import get_ai_provider
from app.schemas.requirement import ExtractedRequirement, ExtractionPayload
from app.services.extraction import RequirementExtractor, requirement_key
from app.services import extract_job as extract_job_module
from app.services import matching as matching_module

DESCRIPTION = """
Analytics Engineer — Harbor Studio

Required:
- Python for data pipelines
- Bachelor's degree in Computer Science
- 3 years of experience in analytics engineering

Preferred:
- dbt for transformation work
- AWS Certified Solutions Architect

Responsibilities:
- Own reporting models used by operations
""".strip()

VALID_PAYLOAD = {
    "requirements": [
        {
            "name": "Python",
            "category": "technology",
            "importance": "required",
            "description": "Used for data pipelines",
            "evidence_text": "Python for data pipelines",
        },
        {
            "name": "Bachelor's degree in Computer Science",
            "category": "education",
            "importance": "required",
            "description": None,
            "evidence_text": "Bachelor's degree in Computer Science",
        },
        {
            "name": "3 years of experience in analytics engineering",
            "category": "experience",
            "importance": "required",
            "description": None,
            "evidence_text": "3 years of experience in analytics engineering",
        },
        {
            "name": "dbt",
            "category": "technology",
            "importance": "preferred",
            "description": "Used for transformation work",
            "evidence_text": "dbt for transformation work",
        },
        {
            "name": "AWS Certified Solutions Architect",
            "category": "certification",
            "importance": "preferred",
            "description": None,
            "evidence_text": "AWS Certified Solutions Architect",
        },
        {
            "name": "Own reporting models used by operations",
            "category": "responsibility",
            "importance": "required",
            "description": None,
            "evidence_text": "Own reporting models used by operations",
        },
        {
            "name": "SQL",
            "category": "skill",
            "importance": "required",
            "description": None,
            "evidence_text": "Python for data pipelines",
        },
        {
            "name": "Reporting ownership",
            "category": "other",
            "importance": "preferred",
            "description": None,
            "evidence_text": "Own reporting models used by operations",
        },
    ]
}


class FakeProvider:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[tuple[str, str]] = []

    def complete(self, *, system: str, user: str) -> str:
        self.calls.append((system, user))
        return self.response


def _create_job(client: TestClient, description: str = DESCRIPTION) -> str:
    response = client.post(
        "/jobs",
        json={
            "title": "Analytics Engineer",
            "company": "Harbor Studio",
            "location": "Remote",
            "description": description,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def _use_provider(monkeypatch: pytest.MonkeyPatch, provider: FakeProvider) -> None:
    monkeypatch.setattr(extract_job_module, "get_ai_provider", lambda: provider)


def test_extract_requirements_from_mocked_provider(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    job_id = _create_job(client)
    provider = FakeProvider(json.dumps(VALID_PAYLOAD))
    _use_provider(monkeypatch, provider)

    response = client.post(f"/jobs/{job_id}/extract-requirements")
    body = response.json()
    names = {item["name"] for item in body["requirements"]}

    assert response.status_code == 200
    assert body["created_count"] == 8
    assert body["skipped_duplicate_count"] == 0
    assert names == {
        "Python",
        "Bachelor's degree in Computer Science",
        "3 years of experience in analytics engineering",
        "dbt",
        "AWS Certified Solutions Architect",
        "Own reporting models used by operations",
        "SQL",
        "Reporting ownership",
    }
    assert len(provider.calls) == 1
    assert "Job description:" in provider.calls[0][1]
    assert "Python for data pipelines" in provider.calls[0][1]


def test_structured_ai_response_validation() -> None:
    payload = ExtractionPayload.model_validate(VALID_PAYLOAD)
    python = payload.requirements[0]

    assert python.name == "Python"
    assert python.category.value == "technology"
    assert python.importance.value == "required"
    assert python.evidence_text == "Python for data pipelines"

    extractor = RequirementExtractor(FakeProvider(json.dumps(VALID_PAYLOAD)))
    extracted = extractor.extract(DESCRIPTION)
    assert [item.name for item in extracted] == [item["name"] for item in VALID_PAYLOAD["requirements"]]


def test_invalid_ai_response_is_rejected(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    job_id = _create_job(client)
    _use_provider(monkeypatch, FakeProvider("not-json"))

    response = client.post(f"/jobs/{job_id}/extract-requirements")

    assert response.status_code == 502
    assert "not valid JSON" in response.json()["detail"]

    with pytest.raises(AIResponseInvalid):
        RequirementExtractor(FakeProvider('{"requirements":[{"name":"Python"}]}')).extract(
            DESCRIPTION
        )

    with pytest.raises(ValidationError):
        ExtractionPayload.model_validate({"requirements": [{"name": "Python"}]})

    with pytest.raises(AIResponseInvalid):
        RequirementExtractor(
            FakeProvider(
                json.dumps(
                    {
                        "requirements": [
                            {
                                "name": "InventedLang",
                                "category": "technology",
                                "importance": "required",
                                "evidence_text": "InventedLang is required",
                            }
                        ]
                    }
                )
            )
        ).extract(DESCRIPTION)


def test_extract_unknown_job_returns_404(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _use_provider(monkeypatch, FakeProvider(json.dumps(VALID_PAYLOAD)))
    missing = "00000000-0000-0000-0000-000000000000"

    response = client.post(f"/jobs/{missing}/extract-requirements")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_extract_empty_job_description_returns_422(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    job_id = _create_job(client, description="   ")
    provider = FakeProvider(json.dumps(VALID_PAYLOAD))
    _use_provider(monkeypatch, provider)

    response = client.post(f"/jobs/{job_id}/extract-requirements")

    assert response.status_code == 422
    assert "no description" in response.json()["detail"].lower()
    assert provider.calls == []
    with pytest.raises(EmptyJobDescription):
        RequirementExtractor(provider).extract("  ")


def test_ai_provider_not_configured_returns_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    job_id = _create_job(client)
    monkeypatch.setattr("app.ai.factory.settings.ai_provider", "none")
    monkeypatch.setattr("app.config.settings.ai_provider", "none")

    response = client.post(f"/jobs/{job_id}/extract-requirements")

    assert response.status_code == 503
    assert "not configured" in response.json()["detail"].lower()
    with pytest.raises(AIProviderNotConfigured):
        get_ai_provider()


def test_duplicate_extraction_skips_existing_requirements(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    job_id = _create_job(client)
    manual = client.post(
        f"/jobs/{job_id}/requirements",
        json={"name": "Python", "category": "technology", "importance": "required"},
    )
    assert manual.status_code == 201
    _use_provider(monkeypatch, FakeProvider(json.dumps(VALID_PAYLOAD)))

    first = client.post(f"/jobs/{job_id}/extract-requirements")
    second = client.post(f"/jobs/{job_id}/extract-requirements")
    listed = client.get(f"/jobs/{job_id}/requirements").json()
    python_rows = [item for item in listed if item["name"] == "Python"]

    assert first.status_code == 200
    assert first.json()["created_count"] == 7
    assert first.json()["skipped_duplicate_count"] == 1
    assert second.status_code == 200
    assert second.json()["created_count"] == 0
    assert second.json()["skipped_duplicate_count"] == 8
    assert len(listed) == 8
    assert len(python_rows) == 1
    assert python_rows[0]["id"] == manual.json()["id"]
    assert python_rows[0]["evidence_text"] is None


def test_required_versus_preferred_extraction(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    job_id = _create_job(client)
    _use_provider(monkeypatch, FakeProvider(json.dumps(VALID_PAYLOAD)))

    body = client.post(f"/jobs/{job_id}/extract-requirements").json()
    by_name = {item["name"]: item["importance"] for item in body["requirements"]}

    assert by_name["Python"] == "required"
    assert by_name["dbt"] == "preferred"
    assert by_name["AWS Certified Solutions Architect"] == "preferred"


def test_evidence_text_is_preserved_verbatim(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    job_id = _create_job(client)
    _use_provider(monkeypatch, FakeProvider(json.dumps(VALID_PAYLOAD)))

    python = next(
        item
        for item in client.post(f"/jobs/{job_id}/extract-requirements").json()["requirements"]
        if item["name"] == "Python"
    )

    assert python["evidence_text"] == "Python for data pipelines"
    assert python["evidence_text"] in DESCRIPTION

    mixed = RequirementExtractor(
        FakeProvider(
            json.dumps(
                {
                    "requirements": [
                        {
                            "name": "Python",
                            "category": "technology",
                            "importance": "required",
                            "evidence_text": "Python for data pipelines",
                        },
                        {
                            "name": "InventedLang",
                            "category": "technology",
                            "importance": "required",
                            "evidence_text": "InventedLang is mandatory",
                        },
                    ]
                }
            )
        )
    ).extract(DESCRIPTION)
    assert [item.name for item in mixed] == ["Python"]


def test_extraction_covers_multiple_categories(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    job_id = _create_job(client)
    _use_provider(monkeypatch, FakeProvider(json.dumps(VALID_PAYLOAD)))

    categories = {
        item["category"]
        for item in client.post(f"/jobs/{job_id}/extract-requirements").json()["requirements"]
    }

    assert categories == {
        "technology",
        "education",
        "experience",
        "certification",
        "responsibility",
        "skill",
        "other",
    }


def test_extraction_service_does_not_perform_candidate_matching() -> None:
    extractor_source = inspect.getsource(RequirementExtractor)
    extract_job_source = Path(extract_job_module.__file__).read_text()
    extraction_source = Path(
        Path(extract_job_module.__file__).parent / "extraction.py"
    ).read_text()
    extracted = RequirementExtractor(FakeProvider(json.dumps(VALID_PAYLOAD))).extract(
        DESCRIPTION
    )

    assert "match_requirements" not in extractor_source
    assert "analyze_job" not in extractor_source
    assert "STRONG_EVIDENCE" not in extractor_source
    assert "matching" not in extract_job_source
    assert "analysis" not in extract_job_source
    assert "from app.services.matching" not in extraction_source
    assert all(not hasattr(item, "classification") for item in extracted)
    assert requirement_key(extracted[0]) == "python"


def test_deterministic_matching_works_after_ai_extraction(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    job_id = _create_job(client)
    _use_provider(monkeypatch, FakeProvider(json.dumps(VALID_PAYLOAD)))
    extracted = client.post(f"/jobs/{job_id}/extract-requirements")
    client.post("/profile/skills", json={"name": "Python", "category": "technical"})
    client.post("/profile/skills", json={"name": "SQL", "category": "technical"})

    analysis = client.get(f"/jobs/{job_id}/analysis")
    body = analysis.json()

    assert extracted.status_code == 200
    assert analysis.status_code == 200
    assert {item["requirement_name"] for item in body["strong_evidence"]} == {"Python", "SQL"}
    assert {item["requirement_name"] for item in body["preferred_gaps"]} >= {"dbt"}
    assert inspect.isfunction(matching_module.match_requirements)
