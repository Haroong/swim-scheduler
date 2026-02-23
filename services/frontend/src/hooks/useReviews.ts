import { useState, useEffect, useCallback } from 'react';
import { reviewApi } from '../services/api';
import type { Review, ReviewStats, ReviewCreatePayload, ReviewUpdatePayload } from '../types/review';

export function useReviews(facilityId: number) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [reviewsData, statsData] = await Promise.all([
        reviewApi.getReviews(facilityId),
        reviewApi.getReviewStats(facilityId),
      ]);
      setReviews(reviewsData);
      setStats(statsData);
    } catch {
      setError('리뷰를 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  }, [facilityId]);

  useEffect(() => {
    load();
  }, [load]);

  const submitReview = useCallback(
    async (payload: Omit<ReviewCreatePayload, 'facility_id'>) => {
      await reviewApi.createReview({ ...payload, facility_id: facilityId });
      await load();
    },
    [facilityId, load]
  );

  const editReview = useCallback(
    async (reviewId: number, payload: ReviewUpdatePayload) => {
      await reviewApi.updateReview(reviewId, payload);
      await load();
    },
    [load]
  );

  const removeReview = useCallback(
    async (reviewId: number, password: string) => {
      await reviewApi.deleteReview(reviewId, password);
      await load();
    },
    [load]
  );

  return { reviews, stats, loading, error, submitReview, editReview, removeReview, reload: load };
}
