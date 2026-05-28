import uuid

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.resume_tailor import TailoredResume
from app.models.jd_analysis import JDAnalysis
from app.models.resume import Resume
from app.ai.tailor_agent import TailorAgent


class TailorService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.agent = TailorAgent()

    async def tailor(self, user_id: uuid.UUID, source_resume_id: uuid.UUID, jd_analysis_id: uuid.UUID) -> TailoredResume:
        # Verify resume exists and belongs to user
        resume_result = await self.db.execute(
            select(Resume)
            .where(Resume.id == source_resume_id, Resume.user_id == user_id)
            .options(selectinload(Resume.skills), selectinload(Resume.projects), selectinload(Resume.work_experiences))
        )
        resume = resume_result.scalar_one_or_none()
        if not resume:
            raise NotFoundException("Resume not found")

        # Verify JD analysis exists and belongs to user
        jd_result = await self.db.execute(
            select(JDAnalysis).where(JDAnalysis.id == jd_analysis_id, JDAnalysis.user_id == user_id)
        )
        jd_analysis = jd_result.scalar_one_or_none()
        if not jd_analysis:
            raise NotFoundException("JD analysis not found")

        # Build resume data dict
        resume_data = {
            "summary": resume.summary,
            "target_position": resume.target_position,
            "skills": [
                {"category": s.category, "name": s.name, "level": s.level}
                for s in resume.skills
            ],
            "projects": [
                {
                    "name": p.name,
                    "role": p.role,
                    "description": p.description,
                    "tech_stack": p.tech_stack,
                    "highlights": p.highlights,
                }
                for p in resume.projects
            ],
            "work_experiences": [
                {
                    "company": w.company,
                    "title": w.title,
                    "description": w.description,
                }
                for w in resume.work_experiences
            ],
        }

        jd_data = {
            "tech_stack": jd_analysis.tech_stack,
            "keywords": jd_analysis.keywords,
            "position_title": jd_analysis.position_title,
            "difficulty_score": jd_analysis.difficulty_score,
        }

        # Run AI tailoring
        result = self.agent.tailor(resume_data, jd_data)

        # Get version number
        version_result = await self.db.execute(
            select(func.count(TailoredResume.id)).where(
                TailoredResume.source_resume_id == source_resume_id,
                TailoredResume.jd_analysis_id == jd_analysis_id,
            )
        )
        version = version_result.scalar() + 1

        tailored = TailoredResume(
            user_id=user_id,
            source_resume_id=source_resume_id,
            jd_analysis_id=jd_analysis_id,
            version=version,
            match_score=result.get("match_score"),
            optimized_content=result,
            skill_gaps=result.get("skill_gaps"),
            tailoring_notes=result.get("tailoring_notes"),
        )
        self.db.add(tailored)
        await self.db.flush()
        return tailored

    async def list_tailored(self, user_id: uuid.UUID) -> list[TailoredResume]:
        result = await self.db.execute(
            select(TailoredResume)
            .where(TailoredResume.user_id == user_id)
            .order_by(TailoredResume.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_tailored(self, user_id: uuid.UUID, tailored_id: uuid.UUID) -> TailoredResume:
        result = await self.db.execute(
            select(TailoredResume).where(
                TailoredResume.id == tailored_id, TailoredResume.user_id == user_id
            )
        )
        tailored = result.scalar_one_or_none()
        if not tailored:
            raise NotFoundException("Tailored resume not found")
        return tailored

    async def delete_tailored(self, user_id: uuid.UUID, tailored_id: uuid.UUID) -> None:
        tailored = await self.get_tailored(user_id, tailored_id)
        await self.db.delete(tailored)
        await self.db.flush()
