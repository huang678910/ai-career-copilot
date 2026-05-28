import os
import uuid
import logging
from io import BytesIO
from typing import List, Optional

from pydantic import BaseModel as PydanticModel, Field
from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import FileResponse, StreamingResponse

from app.api.deps import get_current_user
from app.models.user import User
from app.services.resume_service import ResumeService

logger = logging.getLogger(__name__)

_pdf_fonts_registered = False


def _register_pdf_fonts() -> None:
    """Register Chinese fonts with ReportLab so xhtml2pdf can render CJK text."""
    global _pdf_fonts_registered
    if _pdf_fonts_registered:
        return
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        # Common CJK font locations on Windows / Linux / macOS
        candidates = [
            # Windows
            ("C:/Windows/Fonts/msyh.ttc", "Microsoft YaHei"),
            ("C:/Windows/Fonts/simsun.ttc", "SimSun"),
            # Linux
            ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", "WenQuanYi Micro Hei"),
            ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "Noto Sans CJK SC"),
            # macOS
            ("/System/Library/Fonts/PingFang.ttc", "PingFang SC"),
            ("/Library/Fonts/Arial Unicode.ttf", "Arial Unicode MS"),
        ]
        for path, name in candidates:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont(name, path, subfontIndex=0))
                except Exception:
                    pass
        _pdf_fonts_registered = True
    except ImportError:
        pass

class ExportRequestBody(PydanticModel):
    chat_messages: Optional[List[dict]] = Field(default=None)
    resume_data: Optional[dict] = Field(default=None)
    template: Optional[str] = Field(default=None)
from app.tasks.export_tasks import export_resume_docx, export_resume_pdf
from app.utils.document_gen import build_html_resume, build_docx_resume

router = APIRouter()
EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "media", "exports")


def _build_resume_data(resume) -> dict:
    return {
        "basic_info": resume.basic_info,
        "summary": resume.summary,
        "target_position": resume.target_position,
        "skills": [{"category": s.category, "name": s.name, "level": s.level} for s in resume.skills],
        "education": [
            {"school": e.school, "degree": e.degree, "major": e.major, "start_date": str(e.start_date) if e.start_date else None, "end_date": str(e.end_date) if e.end_date else None, "description": e.description}
            for e in resume.education
        ],
        "work_experiences": [
            {"company": w.company, "title": w.title, "start_date": str(w.start_date) if w.start_date else None, "end_date": str(w.end_date) if w.end_date else None, "description": w.description}
            for w in resume.work_experiences
        ],
        "projects": [
            {"name": p.name, "role": p.role, "description": p.description, "highlights": p.highlights, "tech_stack": p.tech_stack}
            for p in resume.projects
        ],
    }


def _extract_chat_highlights(chat_messages: list) -> str:
    """Extract AI suggestions from chat history for the resume."""
    ai_msgs = [m["content"] for m in chat_messages if m.get("role") == "ai" and m.get("content")]
    if not ai_msgs:
        return ""
    # Take last 5 AI messages, join them as the AI suggestions section
    return "\n\n---\n\n".join(ai_msgs[-5:])


@router.post("/resume/{resume_id}/pdf")
async def export_pdf(resume_id: uuid.UUID, template: str = Query("modern"), current_user: User = Depends(get_current_user), service: ResumeService = Depends(ResumeService)):
    resume = await service.get_resume(user_id=current_user.id, resume_id=resume_id)
    task = export_resume_pdf.delay(_build_resume_data(resume), template)
    return {"task_id": task.id, "status": "queued"}


@router.post("/resume/{resume_id}/docx")
async def export_docx(resume_id: uuid.UUID, template: str = Query("classic"), current_user: User = Depends(get_current_user), service: ResumeService = Depends(ResumeService)):
    resume = await service.get_resume(user_id=current_user.id, resume_id=resume_id)
    task = export_resume_docx.delay(_build_resume_data(resume), template)
    return {"task_id": task.id, "status": "queued"}


@router.get("/download/{filename}")
async def download_file(filename: str):
    filepath = os.path.join(EXPORT_DIR, filename)
    if not os.path.exists(filepath):
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(filepath, filename=filename)


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    return {"task_id": task_id, "status": result.status, "result": result.result if result.ready() else None}


# --- Sync export (with optional chat integration) ---

@router.post("/resume/{resume_id}/pdf/sync")
async def export_pdf_sync(
    resume_id: uuid.UUID,
    body: ExportRequestBody = Body(default_factory=ExportRequestBody),
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    # Prefer the guided resume_data from frontend, fall back to DB data
    if body.resume_data:
        resume_data = body.resume_data
    else:
        resume = await service.get_resume(user_id=current_user.id, resume_id=resume_id)
        resume_data = _build_resume_data(resume)
    if body.chat_messages:
        resume_data["chat_highlights"] = _extract_chat_highlights(body.chat_messages)
    html = build_html_resume(resume_data, template=body.template or "modern")
    try:
        _register_pdf_fonts()
        from xhtml2pdf import pisa
        buf = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=buf, encoding="utf-8")
        if pisa_status.err:
            logger.error("xhtml2pdf conversion error: %s", pisa_status.err)
            raise RuntimeError("PDF conversion failed")
        pdf_bytes = buf.getvalue()
        if not pdf_bytes or len(pdf_bytes) < 100:
            raise RuntimeError("Generated PDF is empty or too small")
        return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf",
                                 headers={"Content-Disposition": f"attachment; filename=resume_{resume_id}.pdf"})
    except ImportError:
        logger.exception("xhtml2pdf not installed")
        html_bytes = html.encode("utf-8")
        return StreamingResponse(BytesIO(html_bytes), media_type="text/html; charset=utf-8",
                                 headers={"Content-Disposition": f"attachment; filename=resume_{resume_id}.html"})
    except Exception:
        logger.exception("PDF generation failed, falling back to HTML")
        html_bytes = html.encode("utf-8")
        return StreamingResponse(BytesIO(html_bytes), media_type="text/html; charset=utf-8",
                                 headers={"Content-Disposition": f"attachment; filename=resume_{resume_id}.html"})


@router.post("/resume/{resume_id}/docx/sync")
async def export_docx_sync(
    resume_id: uuid.UUID,
    body: ExportRequestBody = Body(default_factory=ExportRequestBody),
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(ResumeService),
):
    # Prefer the guided resume_data from frontend, fall back to DB data
    if body.resume_data:
        resume_data = body.resume_data
    else:
        resume = await service.get_resume(user_id=current_user.id, resume_id=resume_id)
        resume_data = _build_resume_data(resume)
    if body.chat_messages:
        resume_data["chat_highlights"] = _extract_chat_highlights(body.chat_messages)
    docx_bytes = build_docx_resume(resume_data)
    return StreamingResponse(BytesIO(docx_bytes),
                             media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                             headers={"Content-Disposition": f"attachment; filename=resume_{resume_id}.docx"})


# --- Interview export ---

@router.post("/interview/{session_id}/txt")
async def export_interview_txt(session_id: uuid.UUID, current_user: User = Depends(get_current_user)):
    from app.core.database import async_session
    from app.models.interview import InterviewSession, InterviewMessage
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with async_session() as db:
        result = await db.execute(
            select(InterviewSession)
            .where(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id)
            .options(selectinload(InterviewSession.messages))
        )
        session = result.scalar_one_or_none()
        if not session:
            return {"error": "Session not found"}

        lines = [f"面试类型：{session.session_type}", f"时间：{session.started_at.strftime('%Y-%m-%d %H:%M')}", f"题目数：{session.questions_asked}/{session.questions_total}"]
        if session.overall_score:
            lines.append(f"总分：{session.overall_score}")
        lines.extend(["", "=" * 50, ""])
        for msg in session.messages:
            role_label = "AI面试官" if msg.role == "ai" else "候选人"
            lines.append(f"{role_label}:")
            lines.append(msg.content)
            lines.append("")

        text = "\n".join(lines)
        return StreamingResponse(BytesIO(text.encode("utf-8")), media_type="text/plain; charset=utf-8",
                                 headers={"Content-Disposition": f"attachment; filename=interview_{session_id}.txt"})
