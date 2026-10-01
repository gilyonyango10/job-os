from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.requirement import RequirementCategory, RequirementImportance
from app.schemas.job import JobRead
from app.schemas.requirement import RequirementRead


class MatchClassification(str, Enum):
    STRONG_EVIDENCE = "STRONG_EVIDENCE"
    TRANSFERABLE = "TRANSFERABLE"
    GAP = "GAP"


class RequirementMatch(BaseModel):
    job_id: UUID
    requirement_id: UUID
    requirement_name: str
    category: RequirementCategory
    importance: RequirementImportance
    classification: MatchClassification
    evidence: list[str] = Field(default_factory=list)


class JobAnalysis(BaseModel):
    job: JobRead
    requirements: list[RequirementRead]
    strong_evidence: list[RequirementMatch]
    transferable: list[RequirementMatch]
    gaps: list[RequirementMatch]
    required_gaps: list[RequirementMatch]
    preferred_gaps: list[RequirementMatch]
