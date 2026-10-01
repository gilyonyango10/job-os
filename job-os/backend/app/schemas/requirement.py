from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.requirement import RequirementCategory, RequirementImportance


class RequirementWrite(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: RequirementCategory = RequirementCategory.OTHER
    importance: RequirementImportance = RequirementImportance.REQUIRED
    description: str | None = None
    evidence_text: str | None = None


class RequirementRead(RequirementWrite):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID


class ExtractedRequirement(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: RequirementCategory
    importance: RequirementImportance
    description: str | None = None
    evidence_text: str = Field(min_length=1)


class ExtractionPayload(BaseModel):
    requirements: list[ExtractedRequirement]


class ExtractRequirementsResponse(BaseModel):
    requirements: list[RequirementRead]
    created_count: int
    skipped_duplicate_count: int

