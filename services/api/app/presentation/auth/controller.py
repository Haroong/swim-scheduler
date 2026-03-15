"""
Auth Controller

Google OAuth 인증 라우터
"""
from fastapi import APIRouter, Depends, HTTPException

from app.application.auth.service import AuthService
from app.presentation.auth.schema import GoogleLoginRequest, AuthResponse, UserResponse
from app.infrastructure.persistence.dependencies import get_auth_service
from app.shared.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth")


@router.post("/google", response_model=AuthResponse)
def google_login(
    request: GoogleLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Google ID Token으로 로그인/회원가입"""
    try:
        result = auth_service.google_login(request.credential)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_me(
    user=Depends(get_current_user),
):
    """현재 로그인된 유저 정보"""
    return user
