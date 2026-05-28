import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class JDAnalysisRequest(BaseModel):
    raw_text: str = Field(min_length=10, max_length=10000)


class JDAnalysisResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    raw_text: str
    tech_stack: dict | None = None
    keywords: list | None = None
    implicit_requirements: list | None = None
    difficulty_score: int | None = None
    risk_flags: list | None = None
    risk_score: int | None = None
    position_title: str | None = None
    company_type: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
