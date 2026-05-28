import asyncio, uuid
from app.core.database import async_session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.interview import InterviewSession
from app.models.resume import Resume

async def test():
    session_id = uuid.UUID('6e68da3c-8ffb-49b7-bc96-502ed88966d5')
    async with async_session() as db:
        result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
        db_sess = result.scalar_one_or_none()
        print(f"Session found: {db_sess is not None}, resume_id: {db_sess.resume_id}")
        if db_sess and db_sess.resume_id:
            r = await db.execute(
                select(Resume).where(Resume.id == db_sess.resume_id)
                .options(selectinload(Resume.skills), selectinload(Resume.projects))
            )
            resume = r.scalar_one_or_none()
            if resume:
                print(f"LOADED: {len(resume.skills or [])} skills, target='{resume.target_position}'")
            else:
                print("Resume not found")
asyncio.run(test())
