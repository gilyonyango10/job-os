import re
from dataclasses import dataclass

from app.models.candidate import Candidate
from app.models.requirement import JobRequirement
from app.schemas.analysis import MatchClassification, RequirementMatch

_STOPWORDS = {
    "a",
    "an",
    "and",
    "ability",
    "excellent",
    "experience",
    "familiarity",
    "for",
    "good",
    "in",
    "knowledge",
    "of",
    "on",
    "or",
    "plus",
    "strong",
    "the",
    "to",
    "use",
    "using",
    "with",
    "working",
    "year",
    "years",
}

_ALIASES = {
    "amazon web services": "aws",
    "js": "javascript",
    "node js": "node",
    "node.js": "node",
    "nodejs": "node",
    "postgres": "postgresql",
    "powerbi": "power bi",
    "ts": "typescript",
}

# Related terms that can support a requirement without being the same thing.
_TRANSFERABLE_SOURCES = {
    "angular": frozenset({"javascript", "typescript"}),
    "bi": frozenset({"business intelligence", "power bi", "sql"}),
    "business intelligence": frozenset({"power bi", "sql"}),
    "django": frozenset({"python"}),
    "fastapi": frozenset({"python"}),
    "flask": frozenset({"python"}),
    "forecasting": frozenset({"power bi", "python", "sql"}),
    "javascript": frozenset({"react", "typescript", "vue", "angular", "node"}),
    "mysql": frozenset({"sql"}),
    "node": frozenset({"javascript", "typescript"}),
    "postgresql": frozenset({"sql"}),
    "react": frozenset({"javascript", "typescript"}),
    "sql": frozenset({"postgresql", "mysql", "sqlite"}),
    "sqlite": frozenset({"sql"}),
    "typescript": frozenset({"javascript", "react", "vue", "angular", "node"}),
    "vue": frozenset({"javascript", "typescript"}),
}


@dataclass(frozen=True)
class _Fact:
    term: str
    message: str


def match_requirements(
    requirements: list[JobRequirement], candidate: Candidate
) -> list[RequirementMatch]:
    facts = _profile_facts(candidate)
    return [match_requirement(requirement, facts) for requirement in requirements]


def match_requirement(
    requirement: JobRequirement, facts: list[_Fact]
) -> RequirementMatch:
    strong = _strong_evidence(requirement, facts)
    if strong:
        classification = MatchClassification.STRONG_EVIDENCE
        evidence = strong
    else:
        transferable = _transferable_evidence(requirement, facts)
        if transferable:
            classification = MatchClassification.TRANSFERABLE
            evidence = transferable
        else:
            classification = MatchClassification.GAP
            evidence = []

    return RequirementMatch(
        job_id=requirement.job_id,
        requirement_id=requirement.id,
        requirement_name=requirement.name,
        category=requirement.category,
        importance=requirement.importance,
        classification=classification,
        evidence=evidence,
    )


def _profile_facts(candidate: Candidate) -> list[_Fact]:
    facts: list[_Fact] = []
    for skill in candidate.skills:
        facts.append(
            _Fact(
                term=_canonical(skill.name),
                message=f"{skill.name} listed as a candidate skill",
            )
        )
    for project in candidate.projects:
        for raw in _split_terms(project.technologies):
            facts.append(
                _Fact(
                    term=_canonical(raw),
                    message=f"{raw} used in {project.name}",
                )
            )
        if project.name:
            facts.append(
                _Fact(
                    term=_canonical(project.name),
                    message=f"Project {project.name}",
                )
            )
        if project.description:
            facts.append(
                _Fact(
                    term=_normalize(project.description),
                    message=f"{project.name} project description",
                )
            )
    for experience in candidate.experience:
        label = f"{experience.title} at {experience.company}"
        for raw in (experience.title, experience.company, experience.description or ""):
            if raw:
                facts.append(_Fact(term=_canonical(raw), message=f"{raw} from {label}"))
        if experience.description:
            facts.append(
                _Fact(
                    term=_normalize(experience.description),
                    message=f"{experience.title} at {experience.company}",
                )
            )
    for certification in candidate.certifications:
        facts.append(
            _Fact(
                term=_canonical(certification.name),
                message=f"{certification.name} listed as a certification",
            )
        )
    for education in candidate.education:
        for raw in (education.degree, education.field_of_study, education.institution):
            if raw:
                facts.append(
                    _Fact(
                        term=_canonical(raw),
                        message=f"{raw} from {education.institution}",
                    )
                )
    return facts


def _strong_evidence(requirement: JobRequirement, facts: list[_Fact]) -> list[str]:
    needles = _requirement_needles(requirement.name)
    evidence: list[str] = []
    seen: set[str] = set()
    for fact in facts:
        if any(_phrase_in(fact.term, needle) for needle in needles):
            if fact.message not in seen:
                seen.add(fact.message)
                evidence.append(fact.message)
    return evidence


def _transferable_evidence(requirement: JobRequirement, facts: list[_Fact]) -> list[str]:
    sources = set()
    for needle in _requirement_needles(requirement.name):
        sources.update(_TRANSFERABLE_SOURCES.get(needle, ()))
    if not sources:
        return []

    evidence: list[str] = []
    seen: set[str] = set()
    display = requirement.name
    for fact in facts:
        if any(_phrase_in(fact.term, source) for source in sources):
            message = f"{fact.message}, which may transfer to {display}"
            if message not in seen:
                seen.add(message)
                evidence.append(message)
    return evidence


def _requirement_needles(name: str) -> set[str]:
    needles = {_canonical(name)}
    terms = _significant_terms(name)
    if terms:
        needles.add(" ".join(terms))
        needles.update(terms)
    return {needle for needle in needles if needle}


def _significant_terms(name: str) -> list[str]:
    return [
        _ALIASES.get(token, token)
        for token in _normalize(name).split()
        if token not in _STOPWORDS and not token.isdigit() and len(token) > 1
    ]


def _canonical(value: str) -> str:
    normalized = _normalize(value)
    return _ALIASES.get(normalized, normalized)


def _normalize(value: str) -> str:
    lowered = value.lower()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def _split_terms(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _phrase_in(haystack: str, needle: str) -> bool:
    if not haystack or not needle:
        return False
    return re.search(rf"\b{re.escape(needle)}\b", haystack) is not None
