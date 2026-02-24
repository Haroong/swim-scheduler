import { useState } from 'react';
import { trackFavoriteToggle } from '../../utils/analytics';
import { DateTab } from './DateTab';
import { MonthlyTab } from './MonthlyTab';
import { ReviewSection } from '../review/ReviewSection';
import type { Fee, Session } from '../../types/schedule';

interface FacilityDetailProps {
  facilityId: number;
  facilityName: string;
  address?: string | null;
  websiteUrl?: string | null;
  isFavorite: boolean;
  onToggleFavorite: () => void;
  onBack: () => void;
  fees?: Fee[];
  sessions?: Session[];
  crawledAt?: string | null;
  isClosed?: boolean;
  closureReason?: string | null;
}

function getStatusInfo(sessions: Session[], isClosed?: boolean, closureReason?: string | null) {
  if (isClosed) {
    return { status: 'closed' as const, label: closureReason || '휴관', badgeClass: 'bg-slate-100 text-slate-400', dotClass: 'bg-slate-300' };
  }
  if (!sessions || sessions.length === 0) {
    return { status: 'closed' as const, label: '세션 없음', badgeClass: 'bg-slate-100 text-slate-400', dotClass: 'bg-slate-300' };
  }

  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  const currentSession = sessions.find((s) => {
    const [startH, startM] = s.start_time.split(':').map(Number);
    const [endH, endM] = s.end_time.split(':').map(Number);
    return currentMinutes >= startH * 60 + startM && currentMinutes < endH * 60 + endM;
  });

  if (currentSession) {
    return { status: 'available' as const, label: '이용 가능', badgeClass: 'bg-emerald-100 text-emerald-700', dotClass: 'bg-emerald-500', session: currentSession };
  }

  const nextSession = sessions.find((s) => {
    const [startH, startM] = s.start_time.split(':').map(Number);
    return currentMinutes < startH * 60 + startM;
  });

  if (nextSession) {
    return { status: 'upcoming' as const, label: `${nextSession.start_time.substring(0, 5)}~`, badgeClass: 'bg-amber-100 text-amber-700', dotClass: 'bg-amber-500', session: nextSession };
  }

  return { status: 'ended' as const, label: '오늘 종료', badgeClass: 'bg-slate-100 text-slate-500', dotClass: 'bg-slate-400' };
}

export function FacilityDetail({
  facilityId,
  facilityName,
  address,
  isFavorite,
  onToggleFavorite,
  onBack,
  fees,
  sessions,
  crawledAt,
  isClosed,
  closureReason,
}: FacilityDetailProps) {
  const [showMonthly, setShowMonthly] = useState(false);

  const handleDirections = () => {
    if (address) {
      const url = `https://map.naver.com/v5/search/${encodeURIComponent(facilityName + ' ' + address)}`;
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  const statusInfo = getStatusInfo(sessions || [], isClosed, closureReason);
  const representativeFee = fees && fees.length > 0
    ? (fees.find(f => f.category.includes('일반') || f.category.includes('성인')) || fees[0])
    : null;
  const maxLanes = sessions?.reduce((max, s) => Math.max(max, s.lanes || 0), 0) || 0;

  return (
    <div className="space-y-4 pb-20 sm:pb-4">
      {/* 헤더 */}
      <div className="flex items-center gap-2">
        <button
          onClick={onBack}
          className="min-w-11 min-h-11 -ml-2 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors"
          aria-label="뒤로가기"
        >
          <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <div className="flex-1 min-w-0">
          <h1 className="font-bold text-lg text-slate-800 truncate">
            {facilityName}
          </h1>
          {address && (
            <p className="text-sm text-slate-500 truncate flex items-center gap-1">
              <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {address}
            </p>
          )}
        </div>

        {/* 길찾기 버튼 */}
        {address && (
          <button
            onClick={handleDirections}
            className="hidden sm:inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-ocean-600 hover:bg-ocean-50 transition-colors border border-ocean-200"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            길찾기
          </button>
        )}

        {/* 즐겨찾기 버튼 - 44x44 터치 영역 확보 */}
        <button
          onClick={() => {
            trackFavoriteToggle(facilityId, facilityName, isFavorite ? 'remove' : 'add');
            onToggleFavorite();
          }}
          className={`
            min-w-11 min-h-11 flex items-center justify-center rounded-lg transition-colors
            ${isFavorite ? 'text-amber-500 bg-amber-50' : 'text-slate-300 hover:text-amber-400 hover:bg-amber-50'}
          `}
          aria-label={isFavorite ? '즐겨찾기 해제' : '즐겨찾기 추가'}
        >
          <svg
            className="w-5 h-5"
            fill={isFavorite ? 'currentColor' : 'none'}
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
        </button>
      </div>

      {/* 시설 요약 카드 */}
      <div className="bg-white rounded-xl border border-slate-200 p-4">
        <div className="flex items-center gap-3 mb-3">
          {/* 상태 배지 (큰) */}
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold ${statusInfo.badgeClass}`}>
            <span className={`w-2 h-2 rounded-full ${statusInfo.dotClass}`} />
            {statusInfo.label}
          </span>
          {statusInfo.status === 'available' && statusInfo.session && (
            <span className="text-sm text-slate-500">
              ~{statusInfo.session.end_time.substring(0, 5)}까지
            </span>
          )}
        </div>

        {/* 핵심 스펙 */}
        {!isClosed && (
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-slate-600">
            {sessions && sessions.length > 0 && (
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>오늘 {sessions.length}개 세션</span>
              </div>
            )}
            {maxLanes > 0 && (
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
                <span>{maxLanes}레인</span>
              </div>
            )}
            {representativeFee && (
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{representativeFee.category} {representativeFee.price.toLocaleString()}원</span>
              </div>
            )}
          </div>
        )}

      </div>

      {/* DateTab (메인 콘텐츠) */}
      <DateTab facilityId={facilityId} facilityName={facilityName} crawledAt={crawledAt} />

      {/* 리뷰 섹션 */}
      <div className="bg-white rounded-xl border border-slate-200 p-4">
        <ReviewSection facilityId={facilityId} facilityName={facilityName} />
      </div>

      {/* 월간 전체 일정 (확장 영역) */}
      <div className="border border-slate-200 rounded-xl overflow-hidden">
        <button
          onClick={() => setShowMonthly(!showMonthly)}
          className="w-full flex items-center justify-center gap-2 py-3 bg-slate-50 hover:bg-slate-100 transition-colors"
        >
          <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <span className="text-sm font-medium text-slate-600">
            월간 전체 일정 {showMonthly ? '접기' : '보기'}
          </span>
          <svg
            className={`w-4 h-4 text-slate-400 transition-transform ${showMonthly ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {showMonthly && (
          <div className="p-4 border-t border-slate-200">
            <MonthlyTab facilityName={facilityName} />
          </div>
        )}
      </div>

      {/* 모바일 하단 Sticky CTA */}
      {address && (
        <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-slate-200 sm:hidden z-40" style={{ paddingBottom: 'max(1rem, env(safe-area-inset-bottom))' }}>
          <a
            href={`https://map.naver.com/v5/search/${encodeURIComponent(facilityName + ' ' + address)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 w-full py-3 bg-ocean-500 hover:bg-ocean-600 text-white rounded-xl font-semibold text-sm transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            길찾기
          </a>
        </div>
      )}
    </div>
  );
}
