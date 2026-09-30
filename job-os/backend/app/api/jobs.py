from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job import JobCreate, JobRead
from app.services import jobs as jobs_service

router = APIRouter(tags=["jobs"])


@router.post("/jobs", status_code=status.HTTP_201_CREATED, response_model=JobRead)
def create_job(payload: JobCreate, db: Session = Depends(get_db)) -> JobRead:
    job = jobs_service.create_job(db, payload)
    return JobRead.model_validate(job)


@router.get("/jobs", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[JobRead]:
    jobs = jobs_service.list_jobs(db)
    return [JobRead.model_validate(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> JobRead:
    job = jobs_service.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobRead.model_validate(job)
