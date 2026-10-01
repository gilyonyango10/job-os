from uuid import UUID

from sqlalchemy.orm import Session

from app.models.requirement import RequirementImportance
from app.schemas.analysis import JobAnalysis, MatchClassification, RequirementMatch
from app.schemas.job import JobRead
from app.schemas.requirement import RequirementRead
from app.services.jobs import get_job
from app.services.matching import match_requirements
from app.services.profile import get_profile
from app.services.requirements import list_requirements


def analyze_job(db: Session, job_id: UUID) -> JobAnalysis | None:
    job = get_job(db, job_id)
    if job is None:
        return None

    requirements = list_requirements(db, job_id) or []
    profile = get_profile(db)
    matches = match_requirements(requirements, profile)
    return _build_analysis(job, requirements, matches)


def _build_analysis(job, requirements, matches: list[RequirementMatch]) -> JobAnalysis:
    gaps = [match for match in matches if match.classification == MatchClassification.GAP]
    return JobAnalysis(
        job=JobRead.model_validate(job),
        requirements=[RequirementRead.model_validate(item) for item in requirements],
        strong_evidence=[
            match
            for match in matches
            if match.classification == MatchClassification.STRONG_EVIDENCE
        ],
        transferable=[
            match
            for match in matches
            if match.classification == MatchClassification.TRANSFERABLE
        ],
        gaps=gaps,
        required_gaps=[
            match for match in gaps if match.importance == RequirementImportance.REQUIRED
        ],
        preferred_gaps=[
            match for match in gaps if match.importance == RequirementImportance.PREFERRED
        ],
    )
