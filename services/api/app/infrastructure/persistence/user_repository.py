"""SqlAlchemy User Repository 구현체"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.user.model import User
from app.domain.user.repository import UserRepository


class SqlAlchemyUserRepository(UserRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_by_google_id(self, google_id: str) -> Optional[User]:
        stmt = select(User).where(User.google_id == google_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def save(self, user: User) -> User:
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user
