"""
Review Schemas
리뷰 API 요청/응답 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    """리뷰 작성 요청"""
    facility_id: int
    nickname: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=4, max_length=20)
    rating: int = Field(..., ge=1, le=5)
    content: str = Field(..., min_length=1, max_length=1000)


class ReviewUpdateRequest(BaseModel):
    """리뷰 수정 요청"""
    password: str = Field(..., min_length=4, max_length=20)
    rating: Optional[int] = Field(None, ge=1, le=5)
    content: Optional[str] = Field(None, min_length=1, max_length=1000)


class ReviewDeleteRequest(BaseModel):
    """리뷰 삭제 요청"""
    password: str = Field(..., min_length=4, max_length=20)


class ReviewResponse(BaseModel):
    """리뷰 응답"""
    id: int
    facility_id: int
    nickname: str
    rating: int
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReviewStatsResponse(BaseModel):
    """리뷰 통계 응답"""
    facility_id: int
    average_rating: float
    review_count: int
