import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class JDAnalysis(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "jd_analysis"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    tech_stack: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    implicit_requirements: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    difficulty_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_flags: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    company_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
