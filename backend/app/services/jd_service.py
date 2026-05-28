import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.jd_analysis import JDAnalysis
from app.ai.jd_agent import JDAgent


class JDService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.agent = JDAgent()

    async def analyze(self, user_id: uuid.UUID, raw_text: str) -> JDAnalysis:
        result = self.agent.analyze(raw_text)

        analysis = JDAnalysis(
            user_id=user_id,
            raw_text=raw_text,
            tech_stack=result.get("tech_stack"),
            keywords=result.get("keywords"),
            implicit_requirements=result.get("implicit_requirements"),
            difficulty_score=result.get("difficulty_score"),
            risk_flags=result.get("risk_flags"),
            risk_score=result.get("risk_score"),
            position_title=result.get("position_title"),
            company_type=result.get("company_type"),
        )
        self.db.add(analysis)
        await self.db.flush()
        return analysis

    async def list_analyses(self, user_id: uuid.UUID) -> list[JDAnalysis]:
        result = await self.db.execute(
            select(JDAnalysis)
            .where(JDAnalysis.user_id == user_id)
            .order_by(JDAnalysis.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_analysis(self, user_id: uuid.UUID, analysis_id: uuid.UUID) -> JDAnalysis:
        result = await self.db.execute(
            select(JDAnalysis).where(
                JDAnalysis.id == analysis_id, JDAnalysis.user_id == user_id
            )
        )
        analysis = result.scalar_one_or_none()
        if not analysis:
            raise NotFoundException("JD analysis not found")
        return analysis

    async def delete_analysis(self, user_id: uuid.UUID, analysis_id: uuid.UUID) -> None:
        analysis = await self.get_analysis(user_id, analysis_id)
        await self.db.delete(analysis)
        await self.db.flush()
