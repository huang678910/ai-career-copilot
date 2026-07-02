import asyncio
import json
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.api.deps import get_current_user_ws
from app.ai.interview_agent import InterviewAgent
from app.core.database import async_session
from app.models.interview import InterviewMessage, InterviewSession
from app.websocket.manager import manager

router = APIRouter()
interview_agent = InterviewAgent()

MAX_MSG_LENGTH = 5000  # chars
MSG_RATE_SECONDS = 1.0  # minimum interval between AI-triggering messages
_ws_last_msg: dict[str, float] = {}
MAX_CONNS_PER_USER = 3


@router.websocket("/ws/interview/{session_id}")
async def interview_ws(websocket: WebSocket, session_id: uuid.UUID):
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
    agent_session_id = f"{user_id}:{session_id}"

    # Check connection limit
    current_conns = len(manager.get_connections(user_id))
    if current_conns >= MAX_CONNS_PER_USER:
        await websocket.close(code=4003, reason="Too many connections")
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()

            # Validate message size
            if len(raw) > MAX_MSG_LENGTH:
                await manager.send_personal_message(
                    {"type": "error", "data": {"message": "消息过长"}}, websocket
                )
                continue
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await manager.send_personal_message({"type": "error", "data": {"message": "无效的JSON格式"}}, websocket)
                continue

            msg_type = msg.get("type")

            if msg_type == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)
                continue

            if msg_type == "start_interview":
                # Skip re-init if agent session already exists (user reconnected)
                if agent_session_id in interview_agent._sessions:
                    await _sync_counter(user_id, session_id, agent_session_id, websocket)
                    continue

                session_type = msg.get("data", {}).get("session_type", "technical")
                questions_total = msg.get("data", {}).get("questions_total", 10)

                # Load resume data for personalized interview questions
                resume_data = None
                try:
                    async with async_session() as db:
                        from sqlalchemy import select
                        from app.models.interview import InterviewSession as IS
                        from app.models.resume import Resume
                        from sqlalchemy.orm import selectinload
                        result = await db.execute(select(IS).where(IS.id == session_id))
                        db_sess = result.scalar_one_or_none()
                        if db_sess and db_sess.resume_id:
                            r = await db.execute(
                                select(Resume)
                                .where(Resume.id == db_sess.resume_id)
                                .options(
                                    selectinload(Resume.skills),
                                    selectinload(Resume.projects),
                                    selectinload(Resume.work_experiences),
                                    selectinload(Resume.education),
                                )
                            )
                            resume = r.scalar_one_or_none()
                            if resume:
                                resume_data = {
                                    "name": (resume.basic_info or {}).get("name", ""),
                                    "target_position": resume.target_position or "",
                                    "summary": resume.summary or "",
                                    "skills": [{"name": s.name, "category": s.category, "level": s.level} for s in (resume.skills or [])],
                                    "projects": [{"name": p.name, "role": p.role, "description": p.description, "tech_stack": p.tech_stack} for p in (resume.projects or [])],
                                    "work_experience": [{"company": w.company, "title": w.title, "description": w.description} for w in (resume.work_experiences or [])],
                                    "education": [{"school": e.school, "major": e.major, "degree": e.degree} for e in (resume.education or [])],
                                }
                except Exception:
                    import logging
                    logging.getLogger("interview_ws").warning(
                        "Failed to load resume data for interview session %s", session_id
                    )

                interview_agent.start_session(agent_session_id, session_type, questions_total, resume_data)
                # Stream the first question via executor
                loop = asyncio.get_event_loop()
                chunks = await loop.run_in_executor(
                    None, lambda: list(interview_agent.chat_stream(agent_session_id))
                )
                full_text = ""
                for chunk in chunks:
                    full_text += chunk
                    await manager.send_personal_message(
                        {"type": "chunk", "data": {"text": chunk}}, websocket
                    )
                await manager.send_personal_message({"type": "done"}, websocket)

                # Persist first AI question and update counter
                interview_agent._sessions[agent_session_id]["questions_asked"] += 1
                await _save_message(session_id, "ai", full_text, "question")
                await _sync_counter(user_id, session_id, agent_session_id, websocket)

            elif msg_type == "user_answer":
                # Rate check: prevent rapid-fire AI calls
                now = time.time()
                last = _ws_last_msg.get(agent_session_id, 0)
                if now - last < MSG_RATE_SECONDS:
                    await manager.send_personal_message(
                        {"type": "error", "data": {"message": "请稍候再发送"}}, websocket
                    )
                    continue
                _ws_last_msg[agent_session_id] = now

                # Check if interview has reached question limit
                questions_asked = interview_agent.get_questions_asked(agent_session_id)
                questions_total = interview_agent._sessions.get(agent_session_id, {}).get("questions_total", 10)
                if questions_asked >= questions_total:
                    await manager.send_personal_message(
                        {"type": "chunk", "data": {"text": "\n\n已达到设定的题目数量，面试即将结束。\n"}}, websocket
                    )
                    feedback = interview_agent.generate_feedback(agent_session_id)
                    await manager.send_personal_message(
                        {"type": "interview_complete", "data": feedback}, websocket
                    )
                    await _save_feedback(session_id, feedback)
                    interview_agent.end_session(agent_session_id)
                    await manager.send_personal_message({"type": "done"}, websocket)
                    continue

                answer = msg.get("data", {}).get("text", "")
                if not answer.strip():
                    continue

                # Save user answer to DB
                await _save_message(session_id, "user", answer, "answer")

                # Stream AI response via executor
                loop = asyncio.get_event_loop()
                chunks = await loop.run_in_executor(
                    None, lambda: list(interview_agent.chat_stream(agent_session_id, answer))
                )
                full_text = ""
                for chunk in chunks:
                    full_text += chunk
                    await manager.send_personal_message(
                        {"type": "chunk", "data": {"text": chunk}}, websocket
                    )
                await manager.send_personal_message({"type": "done"}, websocket)

                # Detect message type: if response contains score/评分, it's evaluation
                is_evaluation = any(kw in full_text for kw in ["评分", "总分", "得分", "overall_score", "面试结束", "反馈报告"])
                msg_type_label = "evaluation" if is_evaluation else "question"
                if msg_type_label == "question":
                    interview_agent._sessions[agent_session_id]["questions_asked"] += 1
                await _save_message(session_id, "ai", full_text, msg_type_label)
                await _sync_counter(user_id, session_id, agent_session_id, websocket)

                # Auto-end if AI produced evaluation
                if is_evaluation:
                    feedback = interview_agent.generate_feedback(agent_session_id)
                    await manager.send_personal_message(
                        {"type": "interview_complete", "data": feedback}, websocket
                    )
                    await _save_feedback(session_id, feedback)
                    interview_agent.end_session(agent_session_id)

            elif msg_type == "end_interview":
                feedback = interview_agent.generate_feedback(agent_session_id)
                await manager.send_personal_message(
                    {"type": "interview_complete", "data": feedback}, websocket
                )
                # Save feedback to DB before clearing agent session
                await _save_feedback(session_id, feedback)
                interview_agent.end_session(agent_session_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)


async def _save_message(session_id: uuid.UUID, role: str, content: str, msg_type: str):
    try:
        async with async_session() as db:
            msg = InterviewMessage(session_id=session_id, role=role, content=content, message_type=msg_type)
            db.add(msg)
            await db.commit()
    except Exception:
        import logging
        logging.getLogger("interview_ws").warning(
            "_save_interview_message failed session=%s", session_id
        )


async def _sync_counter(user_id: str, session_id: uuid.UUID, agent_session_id: str, websocket: WebSocket):
    count = interview_agent.get_questions_asked(agent_session_id)
    try:
        async with async_session() as db:
            result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
            session = result.scalar_one_or_none()
            if session:
                session.questions_asked = count
                await db.commit()
    except Exception:
        import logging
        logging.getLogger("interview_ws").warning(
            "_sync_counter failed session=%s", session_id
        )
    await manager.send_personal_message(
        {"type": "counter_update", "data": {"questions_asked": count}}, websocket
    )


async def _save_feedback(session_id: uuid.UUID, feedback: dict):
    try:
        async with async_session() as db:
            result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
            session = result.scalar_one_or_none()
            if session and session.status == "in_progress":
                session.status = "completed"
                session.completed_at = datetime.now(timezone.utc)
                session.overall_score = feedback.get("overall_score") if isinstance(feedback, dict) else None
                session.feedback = feedback
                await db.commit()
    except Exception:
        import logging
        logging.getLogger("interview_ws").warning(
            "_save_feedback failed session=%s", session_id
        )
