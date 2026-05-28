import uuid
from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.interview import InterviewQuestion, InterviewSession, InterviewMessage
from app.models.jd_analysis import JDAnalysis
from app.models.resume import Resume
from app.ai.interview_agent import InterviewAgent


class InterviewService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.agent = InterviewAgent()

    async def generate_questions(
        self, user_id: uuid.UUID, jd_analysis_id: uuid.UUID | None, resume_id: uuid.UUID | None, count: int = 10
    ) -> list[InterviewQuestion]:
        jd_data = None
        resume_data = None

        if jd_analysis_id:
            result = await self.db.execute(
                select(JDAnalysis).where(JDAnalysis.id == jd_analysis_id, JDAnalysis.user_id == user_id)
            )
            jd = result.scalar_one_or_none()
            if jd:
                jd_data = {
                    "position_title": jd.position_title,
                    "tech_stack": jd.tech_stack,
                    "keywords": jd.keywords,
                }

        if resume_id:
            result = await self.db.execute(
                select(Resume)
                .where(Resume.id == resume_id, Resume.user_id == user_id)
                .options(selectinload(Resume.skills), selectinload(Resume.projects))
            )
            resume = result.scalar_one_or_none()
            if resume:
                resume_data = {
                    "title": resume.title,
                    "summary": resume.summary,
                    "skills": [{"name": s.name, "level": s.level} for s in resume.skills],
                    "projects": [{"name": p.name, "description": p.description} for p in resume.projects],
                }

        import asyncio

        generation_id = uuid.uuid4()
        loop = asyncio.get_event_loop()
        questions_data = await loop.run_in_executor(
            None, lambda: self.agent.generate_questions(jd_data, resume_data, count)
        )
        questions = []
        for q in questions_data:
            question = InterviewQuestion(
                user_id=user_id,
                jd_analysis_id=jd_analysis_id,
                resume_id=resume_id,
                question_type=q.get("type", "technical"),
                category=q.get("category"),
                question=q["question"],
                difficulty=q.get("difficulty", "medium"),
                suggested_answer=q.get("suggested_answer"),
                generation_id=generation_id,
            )
            self.db.add(question)
            questions.append(question)

        await self.db.commit()
        return questions

    async def list_questions(self, user_id: uuid.UUID, generation_id: uuid.UUID | None = None) -> list[InterviewQuestion]:
        query = select(InterviewQuestion).where(InterviewQuestion.user_id == user_id)
        if generation_id:
            query = query.where(InterviewQuestion.generation_id == generation_id)
        query = query.order_by(InterviewQuestion.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_generations(self, user_id: uuid.UUID) -> list[dict]:
        from sqlalchemy import func, desc
        result = await self.db.execute(
            select(
                InterviewQuestion.generation_id,
                func.count(InterviewQuestion.id).label("cnt"),
                func.max(InterviewQuestion.created_at).label("latest"),
                func.min(InterviewQuestion.question).label("preview"),
            )
            .where(InterviewQuestion.user_id == user_id)
            .group_by(InterviewQuestion.generation_id)
            .order_by(desc("latest"))
            .limit(20)
        )
        return [
            {"generation_id": row[0], "question_count": row[1], "created_at": row[2], "preview": (row[3] or "")[:80]}
            for row in result.all()
        ]

    async def get_question(self, user_id: uuid.UUID, question_id: uuid.UUID) -> InterviewQuestion:
        result = await self.db.execute(
            select(InterviewQuestion).where(
                InterviewQuestion.id == question_id, InterviewQuestion.user_id == user_id
            )
        )
        q = result.scalar_one_or_none()
        if not q:
            raise NotFoundException("Question not found")
        return q

    async def delete_question(self, user_id: uuid.UUID, question_id: uuid.UUID) -> None:
        q = await self.get_question(user_id, question_id)
        await self.db.delete(q)
        await self.db.flush()

    async def delete_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> None:
        session = await self.get_session(user_id, session_id)
        await self.db.delete(session)
        await self.db.flush()

    # --- Sessions ---

    async def create_session(self, user_id: uuid.UUID, session_type: str, questions_total: int, resume_id: uuid.UUID | None = None) -> InterviewSession:
        # Load resume data if provided
        resume_data = None
        if resume_id:
            from app.models.resume import Resume
            from sqlalchemy.orm import selectinload
            result = await self.db.execute(
                select(Resume)
                .where(Resume.id == resume_id, Resume.user_id == user_id)
                .options(
                    selectinload(Resume.skills),
                    selectinload(Resume.projects),
                    selectinload(Resume.work_experiences),
                    selectinload(Resume.education),
                )
            )
            resume = result.scalar_one_or_none()
            if resume:
                resume_data = {
                    "basic_info": resume.basic_info,
                    "summary": resume.summary,
                    "target_position": resume.target_position,
                    "skills": [{"name": s.name, "category": s.category, "level": s.level} for s in (resume.skills or [])],
                    "projects": [{"name": p.name, "description": p.description, "tech_stack": p.tech_stack} for p in (resume.projects or [])],
                    "work": [{"company": w.company, "title": w.title, "description": w.description} for w in (resume.work_experiences or [])],
                    "education": [{"school": e.school, "major": e.major, "degree": e.degree} for e in (resume.education or [])],
                }

        session = InterviewSession(
            user_id=user_id,
            session_type=session_type,
            questions_total=questions_total,
            resume_id=resume_id,
        )
        self.db.add(session)
        await self.db.commit()
        # Store resume_data on session for downstream use
        session._resume_data = resume_data
        return session

    async def list_sessions(self, user_id: uuid.UUID) -> list[InterviewSession]:
        result = await self.db.execute(
            select(InterviewSession)
            .where(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.started_at.desc())
        )
        return list(result.scalars().all())

    async def get_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> InterviewSession:
        result = await self.db.execute(
            select(InterviewSession)
            .where(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
            .options(selectinload(InterviewSession.messages))
        )
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundException("Session not found")
        return session

    async def end_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> InterviewSession:
        session = await self.get_session(user_id, session_id)
        if session.status != "in_progress":
            return session  # Already completed by WebSocket

        # Try to generate feedback; WebSocket may have already cleaned up the agent session
        agent_key = f"{user_id}:{session_id}"
        feedback = self.agent.generate_feedback(agent_key)
        if isinstance(feedback, dict) and feedback.get("error"):
            return session  # Agent session already cleaned up by WS, DB already has feedback

        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        session.overall_score = feedback.get("overall_score") if isinstance(feedback, dict) else None
        session.feedback = feedback

        await self.db.flush()
        self.agent.end_session(agent_key)
        return session

    async def add_message(
        self, user_id: uuid.UUID, session_id: uuid.UUID, role: str, content: str, msg_type: str | None = None
    ) -> InterviewMessage:
        session = await self.get_session(user_id, session_id)
        if session.status != "in_progress":
            raise NotFoundException("Session is not active")

        msg = InterviewMessage(
            session_id=session_id, role=role, content=content, message_type=msg_type
        )
        self.db.add(msg)
        await self.db.flush()
        return msg
