import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.ai.resume_agent import GuidedResumeAgent as ResumeAgent
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.resume import (
    EducationCreate,
    EducationResponse,
    EducationUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ResumeCreate,
    ResumeDetailResponse,
    ResumeResponse,
    ResumeUpdate,
    SkillCreate,
    SkillResponse,
    SkillUpdate,
    WorkExperienceCreate,
    WorkExperienceResponse,
    WorkExperienceUpdate,
)
from app.services.resume_service import ResumeService

router = APIRouter()


# --- Resume CRUD ---

@router.post("", response_model=ResumeResponse, status_code=201)
async def create_resume(
    request: ResumeCreate,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.create_resume(
        user_id=current_user.id,
        title=request.title,
        target_position=request.target_position,
        language=request.language,
    )


@router.get("", response_model=list[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.list_resumes(user_id=current_user.id)


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.get_resume(user_id=current_user.id, resume_id=resume_id)


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: uuid.UUID,
    request: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.update_resume(
        user_id=current_user.id,
        resume_id=resume_id,
        **request.model_dump(exclude_none=True),
    )


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    await service.delete_resume(user_id=current_user.id, resume_id=resume_id)


# --- Education ---

@router.post("/{resume_id}/education", response_model=EducationResponse, status_code=201)
async def add_education(
    resume_id: uuid.UUID,
    request: EducationCreate,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.add_education(
        user_id=current_user.id,
        resume_id=resume_id,
        data=request.model_dump(),
    )


@router.put("/{resume_id}/education/{edu_id}", response_model=EducationResponse)
async def update_education(
    resume_id: uuid.UUID,
    edu_id: uuid.UUID,
    request: EducationUpdate,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.update_education(
        user_id=current_user.id,
        resume_id=resume_id,
        edu_id=edu_id,
        data=request.model_dump(exclude_none=True),
    )


@router.delete("/{resume_id}/education/{edu_id}", status_code=204)
async def delete_education(
    resume_id: uuid.UUID,
    edu_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    await service.delete_education(user_id=current_user.id, resume_id=resume_id, edu_id=edu_id)


# --- Work Experience ---

@router.post("/{resume_id}/experience", response_model=WorkExperienceResponse, status_code=201)
async def add_experience(
    resume_id: uuid.UUID,
    request: WorkExperienceCreate,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.add_experience(
        user_id=current_user.id,
        resume_id=resume_id,
        data=request.model_dump(),
    )


@router.put("/{resume_id}/experience/{exp_id}", response_model=WorkExperienceResponse)
async def update_experience(
    resume_id: uuid.UUID,
    exp_id: uuid.UUID,
    request: WorkExperienceUpdate,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.update_experience(
        user_id=current_user.id,
        resume_id=resume_id,
        exp_id=exp_id,
        data=request.model_dump(exclude_none=True),
    )


@router.delete("/{resume_id}/experience/{exp_id}", status_code=204)
async def delete_experience(
    resume_id: uuid.UUID,
    exp_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    await service.delete_experience(user_id=current_user.id, resume_id=resume_id, exp_id=exp_id)


# --- Projects ---

@router.post("/{resume_id}/projects", response_model=ProjectResponse, status_code=201)
async def add_project(
    resume_id: uuid.UUID,
    request: ProjectCreate,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.add_project(
        user_id=current_user.id,
        resume_id=resume_id,
        data=request.model_dump(),
    )


@router.put("/{resume_id}/projects/{proj_id}", response_model=ProjectResponse)
async def update_project(
    resume_id: uuid.UUID,
    proj_id: uuid.UUID,
    request: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.update_project(
        user_id=current_user.id,
        resume_id=resume_id,
        proj_id=proj_id,
        data=request.model_dump(exclude_none=True),
    )


@router.delete("/{resume_id}/projects/{proj_id}", status_code=204)
async def delete_project(
    resume_id: uuid.UUID,
    proj_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    await service.delete_project(user_id=current_user.id, resume_id=resume_id, proj_id=proj_id)


# --- Skills ---

@router.post("/{resume_id}/skills", response_model=SkillResponse, status_code=201)
async def add_skill(
    resume_id: uuid.UUID,
    request: SkillCreate,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.add_skill(
        user_id=current_user.id,
        resume_id=resume_id,
        data=request.model_dump(),
    )


@router.put("/{resume_id}/skills/{skill_id}", response_model=SkillResponse)
async def update_skill(
    resume_id: uuid.UUID,
    skill_id: uuid.UUID,
    request: SkillUpdate,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    return await service.update_skill(
        user_id=current_user.id,
        resume_id=resume_id,
        skill_id=skill_id,
        data=request.model_dump(exclude_none=True),
    )


@router.delete("/{resume_id}/skills/{skill_id}", status_code=204)
async def delete_skill(
    resume_id: uuid.UUID,
    skill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    await service.delete_skill(user_id=current_user.id, resume_id=resume_id, skill_id=skill_id)


# --- AI Tools ---

_star_agent = ResumeAgent()
_highlight_agent = ResumeAgent()


class STARRequest(BaseModel):
    description: str = Field(min_length=10)


class HighlightRequest(BaseModel):
    project_name: str = Field(min_length=1)
    description: str = Field(min_length=10)


@router.post("/ai/star")
async def generate_star(
    request: STARRequest,
    current_user: User = Depends(get_current_user),
):
    result = _star_agent.generate_star(request.description)
    return {"result": result}


@router.post("/ai/highlights")
async def extract_highlights(
    request: HighlightRequest,
    current_user: User = Depends(get_current_user),
):
    result = _highlight_agent.extract_highlights(request.project_name, request.description)
    return {"result": result}


# --- Resume Import ---

from fastapi import File, UploadFile
from app.utils.file_parser import parse_pdf, parse_docx, extract_resume_structure
from datetime import date as date_type


def _clean_date(value: str | None) -> date_type | None:
    """Convert AI-extracted date strings to Python date objects. Returns None if unparseable."""
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    if value.lower() in ("present", "至今", "now", "current", ""):
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y", "%Y/%m/%d", "%Y/%m", "%Y年%m月%d日", "%Y年%m月", "%Y年"):
        try:
            from datetime import datetime
            dt = datetime.strptime(value, fmt)
            return dt.date()
        except ValueError:
            continue
    return None


def _clean_dates_in_dict(data: dict) -> dict:
    """Convert string dates in a dict to Python date objects."""
    for key in ("start_date", "end_date"):
        if key in data and isinstance(data[key], str):
            data[key] = _clean_date(data[key])
    return data


@router.post("/import", response_model=ResumeDetailResponse, status_code=201)
async def import_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
    if file.content_type not in allowed_types:
        from app.core.exceptions import AppException
        raise AppException(400, "不支持的文件格式，请上传 PDF、DOCX 或 TXT 文件")

    content = await file.read()

    # Parse file based on type
    if file.content_type == "application/pdf":
        raw_text = parse_pdf(content)
    elif "docx" in file.content_type or "word" in file.content_type:
        raw_text = parse_docx(content)
    else:
        raw_text = content.decode("utf-8", errors="ignore")

    if not raw_text.strip():
        from app.core.exceptions import AppException
        raise AppException(400, "无法从文件中提取文本内容")

    # Use AI to extract structured data
    extracted = extract_resume_structure(raw_text)

    # Create resume with extracted data
    resume = await service.create_resume(
        user_id=current_user.id,
        title=extracted.get("target_position", "") or "导入的简历",
        target_position=extracted.get("target_position", ""),
    )

    # Add education
    for edu in extracted.get("education", [])[:5]:
        if edu.get("school") and edu.get("major"):
            await service.add_education(current_user.id, resume.id, _clean_dates_in_dict(edu))

    # Add work experiences
    for exp in extracted.get("work_experiences", [])[:10]:
        if exp.get("company") and exp.get("title"):
            await service.add_experience(current_user.id, resume.id, _clean_dates_in_dict(exp))

    # Add projects
    for proj in extracted.get("projects", [])[:10]:
        if proj.get("name"):
            await service.add_project(current_user.id, resume.id, _clean_dates_in_dict(proj))

    # Add skills
    for skill in extracted.get("skills", [])[:20]:
        if skill.get("name"):
            await service.add_skill(current_user.id, resume.id, skill)

    # Update basic info and summary
    basic_info = {
        "name": extracted.get("name", ""),
        "email": extracted.get("email", ""),
        "phone": extracted.get("phone", ""),
    }
    await service.update_resume(current_user.id, resume.id, basic_info=basic_info, summary=extracted.get("summary", ""))

    return await service.get_resume(current_user.id, resume.id)


# --- Chat History ---

from app.models.resume_chat import ResumeChatMessage
from pydantic import BaseModel as PydanticBaseModel, Field as PydanticField


class ChatMessageCreate(PydanticBaseModel):
    role: str
    content: str


class ChatMessageResponse(PydanticBaseModel):
    id: uuid.UUID
    resume_id: uuid.UUID
    role: str
    content: str
    created_at: str

    model_config = {"from_attributes": True}


@router.get("/{resume_id}/chat-history", response_model=list[ChatMessageResponse])
async def get_chat_history(
    resume_id: uuid.UUID,
    start_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    # Verify resume belongs to user
    await service.get_resume(current_user.id, resume_id)
    query = select(ResumeChatMessage).where(ResumeChatMessage.resume_id == resume_id)
    if start_id:
        # Load from start_id onwards (single conversation)
        query = query.where(ResumeChatMessage.id >= start_id)
    query = query.order_by(ResumeChatMessage.created_at.asc()).limit(200 if start_id else 500)
    result = await service.db.execute(query)
    messages = result.scalars().all()

    # When loading a specific conversation, stop at the first time gap > 30 min
    if start_id and len(messages) > 1:
        from datetime import timedelta
        filtered = [messages[0]]
        for i in range(1, len(messages)):
            if messages[i].created_at - messages[i-1].created_at > timedelta(minutes=30):
                break
            filtered.append(messages[i])
        messages = filtered

    return [
        ChatMessageResponse(
            id=m.id, resume_id=m.resume_id, role=m.role,
            content=m.content, created_at=m.created_at.isoformat()
        )
        for m in messages
    ]


@router.post("/{resume_id}/chat-history", status_code=201)
async def save_chat_message(
    resume_id: uuid.UUID,
    request: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
):
    from app.core.database import async_session
    async with async_session() as db:
        msg = ResumeChatMessage(
            resume_id=resume_id, user_id=current_user.id,
            role=request.role, content=request.content,
        )
        db.add(msg)
        await db.commit()
    return {"status": "ok"}


@router.delete("/{resume_id}/chat-history", status_code=204)
async def clear_chat_history(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    # Verify resume belongs to user
    from app.core.database import async_session
    async with async_session() as db:
        result = await db.execute(
            select(ResumeChatMessage).where(ResumeChatMessage.resume_id == resume_id)
        )
        for msg in result.scalars().all():
            await db.delete(msg)
        await db.commit()


@router.get("/{resume_id}/chat-conversations")
async def get_chat_conversations(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    """Group chat messages into conversations by time gap (>30 min = new conversation)."""
    await service.get_resume(current_user.id, resume_id)
    result = await service.db.execute(
        select(ResumeChatMessage)
        .where(ResumeChatMessage.resume_id == resume_id)
        .order_by(ResumeChatMessage.created_at.asc())
    )
    messages = result.scalars().all()

    if not messages:
        return []

    from datetime import timedelta
    conversations = []
    current_group = []
    group_start = messages[0]

    for msg in messages:
        if current_group and (msg.created_at - current_group[-1].created_at) > timedelta(minutes=30):
            conversations.append(_build_conversation(current_group))
            current_group = []
        current_group.append(msg)

    if current_group:
        conversations.append(_build_conversation(current_group))

    return conversations


def _build_conversation(msgs: list) -> dict:
    first = msgs[0]
    last = msgs[-1]
    preview = first.content[:80] + ("..." if len(first.content) > 80 else "")
    return {
        "id": str(first.id),  # Use first message ID as conversation key
        "first_message": preview,
        "message_count": len(msgs),
        "started_at": first.created_at.isoformat(),
        "last_message_at": last.created_at.isoformat(),
    }
