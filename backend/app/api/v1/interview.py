import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.interview import (
    CreateSessionRequest,
    GenerateQuestionsRequest,
    GenerationSummary,
    InterviewQuestionResponse,
    InterviewSessionDetailResponse,
    InterviewSessionResponse,
)
from app.services.interview_service import InterviewService

router = APIRouter()


# --- Questions ---

@router.post("/questions/generate", response_model=list[InterviewQuestionResponse], status_code=201)
async def generate_questions(
    request: GenerateQuestionsRequest,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(InterviewService),
):
    return await service.generate_questions(
        user_id=current_user.id,
        jd_analysis_id=request.jd_analysis_id,
        resume_id=request.resume_id,
        count=request.question_count,
    )


@router.get("/questions", response_model=list[InterviewQuestionResponse])
async def list_questions(
    generation_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(InterviewService),
):
    return await service.list_questions(user_id=current_user.id, generation_id=generation_id)


@router.get("/questions/generations", response_model=list[GenerationSummary])
async def list_generations(
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(InterviewService),
):
    return await service.list_generations(user_id=current_user.id)


@router.get("/questions/{question_id}", response_model=InterviewQuestionResponse)
async def get_question(
    question_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(InterviewService),
):
    return await service.get_question(user_id=current_user.id, question_id=question_id)


@router.delete("/questions/{question_id}", status_code=204)
async def delete_question(
    question_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(InterviewService),
):
    await service.delete_question(user_id=current_user.id, question_id=question_id)


# --- Sessions ---

@router.post("/sessions", response_model=InterviewSessionResponse, status_code=201)
async def create_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(InterviewService),
):
    resume_id = uuid.UUID(request.resume_id) if request.resume_id else None
    session = await service.create_session(
        user_id=current_user.id,
        session_type=request.session_type,
        questions_total=request.questions_total,
        resume_id=resume_id,
    )
    # Attach resume data for WebSocket to use
    session._resume_data = getattr(session, '_resume_data', None)
    return session


@router.get("/sessions", response_model=list[InterviewSessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(InterviewService),
):
    return await service.list_sessions(user_id=current_user.id)


@router.get("/sessions/{session_id}", response_model=InterviewSessionDetailResponse)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(InterviewService),
):
    return await service.get_session(user_id=current_user.id, session_id=session_id)


@router.post("/sessions/{session_id}/end", response_model=InterviewSessionResponse)
async def end_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(InterviewService),
):
    return await service.end_session(user_id=current_user.id, session_id=session_id)


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(InterviewService),
):
    await service.delete_session(user_id=current_user.id, session_id=session_id)
