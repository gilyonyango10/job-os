from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.requirement import RequirementCategory, RequirementImportance


class RequirementWrite(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: RequirementCategory = RequirementCategory.OTHER
    importance: RequirementImportance = RequirementImportance.REQUIRED
    description: str | None = None


class RequirementRead(RequirementWrite):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
