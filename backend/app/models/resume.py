import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Resume(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    basic_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_position: Mapped[str | None] = mapped_column(String(200), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="zh", nullable=False)
    guided_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    education: Mapped[list["ResumeEducation"]] = relationship(
        "ResumeEducation", back_populates="resume", cascade="all, delete-orphan"
    )
    work_experiences: Mapped[list["ResumeWorkExperience"]] = relationship(
        "ResumeWorkExperience", back_populates="resume", cascade="all, delete-orphan"
    )
    projects: Mapped[list["ResumeProject"]] = relationship(
        "ResumeProject", back_populates="resume", cascade="all, delete-orphan"
    )
    skills: Mapped[list["ResumeSkill"]] = relationship(
        "ResumeSkill", back_populates="resume", cascade="all, delete-orphan"
    )


class ResumeEducation(Base, UUIDMixin):
    __tablename__ = "resume_education"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    school: Mapped[str] = mapped_column(String(200), nullable=False)
    degree: Mapped[str | None] = mapped_column(String(100), nullable=True)
    major: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gpa: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    resume: Mapped["Resume"] = relationship("Resume", back_populates="education")


class ResumeWorkExperience(Base, UUIDMixin):
    __tablename__ = "resume_work_experience"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlights: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    resume: Mapped["Resume"] = relationship("Resume", back_populates="work_experiences")


class ResumeProject(Base, UUIDMixin):
    __tablename__ = "resume_projects"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str | None] = mapped_column(String(200), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlights: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    tech_stack: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    project_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    resume: Mapped["Resume"] = relationship("Resume", back_populates="projects")


class ResumeSkill(Base, UUIDMixin):
    __tablename__ = "resume_skills"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[str | None] = mapped_column(String(20), nullable=True)

    resume: Mapped["Resume"] = relationship("Resume", back_populates="skills")
