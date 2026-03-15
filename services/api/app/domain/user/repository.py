"""
User Repository Interface

유저 데이터 접근을 위한 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Optional

from app.domain.user.model import User


class UserRepository(ABC):
    """유저 Repository 인터페이스"""

    @abstractmethod
    def find_by_google_id(self, google_id: str) -> Optional[User]:
        """Google ID로 유저 조회"""
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        """유저 저장"""
        pass
