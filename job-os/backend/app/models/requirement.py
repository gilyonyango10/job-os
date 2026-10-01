import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.job import Job


class RequirementCategory(str, enum.Enum):
    SKILL = "skill"
    TECHNOLOGY = "technology"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    RESPONSIBILITY = "responsibility"
    CERTIFICATION = "certification"
    OTHER = "other"


class RequirementImportance(str, enum.Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[RequirementCategory] = mapped_column(
        Enum(RequirementCategory, name="requirement_category", native_enum=False, length=32),
        nullable=False,
        default=RequirementCategory.OTHER,
    )
    importance: Mapped[RequirementImportance] = mapped_column(
        Enum(
            RequirementImportance,
            name="requirement_importance",
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=RequirementImportance.REQUIRED,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    job: Mapped[Job] = relationship(back_populates="requirements")
