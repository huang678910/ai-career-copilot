import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# --- Basic Info ---

class BasicInfo(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    website: str = ""
    linkedin: str = ""


# --- Education ---

class EducationBase(BaseModel):
    school: str = Field(min_length=1, max_length=200)
    degree: str | None = None
    major: str = Field(min_length=1, max_length=200)
    start_date: date | None = None
    end_date: date | None = None
    gpa: str | None = None
    description: str | None = None


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    school: str | None = None
    degree: str | None = None
    major: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    gpa: str | None = None
    description: str | None = None


class EducationResponse(EducationBase):
    id: uuid.UUID
    resume_id: uuid.UUID

    model_config = {"from_attributes": True}


# --- Work Experience ---

class WorkExperienceBase(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=200)
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    current: bool = False
    description: str | None = None


class WorkExperienceCreate(WorkExperienceBase):
    pass


class WorkExperienceUpdate(BaseModel):
    company: str | None = None
    title: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    current: bool | None = None
    description: str | None = None


class WorkExperienceResponse(WorkExperienceBase):
    id: uuid.UUID
    resume_id: uuid.UUID

    model_config = {"from_attributes": True}


# --- Project ---

class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    role: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    highlights: list[str] | None = None
    tech_stack: list[str] | None = None
    project_url: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    highlights: list[str] | None = None
    tech_stack: list[str] | None = None
    project_url: str | None = None


class ProjectResponse(ProjectBase):
    id: uuid.UUID
    resume_id: uuid.UUID

    model_config = {"from_attributes": True}


# --- Skill ---

class SkillBase(BaseModel):
    category: str | None = None
    name: str = Field(min_length=1, max_length=100)
    level: str | None = None


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    category: str | None = None
    name: str | None = None
    level: str | None = None


class SkillResponse(SkillBase):
    id: uuid.UUID
    resume_id: uuid.UUID

    model_config = {"from_attributes": True}


# --- Resume ---

class ResumeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    target_position: str | None = None
    language: str = "zh"


class ResumeUpdate(BaseModel):
    title: str | None = None
    basic_info: BasicInfo | None = None
    summary: str | None = None
    target_position: str | None = None
    language: str | None = None


class ResumeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    basic_info: dict | None = None
    summary: str | None = None
    target_position: str | None = None
    language: str
    guided_data: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeDetailResponse(ResumeResponse):
    education: list[EducationResponse] = []
    work_experiences: list[WorkExperienceResponse] = []
    projects: list[ProjectResponse] = []
    skills: list[SkillResponse] = []
