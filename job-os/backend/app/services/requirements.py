from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.requirement import JobRequirement
from app.schemas.requirement import (
    ExtractedRequirement,
    ExtractRequirementsResponse,
    RequirementRead,
    RequirementWrite,
)
from app.services.extraction import requirement_key
from app.services.jobs import get_job


def list_requirements(db: Session, job_id: UUID) -> list[JobRequirement] | None:
    if get_job(db, job_id) is None:
        return None
    statement = (
        select(JobRequirement)
        .where(JobRequirement.job_id == job_id)
        .order_by(JobRequirement.name.asc())
    )
    return list(db.scalars(statement).all())


def create_requirement(
    db: Session, job_id: UUID, payload: RequirementWrite
) -> JobRequirement | None:
    job = db.get(Job, job_id)
    if job is None:
        return None
    item = JobRequirement(job_id=job.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_requirement(
    db: Session, job_id: UUID, requirement_id: UUID, payload: RequirementWrite
) -> JobRequirement | None:
    item = _owned_requirement(db, job_id, requirement_id)
    if item is None:
        return None
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_requirement(db: Session, job_id: UUID, requirement_id: UUID) -> bool:
    item = _owned_requirement(db, job_id, requirement_id)
    if item is None:
        return False
    db.delete(item)
    db.commit()
    return True


def persist_extracted_requirements(
    db: Session, job_id: UUID, extracted: list[ExtractedRequirement]
) -> ExtractRequirementsResponse:
    existing = list_requirements(db, job_id) or []
    seen = {requirement_key(item) for item in existing}
    created: list[JobRequirement] = []
    skipped = 0
    for item in extracted:
        if requirement_key(item) in seen:
            skipped += 1
            continue
        record = create_requirement(
            db,
            job_id,
            RequirementWrite(
                name=item.name,
                category=item.category,
                importance=item.importance,
                description=item.description,
                evidence_text=item.evidence_text,
            ),
        )
        if record is None:
            continue
        created.append(record)
        seen.add(requirement_key(record))
    current = list_requirements(db, job_id) or []
    return ExtractRequirementsResponse(
        requirements=[RequirementRead.model_validate(item) for item in current],
        created_count=len(created),
        skipped_duplicate_count=skipped,
    )


def _owned_requirement(
    db: Session, job_id: UUID, requirement_id: UUID
) -> JobRequirement | None:
    if get_job(db, job_id) is None:
        return None
    item = db.get(JobRequirement, requirement_id)
    if item is None or item.job_id != job_id:
        return None
    return item
