import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.resume import (
    Resume,
    ResumeEducation,
    ResumeProject,
    ResumeSkill,
    ResumeWorkExperience,
)


class ResumeService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    # --- Resume CRUD ---

    async def create_resume(self, user_id: uuid.UUID, title: str, target_position: str | None = None, language: str = "zh") -> Resume:
        resume = Resume(user_id=user_id, title=title, target_position=target_position, language=language)
        self.db.add(resume)
        await self.db.flush()
        return resume

    async def list_resumes(self, user_id: uuid.UUID) -> list[Resume]:
        result = await self.db.execute(
            select(Resume).where(Resume.user_id == user_id).order_by(Resume.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Resume:
        result = await self.db.execute(
            select(Resume)
            .where(Resume.id == resume_id, Resume.user_id == user_id)
            .options(
                selectinload(Resume.education),
                selectinload(Resume.work_experiences),
                selectinload(Resume.projects),
                selectinload(Resume.skills),
            )
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise NotFoundException("Resume not found")
        return resume

    async def update_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID, **kwargs) -> Resume:
        resume = await self.get_resume(user_id, resume_id)
        for key, value in kwargs.items():
            if value is not None:
                setattr(resume, key, value)
        await self.db.flush()
        await self.db.refresh(resume)
        return resume

    async def delete_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> None:
        resume = await self.get_resume(user_id, resume_id)
        await self.db.delete(resume)
        await self.db.flush()

    # --- Education CRUD ---

    async def add_education(self, user_id: uuid.UUID, resume_id: uuid.UUID, data: dict) -> ResumeEducation:
        await self.get_resume(user_id, resume_id)
        edu = ResumeEducation(resume_id=resume_id, **data)
        self.db.add(edu)
        await self.db.flush()
        return edu

    async def update_education(self, user_id: uuid.UUID, resume_id: uuid.UUID, edu_id: uuid.UUID, data: dict) -> ResumeEducation:
        await self.get_resume(user_id, resume_id)
        edu = await self.db.get(ResumeEducation, edu_id)
        if not edu or edu.resume_id != resume_id:
            raise NotFoundException("Education entry not found")
        for key, value in data.items():
            if value is not None:
                setattr(edu, key, value)
        await self.db.flush()
        return edu

    async def delete_education(self, user_id: uuid.UUID, resume_id: uuid.UUID, edu_id: uuid.UUID) -> None:
        await self.get_resume(user_id, resume_id)
        edu = await self.db.get(ResumeEducation, edu_id)
        if not edu or edu.resume_id != resume_id:
            raise NotFoundException("Education entry not found")
        await self.db.delete(edu)
        await self.db.flush()

    # --- Work Experience CRUD ---

    async def add_experience(self, user_id: uuid.UUID, resume_id: uuid.UUID, data: dict) -> ResumeWorkExperience:
        await self.get_resume(user_id, resume_id)
        exp = ResumeWorkExperience(resume_id=resume_id, **data)
        self.db.add(exp)
        await self.db.flush()
        return exp

    async def update_experience(self, user_id: uuid.UUID, resume_id: uuid.UUID, exp_id: uuid.UUID, data: dict) -> ResumeWorkExperience:
        await self.get_resume(user_id, resume_id)
        exp = await self.db.get(ResumeWorkExperience, exp_id)
        if not exp or exp.resume_id != resume_id:
            raise NotFoundException("Work experience entry not found")
        for key, value in data.items():
            if value is not None:
                setattr(exp, key, value)
        await self.db.flush()
        return exp

    async def delete_experience(self, user_id: uuid.UUID, resume_id: uuid.UUID, exp_id: uuid.UUID) -> None:
        await self.get_resume(user_id, resume_id)
        exp = await self.db.get(ResumeWorkExperience, exp_id)
        if not exp or exp.resume_id != resume_id:
            raise NotFoundException("Work experience entry not found")
        await self.db.delete(exp)
        await self.db.flush()

    # --- Project CRUD ---

    async def add_project(self, user_id: uuid.UUID, resume_id: uuid.UUID, data: dict) -> ResumeProject:
        await self.get_resume(user_id, resume_id)
        proj = ResumeProject(resume_id=resume_id, **data)
        self.db.add(proj)
        await self.db.flush()
        return proj

    async def update_project(self, user_id: uuid.UUID, resume_id: uuid.UUID, proj_id: uuid.UUID, data: dict) -> ResumeProject:
        await self.get_resume(user_id, resume_id)
        proj = await self.db.get(ResumeProject, proj_id)
        if not proj or proj.resume_id != resume_id:
            raise NotFoundException("Project not found")
        for key, value in data.items():
            if value is not None:
                setattr(proj, key, value)
        await self.db.flush()
        return proj

    async def delete_project(self, user_id: uuid.UUID, resume_id: uuid.UUID, proj_id: uuid.UUID) -> None:
        await self.get_resume(user_id, resume_id)
        proj = await self.db.get(ResumeProject, proj_id)
        if not proj or proj.resume_id != resume_id:
            raise NotFoundException("Project not found")
        await self.db.delete(proj)
        await self.db.flush()

    # --- Skill CRUD ---

    async def add_skill(self, user_id: uuid.UUID, resume_id: uuid.UUID, data: dict) -> ResumeSkill:
        await self.get_resume(user_id, resume_id)
        skill = ResumeSkill(resume_id=resume_id, **data)
        self.db.add(skill)
        await self.db.flush()
        return skill

    async def update_skill(self, user_id: uuid.UUID, resume_id: uuid.UUID, skill_id: uuid.UUID, data: dict) -> ResumeSkill:
        await self.get_resume(user_id, resume_id)
        skill = await self.db.get(ResumeSkill, skill_id)
        if not skill or skill.resume_id != resume_id:
            raise NotFoundException("Skill not found")
        for key, value in data.items():
            if value is not None:
                setattr(skill, key, value)
        await self.db.flush()
        return skill

    async def delete_skill(self, user_id: uuid.UUID, resume_id: uuid.UUID, skill_id: uuid.UUID) -> None:
        await self.get_resume(user_id, resume_id)
        skill = await self.db.get(ResumeSkill, skill_id)
        if not skill or skill.resume_id != resume_id:
            raise NotFoundException("Skill not found")
        await self.db.delete(skill)
        await self.db.flush()
