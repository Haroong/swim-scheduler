"""
Review API Controller

리뷰 관련 API 엔드포인트
"""
from typing import List
from fastapi import APIRouter, Query, HTTPException, Depends

from app.application.review.service import ReviewService
from app.presentation.review.schema import (
    ReviewCreateRequest,
    ReviewUpdateRequest,
    ReviewDeleteRequest,
    ReviewResponse,
    ReviewStatsResponse,
)
from app.infrastructure.persistence.dependencies import get_review_service

router = APIRouter()


@router.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    facility_id: int = Query(..., description="시설 ID"),
    service: ReviewService = Depends(get_review_service),
):
    """시설별 리뷰 목록 조회 (최신순)"""
    return service.get_reviews(facility_id)


@router.get("/reviews/stats", response_model=ReviewStatsResponse)
async def get_review_stats(
    facility_id: int = Query(..., description="시설 ID"),
    service: ReviewService = Depends(get_review_service),
):
    """시설별 리뷰 통계 (평균 별점, 리뷰 수)"""
    return service.get_review_stats(facility_id)


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    body: ReviewCreateRequest,
    service: ReviewService = Depends(get_review_service),
):
    """리뷰 작성"""
    return service.create_review(
        facility_id=body.facility_id,
        nickname=body.nickname,
        password=body.password,
        rating=body.rating,
        content=body.content,
    )


@router.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    body: ReviewUpdateRequest,
    service: ReviewService = Depends(get_review_service),
):
    """리뷰 수정 (비밀번호 검증)"""
    try:
        result = service.update_review(
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
    service: ReviewService = Depends(get_review_service),
):
    """리뷰 삭제 (비밀번호 검증)"""
    try:
        result = service.delete_review(
            review_id=review_id,
            password=body.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if result is None:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
