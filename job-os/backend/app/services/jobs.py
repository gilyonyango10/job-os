from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import JobCreate


def create_job(db: Session, payload: JobCreate) -> Job:
    job = Job(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(db: Session) -> list[Job]:
    statement = select(Job).order_by(Job.created_at.desc())
    return list(db.scalars(statement).all())


def get_job(db: Session, job_id: UUID) -> Job | None:
    return db.get(Job, job_id)
