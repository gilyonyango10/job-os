from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.job import JobStatus


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str = Field(min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    description: str = Field(min_length=1)
    source: str = Field(default="manual", min_length=1, max_length=100)
    source_url: str | None = Field(default=None, max_length=2048)
    status: JobStatus = JobStatus.DISCOVERED


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    company: str
    location: str | None
    description: str
    source: str
    source_url: str | None
    status: JobStatus
    created_at: datetime
