from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.candidate import (
    Candidate,
    Certification,
    Education,
    Experience,
    Project,
    Skill,
)
from app.schemas.candidate import (
    CandidateUpdate,
    CertificationWrite,
    EducationWrite,
    ExperienceWrite,
    ProjectWrite,
    SkillWrite,
)

_PROFILE_LOAD_OPTIONS = (
    selectinload(Candidate.education),
    selectinload(Candidate.experience),
    selectinload(Candidate.skills),
    selectinload(Candidate.projects),
    selectinload(Candidate.certifications),
)


def get_profile(db: Session) -> Candidate:
    statement = select(Candidate).options(*_PROFILE_LOAD_OPTIONS).limit(1)
    candidate = db.scalar(statement)
    if candidate is not None:
        return candidate

    candidate = Candidate(full_name="")
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return get_profile(db)


def update_profile(db: Session, payload: CandidateUpdate) -> Candidate:
    candidate = get_profile(db)
    candidate.full_name = payload.full_name
    candidate.email = payload.email
    candidate.location = payload.location
    candidate.professional_summary = payload.professional_summary
    db.commit()
    return get_profile(db)


def add_education(db: Session, payload: EducationWrite) -> Education:
    candidate = get_profile(db)
    item = Education(candidate_id=candidate.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_education(db: Session, item_id: UUID, payload: EducationWrite) -> Education | None:
    item = _owned_item(db, Education, item_id)
    if item is None:
        return None
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_education(db: Session, item_id: UUID) -> bool:
    return _delete_owned_item(db, Education, item_id)


def add_experience(db: Session, payload: ExperienceWrite) -> Experience:
    candidate = get_profile(db)
    item = Experience(candidate_id=candidate.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_experience(
    db: Session, item_id: UUID, payload: ExperienceWrite
) -> Experience | None:
    item = _owned_item(db, Experience, item_id)
    if item is None:
        return None
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_experience(db: Session, item_id: UUID) -> bool:
    return _delete_owned_item(db, Experience, item_id)


def add_skill(db: Session, payload: SkillWrite) -> Skill:
    candidate = get_profile(db)
    item = Skill(candidate_id=candidate.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_skill(db: Session, item_id: UUID, payload: SkillWrite) -> Skill | None:
    item = _owned_item(db, Skill, item_id)
    if item is None:
        return None
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_skill(db: Session, item_id: UUID) -> bool:
    return _delete_owned_item(db, Skill, item_id)


def add_project(db: Session, payload: ProjectWrite) -> Project:
    candidate = get_profile(db)
    item = Project(candidate_id=candidate.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_project(db: Session, item_id: UUID, payload: ProjectWrite) -> Project | None:
    item = _owned_item(db, Project, item_id)
    if item is None:
        return None
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_project(db: Session, item_id: UUID) -> bool:
    return _delete_owned_item(db, Project, item_id)


def add_certification(db: Session, payload: CertificationWrite) -> Certification:
    candidate = get_profile(db)
    item = Certification(candidate_id=candidate.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_certification(
    db: Session, item_id: UUID, payload: CertificationWrite
) -> Certification | None:
    item = _owned_item(db, Certification, item_id)
    if item is None:
        return None
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_certification(db: Session, item_id: UUID) -> bool:
    return _delete_owned_item(db, Certification, item_id)


def _owned_item[T](db: Session, model: type[T], item_id: UUID) -> T | None:
    candidate = get_profile(db)
    item = db.get(model, item_id)
    if item is None or getattr(item, "candidate_id") != candidate.id:
        return None
    return item


def _delete_owned_item[T](db: Session, model: type[T], item_id: UUID) -> bool:
    item = _owned_item(db, model, item_id)
    if item is None:
        return False
    db.delete(item)
    db.commit()
    return True
