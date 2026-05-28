import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.tailor import TailorRequest, TailoredResumeResponse
from app.services.tailor_service import TailorService

router = APIRouter()


@router.post("", response_model=TailoredResumeResponse, status_code=201)
async def tailor_resume(
    request: TailorRequest,
    current_user: User = Depends(get_current_user),
    service: TailorService = Depends(TailorService),
):
    return await service.tailor(
        user_id=current_user.id,
        source_resume_id=request.source_resume_id,
        jd_analysis_id=request.jd_analysis_id,
    )


@router.get("", response_model=list[TailoredResumeResponse])
async def list_tailored(
    current_user: User = Depends(get_current_user),
    service: TailorService = Depends(TailorService),
):
    return await service.list_tailored(user_id=current_user.id)


@router.get("/{tailored_id}", response_model=TailoredResumeResponse)
async def get_tailored(
    tailored_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: TailorService = Depends(TailorService),
):
    return await service.get_tailored(user_id=current_user.id, tailored_id=tailored_id)


@router.delete("/{tailored_id}", status_code=204)
async def delete_tailored(
    tailored_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: TailorService = Depends(TailorService),
):
    await service.delete_tailored(user_id=current_user.id, tailored_id=tailored_id)
