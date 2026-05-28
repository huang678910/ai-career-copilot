import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GenerateQuestionsRequest(BaseModel):
    jd_analysis_id: uuid.UUID | None = None
    resume_id: uuid.UUID | None = None
    question_count: int = Field(default=10, ge=1, le=30)


class InterviewQuestionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    jd_analysis_id: uuid.UUID | None = None
    resume_id: uuid.UUID | None = None
    question_type: str
    category: str | None = None
    question: str
    difficulty: str | None = None
    suggested_answer: str | None = None
    generation_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerationSummary(BaseModel):
    generation_id: uuid.UUID
    question_count: int
    created_at: datetime
    preview: str = ""


class CreateSessionRequest(BaseModel):
    session_type: str = Field(default="technical")
    questions_total: int = Field(default=10, ge=3, le=30)
    resume_id: str | None = Field(default=None)


class InterviewMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    message_type: str | None = None
    score: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InterviewSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    session_type: str
    status: str
    questions_asked: int
    questions_total: int
    overall_score: float | None = None
    feedback: dict | None = None
    started_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class InterviewSessionDetailResponse(InterviewSessionResponse):
    messages: list[InterviewMessageResponse] = []
