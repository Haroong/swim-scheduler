import { useState } from 'react';
import { trackFavoriteToggle } from '../../utils/analytics';
import { DateTab } from './DateTab';
import { MonthlyTab } from './MonthlyTab';

interface FacilityDetailProps {
  facilityId: number;
  facilityName: string;
  address?: string | null;
  websiteUrl?: string | null;
  isFavorite: boolean;
  onToggleFavorite: () => void;
  onBack: () => void;
}

type TabType = 'date' | 'monthly';

export function FacilityDetail({
  facilityId,
  facilityName,
  address,
  websiteUrl,
  isFavorite,
  onToggleFavorite,
  onBack,
}: FacilityDetailProps) {
  const [activeTab, setActiveTab] = useState<TabType>('date');

  const handleWebsiteClick = () => {
    if (websiteUrl) {
      window.open(websiteUrl, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className="space-y-4">
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

        {/* 공식 웹사이트 버튼 */}
        {websiteUrl && (
          <button
            onClick={handleWebsiteClick}
            className="min-w-11 min-h-11 flex items-center justify-center rounded-lg text-slate-400 hover:text-ocean-500 hover:bg-ocean-50 transition-colors"
            aria-label="공식 웹사이트"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
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

      {/* 탭 네비게이션 */}
      <div className="flex bg-slate-100 rounded-xl p-1">
        <button
          onClick={() => setActiveTab('date')}
          className={`
            flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all
            ${activeTab === 'date'
              ? 'bg-white text-slate-800 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
            }
          `}
        >
          <span className="flex items-center justify-center gap-1.5">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            날짜 선택
          </span>
        </button>
        <button
          onClick={() => setActiveTab('monthly')}
          className={`
            flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all
            ${activeTab === 'monthly'
              ? 'bg-white text-slate-800 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
            }
          `}
        >
          <span className="flex items-center justify-center gap-1.5">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            월간 정보
          </span>
        </button>
      </div>

      {/* 탭 컨텐츠 */}
      {activeTab === 'date' ? (
        <DateTab facilityId={facilityId} facilityName={facilityName} />
      ) : (
        <MonthlyTab facilityName={facilityName} />
      )}
    </div>
  );
}
