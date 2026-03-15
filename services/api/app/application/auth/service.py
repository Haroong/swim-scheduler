"""
Auth Service

Google ID Token 검증, JWT 생성/검증, 유저 upsert
"""
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.domain.user.model import User
from app.domain.user.repository import UserRepository
from app.shared.config.settings import settings


class AuthService:

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def google_login(self, credential: str) -> dict:
        """Google ID Token 검증 후 JWT 발급"""
        google_info = self._verify_google_token(credential)

        user = self._upsert_user(
            google_id=google_info["sub"],
            email=google_info["email"],
            name=google_info.get("name", ""),
            profile_image=google_info.get("picture"),
        )

        token = self._create_jwt(user)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "profile_image": user.profile_image,
            },
        }

    def get_current_user(self, token: str) -> Optional[User]:
        """JWT에서 유저 조회"""
        payload = self._verify_jwt(token)
        if payload is None:
            return None
        return self._user_repo.find_by_google_id(payload["google_id"])

    def _verify_google_token(self, credential: str) -> dict:
        """Google ID Token 검증"""
        try:
            idinfo = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
            return idinfo
        except ValueError as e:
            raise ValueError(f"Invalid Google token: {e}")

    def _upsert_user(self, google_id: str, email: str, name: str, profile_image: Optional[str]) -> User:
        """유저 조회 후 없으면 생성, 있으면 프로필 업데이트"""
        user = self._user_repo.find_by_google_id(google_id)
        if user is None:
            user = User(
                google_id=google_id,
                email=email,
                name=name,
                profile_image=profile_image,
            )
        else:
            user.name = name
            user.email = email
            user.profile_image = profile_image
        return self._user_repo.save(user)

    def _create_jwt(self, user: User) -> str:
        """자체 JWT 생성"""
        payload = {
            "google_id": user.google_id,
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    def _verify_jwt(self, token: str) -> Optional[dict]:
        """JWT 검증"""
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        except jwt.PyJWTError:
            return None
