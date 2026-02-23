import { useState } from 'react';
import { StarRating } from './StarRating';

interface ReviewFormProps {
  onSubmit: (data: { nickname: string; password: string; rating: number; content: string }) => Promise<void>;
  onCancel: () => void;
}

export function ReviewForm({ onSubmit, onCancel }: ReviewFormProps) {
  const [nickname, setNickname] = useState('');
  const [password, setPassword] = useState('');
  const [rating, setRating] = useState(0);
  const [content, setContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!nickname.trim()) {
      setError('닉네임을 입력해주세요.');
      return;
    }
    if (password.length < 4) {
      setError('비밀번호는 4자 이상이어야 합니다.');
      return;
    }
    if (rating === 0) {
      setError('별점을 선택해주세요.');
      return;
    }
    if (!content.trim()) {
      setError('리뷰 내용을 입력해주세요.');
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await onSubmit({ nickname: nickname.trim(), password, rating, content: content.trim() });
      setNickname('');
      setPassword('');
      setRating(0);
      setContent('');
      onCancel();
    } catch {
      setError('리뷰 작성 중 오류가 발생했습니다.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 space-y-3">
      <h3 className="font-semibold text-sm text-slate-800">리뷰 작성</h3>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-slate-500 mb-1 block">닉네임</label>
          <input
            type="text"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            maxLength={50}
            placeholder="닉네임"
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-300"
          />
        </div>
        <div>
          <label className="text-xs text-slate-500 mb-1 block">비밀번호</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            maxLength={20}
            placeholder="수정/삭제 시 필요"
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-300"
          />
        </div>
      </div>

      <div>
        <label className="text-xs text-slate-500 mb-1 block">별점</label>
        <StarRating rating={rating} onChange={setRating} />
      </div>

      <div>
        <label className="text-xs text-slate-500 mb-1 block">내용</label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          maxLength={1000}
          rows={3}
          placeholder="이용 경험을 공유해주세요"
          className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-300 resize-none"
        />
        <div className="text-right text-xs text-slate-400 mt-1">{content.length}/1000</div>
      </div>

      {error && <p className="text-xs text-red-500">{error}</p>}

      <div className="flex gap-2 justify-end">
        <button onClick={onCancel} className="px-3 py-1.5 text-sm text-slate-500 hover:bg-slate-100 rounded-lg transition-colors">
          취소
        </button>
        <button
          onClick={handleSubmit}
          disabled={submitting}
          className="px-4 py-1.5 text-sm font-medium text-white bg-ocean-500 hover:bg-ocean-600 rounded-lg transition-colors disabled:opacity-50"
        >
          {submitting ? '작성 중...' : '작성'}
        </button>
      </div>
    </div>
  );
}
