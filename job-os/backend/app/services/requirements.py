from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.requirement import JobRequirement
from app.schemas.requirement import RequirementWrite
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


def _owned_requirement(
    db: Session, job_id: UUID, requirement_id: UUID
) -> JobRequirement | None:
    if get_job(db, job_id) is None:
        return None
    item = db.get(JobRequirement, requirement_id)
    if item is None or item.job_id != job_id:
        return None
    return item
