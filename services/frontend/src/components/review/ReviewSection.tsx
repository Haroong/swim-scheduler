import { useState } from 'react';
import { useReviews } from '../../hooks/useReviews';
import { StarRating } from './StarRating';
import { ReviewItem } from './ReviewItem';
import { ReviewForm } from './ReviewForm';

interface ReviewSectionProps {
  facilityId: number;
  facilityName: string;
}

export function ReviewSection({ facilityId }: ReviewSectionProps) {
  const { reviews, stats, loading, error, submitReview, editReview, removeReview } = useReviews(facilityId);
  const [showForm, setShowForm] = useState(false);
  const [showAll, setShowAll] = useState(false);

  const handleEdit = async (reviewId: number, password: string, rating?: number, content?: string) => {
    await editReview(reviewId, { password, rating, content });
  };

  const handleDelete = async (reviewId: number, password: string) => {
    await removeReview(reviewId, password);
  };

  return (
    <div className="space-y-3">
      {/* 헤더 + 통계 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="font-bold text-base text-slate-800">리뷰</h2>
          {stats && stats.review_count > 0 && (
            <div className="flex items-center gap-1.5">
              <StarRating rating={Math.round(stats.average_rating)} readOnly size="sm" />
              <span className="text-sm font-semibold text-slate-700">{stats.average_rating}</span>
              <span className="text-sm text-slate-400">({stats.review_count})</span>
            </div>
          )}
        </div>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-ocean-600 hover:bg-ocean-50 rounded-lg transition-colors border border-ocean-200"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            리뷰 작성
          </button>
        )}
      </div>

      {/* 작성 폼 */}
      {showForm && (
        <ReviewForm
          onSubmit={submitReview}
          onCancel={() => setShowForm(false)}
        />
      )}

      {/* 리뷰 목록 */}
      {loading ? (
        <div className="text-center py-8 text-sm text-slate-400">불러오는 중...</div>
      ) : error ? (
        <div className="text-center py-8 text-sm text-red-400">{error}</div>
      ) : reviews.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-sm text-slate-400">아직 리뷰가 없습니다.</p>
          {!showForm && (
            <button
              onClick={() => setShowForm(true)}
              className="mt-2 text-sm text-ocean-500 hover:text-ocean-600 font-medium"
            >
              첫 리뷰를 작성해보세요
            </button>
          )}
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {(showAll ? reviews : reviews.slice(0, 2)).map((review) => (
              <ReviewItem
                key={review.id}
                review={review}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>
          {!showAll && reviews.length > 2 && (
            <button
              onClick={() => setShowAll(true)}
              className="w-full py-2.5 text-sm font-medium text-ocean-500 hover:text-ocean-600 hover:bg-ocean-50 rounded-lg transition-colors"
            >
              리뷰 더보기 ({reviews.length})
            </button>
          )}
        </>
      )}
    </div>
  );
}
