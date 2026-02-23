import { useState } from 'react';
import type { Review } from '../../types/review';
import { StarRating } from './StarRating';

interface ReviewItemProps {
  review: Review;
  onEdit: (reviewId: number, password: string, rating?: number, content?: string) => Promise<void>;
  onDelete: (reviewId: number, password: string) => Promise<void>;
}

export function ReviewItem({ review, onEdit, onDelete }: ReviewItemProps) {
  const [mode, setMode] = useState<'view' | 'edit' | 'delete'>('view');
  const [password, setPassword] = useState('');
  const [editRating, setEditRating] = useState(review.rating);
  const [editContent, setEditContent] = useState(review.content);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      return `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()}`;
    } catch {
      return '';
    }
  };

  const handleSubmit = async () => {
    if (!password) {
      setError('비밀번호를 입력해주세요.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      if (mode === 'edit') {
        await onEdit(review.id, password, editRating, editContent);
      } else {
        await onDelete(review.id, password);
      }
      resetState();
    } catch (e: unknown) {
      if (e && typeof e === 'object' && 'response' in e) {
        const axiosErr = e as { response?: { status?: number } };
        if (axiosErr.response?.status === 403) {
          setError('비밀번호가 일치하지 않습니다.');
        } else {
          setError('처리 중 오류가 발생했습니다.');
        }
      } else {
        setError('처리 중 오류가 발생했습니다.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const resetState = () => {
    setMode('view');
    setPassword('');
    setError(null);
    setEditRating(review.rating);
    setEditContent(review.content);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm text-slate-800">{review.nickname}</span>
          <StarRating rating={review.rating} readOnly size="sm" />
        </div>
        <div className="flex items-center gap-1">
          <span className="text-xs text-slate-400">
            {formatDate(review.updated_at || review.created_at)}
            {review.updated_at && ' (수정됨)'}
          </span>
          {mode === 'view' && (
            <div className="flex items-center gap-1 ml-2">
              <button
                onClick={() => setMode('edit')}
                className="text-xs text-slate-400 hover:text-slate-600 px-1.5 py-0.5 rounded hover:bg-slate-100 transition-colors"
              >
                수정
              </button>
              <button
                onClick={() => setMode('delete')}
                className="text-xs text-slate-400 hover:text-red-500 px-1.5 py-0.5 rounded hover:bg-red-50 transition-colors"
              >
                삭제
              </button>
            </div>
          )}
        </div>
      </div>

      {/* 본문 / 수정 폼 */}
      {mode === 'view' ? (
        <p className="text-sm text-slate-600 whitespace-pre-wrap">{review.content}</p>
      ) : mode === 'edit' ? (
        <div className="space-y-3 mt-3">
          <div>
            <label className="text-xs text-slate-500 mb-1 block">별점</label>
            <StarRating rating={editRating} onChange={setEditRating} />
          </div>
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            maxLength={1000}
            rows={3}
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-300 resize-none"
          />
          <div>
            <label className="text-xs text-slate-500 mb-1 block">비밀번호 확인</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="작성 시 입력한 비밀번호"
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-300"
            />
          </div>
          {error && <p className="text-xs text-red-500">{error}</p>}
          <div className="flex gap-2 justify-end">
            <button onClick={resetState} className="px-3 py-1.5 text-sm text-slate-500 hover:bg-slate-100 rounded-lg transition-colors">
              취소
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="px-3 py-1.5 text-sm font-medium text-white bg-ocean-500 hover:bg-ocean-600 rounded-lg transition-colors disabled:opacity-50"
            >
              {submitting ? '처리 중...' : '수정'}
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-3 mt-3">
          <p className="text-sm text-red-600">이 리뷰를 삭제하시겠습니까?</p>
          <div>
            <label className="text-xs text-slate-500 mb-1 block">비밀번호 확인</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="작성 시 입력한 비밀번호"
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-300"
            />
          </div>
          {error && <p className="text-xs text-red-500">{error}</p>}
          <div className="flex gap-2 justify-end">
            <button onClick={resetState} className="px-3 py-1.5 text-sm text-slate-500 hover:bg-slate-100 rounded-lg transition-colors">
              취소
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="px-3 py-1.5 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors disabled:opacity-50"
            >
              {submitting ? '처리 중...' : '삭제'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
