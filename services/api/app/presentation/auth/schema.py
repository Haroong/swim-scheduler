"""
Auth Schemas
인증 API 요청/응답 스키마
"""
from typing import Optional
from pydantic import BaseModel


class GoogleLoginRequest(BaseModel):
    """Google 로그인 요청"""
    credential: str


class UserResponse(BaseModel):
    """유저 정보 응답"""
    id: int
    email: str
    name: str
    profile_image: Optional[str] = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """인증 응답 (JWT + 유저 정보)"""
    access_token: str
    token_type: str
    user: UserResponse
