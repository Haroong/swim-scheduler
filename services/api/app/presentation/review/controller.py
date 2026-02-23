"""
Review API Controller

리뷰 관련 API 엔드포인트
"""
from typing import List
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session

from app.application.review.service import ReviewService
from app.presentation.review.schema import (
    ReviewCreateRequest,
    ReviewUpdateRequest,
    ReviewDeleteRequest,
    ReviewResponse,
    ReviewStatsResponse,
)
from app.infrastructure import get_db

router = APIRouter()


@router.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    facility_id: int = Query(..., description="시설 ID"),
    db: Session = Depends(get_db),
):
    """시설별 리뷰 목록 조회 (최신순)"""
    reviews = ReviewService.get_reviews(db, facility_id)
    return reviews


@router.get("/reviews/stats", response_model=ReviewStatsResponse)
async def get_review_stats(
    facility_id: int = Query(..., description="시설 ID"),
    db: Session = Depends(get_db),
):
    """시설별 리뷰 통계 (평균 별점, 리뷰 수)"""
    return ReviewService.get_review_stats(db, facility_id)


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    body: ReviewCreateRequest,
    db: Session = Depends(get_db),
):
    """리뷰 작성"""
    review = ReviewService.create_review(
        db,
        facility_id=body.facility_id,
        nickname=body.nickname,
        password=body.password,
        rating=body.rating,
        content=body.content,
    )
    return review


@router.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    body: ReviewUpdateRequest,
    db: Session = Depends(get_db),
):
    """리뷰 수정 (비밀번호 검증)"""
    try:
        result = ReviewService.update_review(
            db,
            review_id=review_id,
            password=body.password,
            rating=body.rating,
            content=body.content,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if result is None:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    return result


@router.delete("/reviews/{review_id}", status_code=204)
async def delete_review(
    review_id: int,
    body: ReviewDeleteRequest,
    db: Session = Depends(get_db),
):
    """리뷰 삭제 (비밀번호 검증)"""
    try:
        result = ReviewService.delete_review(
            db,
            review_id=review_id,
            password=body.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if result is None:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
