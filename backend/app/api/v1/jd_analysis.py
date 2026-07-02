import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.jd_analysis import JDAnalysisRequest, JDAnalysisResponse
from app.services.jd_service import JDService

router = APIRouter()


@router.post("", response_model=JDAnalysisResponse, status_code=201)
async def analyze_jd(
    request: JDAnalysisRequest,
    current_user: User = Depends(get_current_user),
    service: JDService = Depends(JDService),
):
    try:
        return await service.analyze(user_id=current_user.id, raw_text=request.raw_text)
    except Exception as e:
        from fastapi import HTTPException
        import logging
        logging.getLogger("jd_analysis").exception("JD analysis failed")
        raise HTTPException(status_code=500, detail=f"JD analysis failed: {str(e)}")


@router.get("", response_model=list[JDAnalysisResponse])
async def list_jd_analyses(
    current_user: User = Depends(get_current_user),
    service: JDService = Depends(JDService),
):
    return await service.list_analyses(user_id=current_user.id)


@router.get("/{analysis_id}", response_model=JDAnalysisResponse)
async def get_jd_analysis(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: JDService = Depends(JDService),
):
    return await service.get_analysis(user_id=current_user.id, analysis_id=analysis_id)


@router.delete("/{analysis_id}", status_code=204)
async def delete_jd_analysis(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: JDService = Depends(JDService),
):
    await service.delete_analysis(user_id=current_user.id, analysis_id=analysis_id)
