"""
인증 관련 FastAPI 의존성
"""
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.application.auth.service import AuthService
from app.infrastructure.persistence.dependencies import get_auth_service

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
):
    """JWT에서 현재 유저 조회 (필수)"""
    user = auth_service.get_current_user(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    auth_service: AuthService = Depends(get_auth_service),
):
    """JWT에서 현재 유저 조회 (선택적 - 비로그인 허용)"""
    if credentials is None:
        return None
    return auth_service.get_current_user(credentials.credentials)
