from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.errors import EmptyJobDescription
from app.ai.factory import get_ai_provider
from app.schemas.requirement import ExtractRequirementsResponse
from app.services.extraction import RequirementExtractor
from app.services.jobs import get_job
from app.services.requirements import persist_extracted_requirements


def extract_requirements_for_job(
    db: Session,
    job_id: UUID,
    extractor: RequirementExtractor | None = None,
) -> ExtractRequirementsResponse | None:
    job = get_job(db, job_id)
    if job is None:
        return None
    if not job.description.strip():
        raise EmptyJobDescription(
            "This job has no description to extract requirements from."
        )
    if extractor is None:
        extractor = RequirementExtractor(get_ai_provider())
    extracted = extractor.extract(job.description)
    return persist_extracted_requirements(db, job.id, extracted)
