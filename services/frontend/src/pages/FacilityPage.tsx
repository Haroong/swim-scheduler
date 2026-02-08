import { useState, useEffect, useCallback } from 'react';
import { scheduleApi } from '../services/api';
import type { DailySchedule } from '../types/schedule';
import { trackFacilityView, trackFavoriteToggle } from '../utils/analytics';
import { EmptyState } from '../components/common';
import { FacilityDetail } from '../components/facility';
import { useFavorites } from '../hooks';

// 시설 목록용 간단한 카드
function SimpleFacilityCard({
  schedule,
  isFavorite,
  onToggleFavorite,
  onClick,
}: {
  schedule: DailySchedule;
  isFavorite: boolean;
  onToggleFavorite: () => void;
  onClick: () => void;
}) {
  return (
    <div
      className={`
        relative bg-white rounded-xl border overflow-hidden
        transition-all active:scale-[0.98] hover:shadow-md hover:border-ocean-200
        ${isFavorite ? 'border-amber-300 ring-1 ring-amber-200' : 'border-slate-200'}
      `}
    >
      <button
        onClick={onClick}
        className="w-full px-4 py-3 text-left"
      >
        <h3 className="font-bold text-base truncate pr-8 text-slate-800">
          {schedule.facility_name}
        </h3>
      </button>

      {/* 즐겨찾기 버튼 - 44x44 터치 영역 확보 */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          trackFavoriteToggle(schedule.facility_id, schedule.facility_name, isFavorite ? 'remove' : 'add');
          onToggleFavorite();
        }}
        className={`
          absolute top-1/2 -translate-y-1/2 right-1 min-w-11 min-h-11 flex items-center justify-center rounded-full transition-colors
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
  );
}

// 시설 목록 그리드
function SimpleFacilityGrid({
  schedules,
  favorites,
  onSelectFacility,
  toggleFavorite,
}: {
  schedules: DailySchedule[];
  favorites: number[];
  onSelectFacility: (facilityId: number) => void;
  toggleFavorite: (facilityId: number) => void;
}) {
  const favoriteSchedules = schedules.filter((s) => favorites.includes(s.facility_id));
  const otherSchedules = schedules.filter((s) => !favorites.includes(s.facility_id));

  return (
    <div className="space-y-6">
      {/* 즐겨찾기 섹션 */}
      {favoriteSchedules.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-4 h-4 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
            <h2 className="text-sm font-semibold text-slate-700">즐겨찾기</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {favoriteSchedules.map((schedule) => (
              <SimpleFacilityCard
                key={schedule.facility_id}
                schedule={schedule}
                isFavorite={true}
                onToggleFavorite={() => toggleFavorite(schedule.facility_id)}
                onClick={() => onSelectFacility(schedule.facility_id)}
              />
            ))}
          </div>
        </section>
      )}

      {/* 전체 수영장 섹션 */}
      {otherSchedules.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h2 className="text-sm font-semibold text-slate-700">전체 수영장</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {otherSchedules.map((schedule) => (
              <SimpleFacilityCard
                key={schedule.facility_id}
                schedule={schedule}
                isFavorite={false}
                onToggleFavorite={() => toggleFavorite(schedule.facility_id)}
                onClick={() => onSelectFacility(schedule.facility_id)}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function FacilityPage() {
  const [schedules, setSchedules] = useState<DailySchedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { favorites, toggleFavorite, isFavorite } = useFavorites();

  // 선택된 수영장 (null이면 목록 표시)
  const [selectedFacilityId, setSelectedFacilityId] = useState<number | null>(null);

  // 오늘 날짜
  const [today] = useState(() => new Date().toISOString().split('T')[0]);

  // 수영장 선택 핸들러
  const handleSelectFacility = useCallback((facilityId: number) => {
    const schedule = schedules.find((s) => s.facility_id === facilityId);
    if (schedule) {
      trackFacilityView(facilityId, schedule.facility_name);
    }
    history.pushState({ facilityId }, '');
    setSelectedFacilityId(facilityId);
  }, [schedules]);

  // 뒤로가기 핸들러
  const handleBack = useCallback(() => {
    history.back();
  }, []);

  // 브라우저 뒤로가기 지원
  useEffect(() => {
    const handlePopState = () => {
      setSelectedFacilityId(null);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  useEffect(() => {
    loadDailySchedules();
  }, [today]);

  const loadDailySchedules = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await scheduleApi.getDailySchedules(today);
      setSchedules(data);
    } catch (err) {
      setError('시설 목록을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 선택된 수영장의 스케줄
  const selectedSchedule = selectedFacilityId
    ? schedules.find((s) => s.facility_id === selectedFacilityId)
    : null;

  // 상세 뷰 표시
  if (selectedSchedule) {
    return (
      <FacilityDetail
        facilityId={selectedSchedule.facility_id}
        facilityName={selectedSchedule.facility_name}
        address={selectedSchedule.address}
        websiteUrl={selectedSchedule.website_url}
        isFavorite={isFavorite(selectedSchedule.facility_id)}
        onToggleFavorite={() => toggleFavorite(selectedSchedule.facility_id)}
        onBack={handleBack}
      />
    );
  }

  // 목록 뷰 표시
  return (
    <div className="space-y-4">
      {/* 헤더 */}
      <div className="px-1">
        <h1 className="text-lg font-bold text-slate-800">시설별 일정</h1>
        <p className="text-sm text-slate-500">수영장을 선택해서 상세 일정을 확인하세요</p>
      </div>

      {/* 에러 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
          <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span className="flex-1 text-sm text-red-700">{error}</span>
          <button
            onClick={loadDailySchedules}
            className="text-sm font-medium text-red-600 hover:text-red-700 px-3 py-1.5 rounded-lg hover:bg-red-100"
          >
            재시도
          </button>
        </div>
      )}

      {/* 로딩 */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl border border-slate-200 p-4 animate-pulse">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 bg-slate-200 rounded-lg" />
                <div className="flex-1">
                  <div className="h-4 bg-slate-200 rounded w-2/3 mb-2" />
                  <div className="h-3 bg-slate-100 rounded w-1/2" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : schedules.length === 0 ? (
        <EmptyState
          message="등록된 수영장이 없습니다."
          icon="minus"
        />
      ) : (
        <SimpleFacilityGrid
          schedules={schedules}
          favorites={favorites}
          onSelectFacility={handleSelectFacility}
          toggleFavorite={toggleFavorite}
        />
      )}
    </div>
  );
}

export default FacilityPage;
