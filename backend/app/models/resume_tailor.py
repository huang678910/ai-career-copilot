import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class TailoredResume(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tailored_resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    source_resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    jd_analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jd_analysis.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    optimized_content: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    skill_gaps: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    tailoring_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
