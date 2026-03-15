"""
User Model

Google OAuth 인증 유저
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func

from app.domain.base import Base


class User(Base):
    """유저 모델"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    google_id = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    profile_image = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.current_timestamp())

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
