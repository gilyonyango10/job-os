from datetime import date as Date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CandidateUpdate(BaseModel):
    full_name: str = Field(default="", max_length=255)
    email: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    professional_summary: str | None = None


class EducationWrite(BaseModel):
    institution: str = Field(min_length=1, max_length=255)
    degree: str | None = Field(default=None, max_length=255)
    field_of_study: str | None = Field(default=None, max_length=255)
    start_date: Date | None = None
    end_date: Date | None = None


class ExperienceWrite(BaseModel):
    company: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=255)
    start_date: Date | None = None
    end_date: Date | None = None
    description: str | None = None


class SkillWrite(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=100)


class ProjectWrite(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    technologies: str | None = None


class CertificationWrite(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    issuer: str | None = Field(default=None, max_length=255)
    date: Date | None = None


class EducationRead(EducationWrite):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID


class ExperienceRead(ExperienceWrite):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID


class SkillRead(SkillWrite):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID


class ProjectRead(ProjectWrite):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID


class CertificationRead(CertificationWrite):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID


class CandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: str | None
    location: str | None
    professional_summary: str | None
    education: list[EducationRead] = Field(default_factory=list)
    experience: list[ExperienceRead] = Field(default_factory=list)
    skills: list[SkillRead] = Field(default_factory=list)
    projects: list[ProjectRead] = Field(default_factory=list)
    certifications: list[CertificationRead] = Field(default_factory=list)
