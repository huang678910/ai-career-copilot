from fastapi import APIRouter, Depends, Response

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(request: RegisterRequest, auth_service: AuthService = Depends(AuthService)):
    return await auth_service.register(request)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, auth_service: AuthService = Depends(AuthService)):
    return await auth_service.login(request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest, auth_service: AuthService = Depends(AuthService)):
    return await auth_service.refresh(request.refresh_token)


@router.post("/logout", status_code=204)
async def logout(response: Response):
    response.status_code = 204


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
