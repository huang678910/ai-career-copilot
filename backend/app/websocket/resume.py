import asyncio
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.deps import get_current_user_ws
from app.ai.resume_agent import GuidedResumeAgent
from app.core.database import async_session
from app.models.resume_chat import ResumeChatMessage
from app.websocket.manager import manager

router = APIRouter()
resume_agent = GuidedResumeAgent()


@router.websocket("/ws/resume/{resume_id}")
async def resume_chat(websocket: WebSocket, resume_id: uuid.UUID):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    try:
        user = await get_current_user_ws(token)
    except Exception:
        await websocket.close(code=4002, reason="Invalid token")
        return

    user_id = str(user.id)
    session_id = f"{user_id}:{resume_id}"
    await manager.connect(user_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {"type": "error", "data": {"message": "无效的JSON格式"}}, websocket
                )
                continue

            msg_type = msg.get("type")

            if msg_type == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)
                continue

            # --- Guided Resume Flow ---
            if msg_type == "start_guided":
                try:
                    loop = asyncio.get_event_loop()
                    existing_data = msg.get("data", {}).get("collected_data", None)
                    first_msg = await loop.run_in_executor(
                        None, lambda: resume_agent.start_session(session_id, existing_data)
                    )
                    await _save_resume_chat(resume_id, user_id, "ai", first_msg)
                    await manager.send_personal_message(
                        {"type": "chunk", "data": {"text": first_msg}}, websocket
                    )
                    progress = resume_agent.get_progress(session_id)
                    await manager.send_personal_message(
                        {"type": "progress", "data": progress}, websocket
                    )
                    data = resume_agent.get_collected_data(session_id)
                    if data:
                        # Send to frontend FIRST, then persist
                        await manager.send_personal_message(
                            {"type": "resume_update", "data": data}, websocket
                        )
                        await _save_guided_data(resume_id, data)
                        await _sync_resume_fields(resume_id, data)
                        if data.get("summary"):
                            await manager.send_personal_message(
                                {"type": "resume_ready", "data": data}, websocket
                            )
                    await manager.send_personal_message({"type": "done"}, websocket)
                except Exception as e:
                    await manager.send_personal_message(
                        {"type": "error", "data": {"message": str(e)}}, websocket
                    )
                continue

            if msg_type == "resume_session":
                db_data = await _load_guided_data(resume_id)
                frontend_data = msg.get("data", {}).get("collected_data", {}) or {}
                merged = {**frontend_data, **db_data}
                merged.pop("_meta", None)

                history_msgs = []
                try:
                    async with async_session() as db:
                        from sqlalchemy import select
                        result = await db.execute(
                            select(ResumeChatMessage)
                            .where(ResumeChatMessage.resume_id == resume_id)
                            .order_by(ResumeChatMessage.created_at.asc())
                            .limit(40)
                        )
                        history_msgs = result.scalars().all()
                except Exception:
                    import logging
                    logging.getLogger("resume_ws").warning(
                        "Failed to load chat history for resume %s", resume_id
                    )

                resume_agent.init_silent(session_id, merged, history_msgs)

                progress = resume_agent.get_progress(session_id)
                await manager.send_personal_message(
                    {"type": "progress", "data": progress}, websocket
                )
                data = resume_agent.get_collected_data(session_id)
                if data:
                    await manager.send_personal_message(
                        {"type": "resume_update", "data": data}, websocket
                    )
                    if data.get("summary"):
                        await manager.send_personal_message(
                            {"type": "resume_ready", "data": data}, websocket
                        )
                await manager.send_personal_message({"type": "done"}, websocket)
                continue

            if msg_type == "chat_message":
                user_message = msg.get("data", {}).get("text", "")
                if not user_message.strip():
                    continue

                await _save_resume_chat(resume_id, user_id, "user", user_message)

                try:
                    loop = asyncio.get_event_loop()
                    chunks = await loop.run_in_executor(
                        None,
                        lambda: list(resume_agent.chat_stream(session_id, user_message)),
                    )
                    full_response = ""
                    for chunk in chunks:
                        full_response += chunk
                        await manager.send_personal_message(
                            {"type": "chunk", "data": {"text": chunk}}, websocket
                        )

                    await _save_resume_chat(resume_id, user_id, "ai", full_response)

                    progress = resume_agent.get_progress(session_id)
                    await manager.send_personal_message(
                        {"type": "progress", "data": progress}, websocket
                    )

                    data = resume_agent.get_collected_data(session_id)
                    if data:
                        # Send to frontend FIRST, then persist
                        await manager.send_personal_message(
                            {"type": "resume_update", "data": data}, websocket
                        )
                        await _save_guided_data(resume_id, data)
                        await _sync_resume_fields(resume_id, data)

                    # Generate summary when all 6 sections have data
                    all_completed = len(progress.get("completed", [])) >= 6
                    has_summary = bool(data.get("summary"))

                    if all_completed and not has_summary:
                        try:
                            loop = asyncio.get_event_loop()
                            summary = await loop.run_in_executor(
                                None, lambda: resume_agent.build_summary(session_id)
                            )
                            if summary:
                                data["summary"] = summary
                                await _save_guided_data(resume_id, data)
                                await _sync_resume_fields(resume_id, data)
                                await manager.send_personal_message(
                                    {"type": "resume_update", "data": data}, websocket
                                )
                        except Exception:
                            import logging
                            logging.getLogger("resume_ws").exception(
                                "build_summary failed for session %s", session_id
                            )

                    if data.get("summary"):
                        await manager.send_personal_message(
                            {"type": "resume_ready", "data": data}, websocket
                        )

                    await manager.send_personal_message({"type": "done"}, websocket)
                except Exception as e:
                    await manager.send_personal_message(
                        {"type": "error", "data": {"message": str(e)}}, websocket
                    )

            # --- Legacy compat ---
            elif msg_type == "generate_star":
                raw_desc = msg.get("data", {}).get("text", "")
                if raw_desc.strip():
                    try:
                        result = resume_agent.generate_star(raw_desc)
                        await manager.send_personal_message(
                            {"type": "structured", "data": {"type": "star", "result": result}}, websocket
                        )
                        await manager.send_personal_message({"type": "done"}, websocket)
                    except Exception as e:
                        await manager.send_personal_message(
                            {"type": "error", "data": {"message": str(e)}}, websocket
                        )

            elif msg_type == "extract_highlights":
                proj_name = msg.get("data", {}).get("project_name", "")
                proj_desc = msg.get("data", {}).get("description", "")
                if proj_name.strip() and proj_desc.strip():
                    try:
                        result = resume_agent.extract_highlights(proj_name, proj_desc)
                        await manager.send_personal_message(
                            {"type": "structured", "data": {"type": "highlights", "result": result}}, websocket
                        )
                        await manager.send_personal_message({"type": "done"}, websocket)
                    except Exception as e:
                        await manager.send_personal_message(
                            {"type": "error", "data": {"message": str(e)}}, websocket
                        )

            elif msg_type == "reset":
                resume_agent.reset_session(session_id)
                await manager.send_personal_message({"type": "done"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)


def _clean_date_str(value) -> "date | None":
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    if value.lower() in ("present", "至今", "now", "current", ""):
        return None
    from datetime import datetime
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y.%m", "%Y/%m/%d", "%Y/%m", "%Y", "%Y年%m月%d日", "%Y年%m月", "%Y年"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _clean_dates(d: dict) -> dict:
    for key in ("start_date", "end_date"):
        if key in d and isinstance(d[key], str):
            d[key] = _clean_date_str(d[key])
    return d


def _filter_fields(data: dict, whitelist: set) -> dict:
    return {k: v for k, v in data.items() if k in whitelist and v}


EDU_FIELDS = {"school", "degree", "major", "start_date", "end_date", "gpa", "description"}
WORK_FIELDS = {"company", "title", "location", "start_date", "end_date", "description", "highlights"}
PROJ_FIELDS = {"name", "role", "start_date", "end_date", "description", "tech_stack", "highlights", "project_url"}
SKILL_FIELDS = {"category", "name", "level"}


async def _sync_resume_fields(resume_id: uuid.UUID, guided_data: dict):
    if not guided_data:
        return
    try:
        async with async_session() as db:
            from sqlalchemy import select
            from app.models.resume import Resume, ResumeEducation, ResumeWorkExperience, ResumeProject, ResumeSkill

            result = await db.execute(select(Resume).where(Resume.id == resume_id))
            resume = result.scalar_one_or_none()
            if not resume:
                return

            basic = guided_data.get("basic_info", {})
            if basic:
                current_basic = resume.basic_info or {}
                current_basic.update({k: v for k, v in basic.items() if v})
                resume.basic_info = current_basic

            jt = guided_data.get("job_target", {})
            if jt.get("target_position"):
                resume.target_position = jt["target_position"]

            if guided_data.get("summary"):
                resume.summary = guided_data["summary"]

            async def _sync_subsection(model, data_list, required_condition, field_whitelist):
                if not data_list:
                    return
                old_records = (
                    await db.execute(select(model).where(model.resume_id == resume.id))
                ).scalars().all()
                for old in old_records:
                    await db.delete(old)
                for item in data_list:
                    if required_condition(item):
                        _clean_dates(item)
                        db.add(model(resume_id=resume.id, **_filter_fields(item, field_whitelist)))

            await _sync_subsection(ResumeEducation, guided_data.get("education") or [],
                                   lambda e: e.get("school") and e.get("major"), EDU_FIELDS)
            await _sync_subsection(ResumeWorkExperience, guided_data.get("work_experience") or [],
                                   lambda e: e.get("company") and e.get("title"), WORK_FIELDS)
            await _sync_subsection(ResumeProject, guided_data.get("projects") or [],
                                   lambda e: e.get("name"), PROJ_FIELDS)
            await _sync_subsection(ResumeSkill, guided_data.get("skills") or [],
                                   lambda e: e.get("name"), SKILL_FIELDS)

            await db.commit()
    except Exception:
        import logging
        logging.getLogger("resume_ws").exception("_sync_resume_fields failed for resume %s", resume_id)


async def _save_resume_chat(resume_id: uuid.UUID, user_id: str, role: str, content: str):
    try:
        async with async_session() as db:
            msg = ResumeChatMessage(
                resume_id=resume_id, user_id=uuid.UUID(user_id),
                role=role, content=content,
            )
            db.add(msg)
            await db.commit()
    except Exception:
        import logging
        logging.getLogger("resume_ws").warning(
            "_save_resume_chat failed for resume %s user %s", resume_id, user_id
        )


async def _save_guided_data(resume_id: uuid.UUID, data: dict):
    try:
        async with async_session() as db:
            from sqlalchemy import update
            from app.models.resume import Resume
            await db.execute(
                update(Resume).where(Resume.id == resume_id).values(guided_data=data)
            )
            await db.commit()
    except Exception:
        import logging
        logging.getLogger("resume_ws").exception("_save_guided_data failed for resume %s", resume_id)


async def _load_guided_data(resume_id: uuid.UUID) -> dict:
    try:
        async with async_session() as db:
            from sqlalchemy import select
            from app.models.resume import Resume
            result = await db.execute(select(Resume.guided_data).where(Resume.id == resume_id))
            row = result.scalar_one_or_none()
            return row or {}
    except Exception:
        return {}
