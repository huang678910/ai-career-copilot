from fastapi import APIRouter

from app.api.v1 import auth, resumes, jd_analysis, tailor, interview, export

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
router.include_router(jd_analysis.router, prefix="/jd-analysis", tags=["jd-analysis"])
router.include_router(tailor.router, prefix="/tailor", tags=["tailor"])
router.include_router(interview.router, prefix="/interview", tags=["interview"])
router.include_router(export.router, prefix="/export", tags=["export"])
