import uuid
from datetime import datetime

from pydantic import BaseModel


class TailorRequest(BaseModel):
    source_resume_id: uuid.UUID
    jd_analysis_id: uuid.UUID


class TailoredResumeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    source_resume_id: uuid.UUID
    jd_analysis_id: uuid.UUID
    version: int
    match_score: float | None = None
    optimized_content: dict | None = None
    skill_gaps: list | None = None
    tailoring_notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
