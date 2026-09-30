from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.candidate import (
    CandidateRead,
    CandidateUpdate,
    CertificationRead,
    CertificationWrite,
    EducationRead,
    EducationWrite,
    ExperienceRead,
    ExperienceWrite,
    ProjectRead,
    ProjectWrite,
    SkillRead,
    SkillWrite,
)
from app.services import profile as profile_service

router = APIRouter(tags=["profile"])


@router.get("/profile", response_model=CandidateRead)
def get_profile(db: Session = Depends(get_db)) -> CandidateRead:
    candidate = profile_service.get_profile(db)
    return CandidateRead.model_validate(candidate)


@router.put("/profile", response_model=CandidateRead)
def update_profile(
    payload: CandidateUpdate, db: Session = Depends(get_db)
) -> CandidateRead:
    candidate = profile_service.update_profile(db, payload)
    return CandidateRead.model_validate(candidate)


@router.post(
    "/profile/education",
    status_code=status.HTTP_201_CREATED,
    response_model=EducationRead,
)
def add_education(
    payload: EducationWrite, db: Session = Depends(get_db)
) -> EducationRead:
    item = profile_service.add_education(db, payload)
    return EducationRead.model_validate(item)


@router.put("/profile/education/{item_id}", response_model=EducationRead)
def update_education(
    item_id: UUID, payload: EducationWrite, db: Session = Depends(get_db)
) -> EducationRead:
    item = profile_service.update_education(db, item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")
    return EducationRead.model_validate(item)


@router.delete("/profile/education/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(item_id: UUID, db: Session = Depends(get_db)) -> Response:
    if not profile_service.delete_education(db, item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/profile/experience",
    status_code=status.HTTP_201_CREATED,
    response_model=ExperienceRead,
)
def add_experience(
    payload: ExperienceWrite, db: Session = Depends(get_db)
) -> ExperienceRead:
    item = profile_service.add_experience(db, payload)
    return ExperienceRead.model_validate(item)


@router.put("/profile/experience/{item_id}", response_model=ExperienceRead)
def update_experience(
    item_id: UUID, payload: ExperienceWrite, db: Session = Depends(get_db)
) -> ExperienceRead:
    item = profile_service.update_experience(db, item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
    return ExperienceRead.model_validate(item)


@router.delete("/profile/experience/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(item_id: UUID, db: Session = Depends(get_db)) -> Response:
    if not profile_service.delete_experience(db, item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/profile/skills",
    status_code=status.HTTP_201_CREATED,
    response_model=SkillRead,
)
def add_skill(payload: SkillWrite, db: Session = Depends(get_db)) -> SkillRead:
    item = profile_service.add_skill(db, payload)
    return SkillRead.model_validate(item)


@router.put("/profile/skills/{item_id}", response_model=SkillRead)
def update_skill(
    item_id: UUID, payload: SkillWrite, db: Session = Depends(get_db)
) -> SkillRead:
    item = profile_service.update_skill(db, item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return SkillRead.model_validate(item)


@router.delete("/profile/skills/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(item_id: UUID, db: Session = Depends(get_db)) -> Response:
    if not profile_service.delete_skill(db, item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/profile/projects",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectRead,
)
def add_project(payload: ProjectWrite, db: Session = Depends(get_db)) -> ProjectRead:
    item = profile_service.add_project(db, payload)
    return ProjectRead.model_validate(item)


@router.put("/profile/projects/{item_id}", response_model=ProjectRead)
def update_project(
    item_id: UUID, payload: ProjectWrite, db: Session = Depends(get_db)
) -> ProjectRead:
    item = profile_service.update_project(db, item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectRead.model_validate(item)


@router.delete("/profile/projects/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(item_id: UUID, db: Session = Depends(get_db)) -> Response:
    if not profile_service.delete_project(db, item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/profile/certifications",
    status_code=status.HTTP_201_CREATED,
    response_model=CertificationRead,
)
def add_certification(
    payload: CertificationWrite, db: Session = Depends(get_db)
) -> CertificationRead:
    item = profile_service.add_certification(db, payload)
    return CertificationRead.model_validate(item)


@router.put("/profile/certifications/{item_id}", response_model=CertificationRead)
def update_certification(
    item_id: UUID, payload: CertificationWrite, db: Session = Depends(get_db)
) -> CertificationRead:
    item = profile_service.update_certification(db, item_id, payload)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Certification not found"
        )
    return CertificationRead.model_validate(item)


@router.delete("/profile/certifications/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certification(item_id: UUID, db: Session = Depends(get_db)) -> Response:
    if not profile_service.delete_certification(db, item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Certification not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
