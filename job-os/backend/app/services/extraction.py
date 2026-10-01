import json
import re

from pydantic import ValidationError

from app.ai.errors import AIResponseInvalid, EmptyJobDescription
from app.ai.provider import AIProvider
from app.models.requirement import JobRequirement
from app.schemas.requirement import ExtractedRequirement, ExtractionPayload

EXTRACTION_SYSTEM_PROMPT = """
You extract structured hiring requirements from a job description.

Return JSON only in this shape:
{"requirements":[{"name":"...","category":"skill","importance":"required","description":"...","evidence_text":"..."}]}

Rules:
- Only extract requirements the job description actually supports.
- Do not invent technologies, tools, credentials, or years of experience.
- Do not infer years of experience unless the description states them.
- Do not turn a responsibility into a required skill unless the description supports that.
- Use category from: skill, technology, experience, education, responsibility, certification, other.
- Use importance required or preferred only when the description makes that distinction. If it is unclear, use required.
- Preserve the employer's terminology where practical.
- evidence_text must be a short verbatim excerpt copied from the job description. Do not invent evidence_text.
- If the description is ambiguous, keep the ambiguity in name/description rather than guessing.
- If nothing can be extracted, return {"requirements":[]}.
""".strip()


class RequirementExtractor:
    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    def extract(self, description: str) -> list[ExtractedRequirement]:
        cleaned = description.strip()
        if not cleaned:
            raise EmptyJobDescription("Job description is empty.")

        raw = self.provider.complete(
            system=EXTRACTION_SYSTEM_PROMPT,
            user=f"Job description:\n\n{cleaned}",
        )
        payload = _parse_payload(raw)
        supported = [
            item
            for item in payload.requirements
            if _evidence_is_verbatim(cleaned, item.evidence_text)
        ]
        if payload.requirements and not supported:
            raise AIResponseInvalid(
                "No extracted requirements were supported by the job description."
            )
        return supported[:50]


def _parse_payload(raw: str) -> ExtractionPayload:
    try:
        data = json.loads(_extract_json(raw))
    except json.JSONDecodeError as exc:
        raise AIResponseInvalid("AI response was not valid JSON.") from exc
    try:
        return ExtractionPayload.model_validate(data)
    except ValidationError as exc:
        raise AIResponseInvalid("AI response did not match the extraction schema.") from exc


def _extract_json(raw: str) -> str:
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise json.JSONDecodeError("No JSON object found", text, 0)
    return text[start : end + 1]


def _evidence_is_verbatim(description: str, evidence: str) -> bool:
    return _collapse(evidence) in _collapse(description)


def _collapse(value: str) -> str:
    return " ".join(value.lower().split())


def requirement_key(item: JobRequirement | ExtractedRequirement) -> str:
    return " ".join(item.name.lower().split())
