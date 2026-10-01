from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analysis import JobAnalysis
from app.schemas.requirement import (
    ExtractRequirementsResponse,
    RequirementRead,
    RequirementWrite,
)
from app.services import analysis as analysis_service
from app.services import extract_job as extract_job_service
from app.services import requirements as requirements_service

router = APIRouter(tags=["requirements"])


@router.post(
    "/jobs/{job_id}/requirements",
    status_code=status.HTTP_201_CREATED,
    response_model=RequirementRead,
)
def create_requirement(
    job_id: UUID, payload: RequirementWrite, db: Session = Depends(get_db)
) -> RequirementRead:
    item = requirements_service.create_requirement(db, job_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return RequirementRead.model_validate(item)


@router.get("/jobs/{job_id}/requirements", response_model=list[RequirementRead])
def list_requirements(job_id: UUID, db: Session = Depends(get_db)) -> list[RequirementRead]:
    items = requirements_service.list_requirements(db, job_id)
    if items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return [RequirementRead.model_validate(item) for item in items]


@router.put(
    "/jobs/{job_id}/requirements/{requirement_id}",
    response_model=RequirementRead,
)
def update_requirement(
    job_id: UUID,
    requirement_id: UUID,
    payload: RequirementWrite,
    db: Session = Depends(get_db),
) -> RequirementRead:
    item = requirements_service.update_requirement(db, job_id, requirement_id, payload)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found"
        )
    return RequirementRead.model_validate(item)


@router.delete(
    "/jobs/{job_id}/requirements/{requirement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_requirement(
    job_id: UUID, requirement_id: UUID, db: Session = Depends(get_db)
) -> Response:
    if not requirements_service.delete_requirement(db, job_id, requirement_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/jobs/{job_id}/extract-requirements",
    response_model=ExtractRequirementsResponse,
)
def extract_requirements(
    job_id: UUID, db: Session = Depends(get_db)
) -> ExtractRequirementsResponse:
    result = extract_job_service.extract_requirements_for_job(db, job_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return result


@router.get("/jobs/{job_id}/analysis", response_model=JobAnalysis)
def analyze_job(job_id: UUID, db: Session = Depends(get_db)) -> JobAnalysis:
    analysis = analysis_service.analyze_job(db, job_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return analysis
