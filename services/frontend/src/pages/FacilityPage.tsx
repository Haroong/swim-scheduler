import { useState, useEffect, useCallback, useMemo } from 'react';
import { scheduleApi } from '../services/api';
import type { DailySchedule, Session } from '../types/schedule';
import { trackFacilityView, trackFavoriteToggle } from '../utils/analytics';
import { EmptyState } from '../components/common';
import { FacilityDetail } from '../components/facility';
import { useFavorites } from '../hooks';

// --- 상태 계산 유틸리티 (daily/FacilityCard.tsx 패턴) ---

type AvailabilityStatus =
  | { status: 'closed'; label: string }
  | { status: 'available'; label: string; session: Session }
  | { status: 'upcoming'; label: string; session: Session }
  | { status: 'ended'; label: string };

function getAvailabilityStatus(schedule: DailySchedule): AvailabilityStatus {
  if (schedule.is_closed) {
    return { status: 'closed', label: schedule.closure_reason || '휴관' };
  }

  if (schedule.sessions.length === 0) {
    return { status: 'closed', label: '세션 없음' };
  }

  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  const currentSession = schedule.sessions.find((s) => {
    const [startH, startM] = s.start_time.split(':').map(Number);
    const [endH, endM] = s.end_time.split(':').map(Number);
    const startMinutes = startH * 60 + startM;
    const endMinutes = endH * 60 + endM;
    return currentMinutes >= startMinutes && currentMinutes < endMinutes;
  });

  if (currentSession) {
    return { status: 'available', label: '이용 가능', session: currentSession };
  }

  const nextSession = schedule.sessions.find((s) => {
    const [startH, startM] = s.start_time.split(':').map(Number);
    const startMinutes = startH * 60 + startM;
    return currentMinutes < startMinutes;
  });

  if (nextSession) {
    return { status: 'upcoming', label: `${nextSession.start_time.substring(0, 5)}~`, session: nextSession };
  }

  return { status: 'ended', label: '오늘 종료' };
}

function countRemainingSessions(schedule: DailySchedule): number {
  if (schedule.is_closed) return 0;

  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  return schedule.sessions.filter((session) => {
    const [endHour, endMin] = session.end_time.split(':').map(Number);
    const endMinutes = endHour * 60 + endMin;
    return currentMinutes < endMinutes;
  }).length;
}

const statusStyles = {
  available: {
    badge: 'bg-emerald-100 text-emerald-700',
    dot: 'bg-emerald-500',
  },
  upcoming: {
    badge: 'bg-amber-100 text-amber-700',
    dot: 'bg-amber-500',
  },
  ended: {
    badge: 'bg-slate-100 text-slate-500',
    dot: 'bg-slate-400',
  },
  closed: {
    badge: 'bg-slate-100 text-slate-400',
    dot: 'bg-slate-300',
  },
};

// --- SimpleFacilityCard (리디자인) ---

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
  const availability = getAvailabilityStatus(schedule);
  const remainingCount = countRemainingSessions(schedule);
  const style = statusStyles[availability.status];
  const isClosed = availability.status === 'closed';

  return (
    <div
      className={`
        relative rounded-xl border overflow-hidden
        transition-all active:scale-[0.98]
        ${isClosed
          ? 'bg-slate-100 border-slate-200 border-dashed'
          : 'bg-white hover:shadow-md hover:border-ocean-200'
        }
        ${isFavorite && !isClosed ? 'border-amber-300 ring-1 ring-amber-200' : ''}
        ${!isFavorite && !isClosed ? 'border-slate-200' : ''}
      `}
    >
      <button
        onClick={onClick}
        className="w-full p-4 text-left"
      >
        <div className="flex items-start gap-3">
          {/* 휴관 아이콘 */}
          {isClosed && (
            <div className="flex-shrink-0 w-8 h-8 bg-slate-200 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
          )}

          <div className="flex-1 min-w-0">
            <h3 className={`font-bold text-base truncate pr-8 ${isClosed ? 'text-slate-400' : 'text-slate-800'}`}>
              {schedule.facility_name}
            </h3>

            {/* 주소 */}
            {schedule.address && (
              <div className="flex items-center gap-1 mt-1">
                <svg className="w-3 h-3 text-slate-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span className="text-xs text-slate-400 truncate">{schedule.address}</span>
              </div>
            )}

            {/* 상태 배지 */}
            <div className="flex items-center gap-2 mt-1.5">
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${style.badge}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
                {availability.status === 'available' ? '이용 가능' : availability.label}
              </span>

              {availability.status === 'available' && 'session' in availability && (
                <span className="text-xs text-slate-400">
                  ~{availability.session.end_time.substring(0, 5)}까지
                </span>
              )}
              {availability.status === 'upcoming' && remainingCount > 0 && (
                <span className="text-xs text-slate-400">
                  오늘 {remainingCount}개 세션
                </span>
              )}
              {availability.status === 'ended' && (
                <span className="text-xs text-slate-400">
                  {schedule.sessions.length}개 세션 모두 종료
                </span>
              )}
            </div>
          </div>
        </div>
      </button>

      {/* 즐겨찾기 버튼 - 44x44 터치 영역 확보 */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          trackFavoriteToggle(schedule.facility_id, schedule.facility_name, isFavorite ? 'remove' : 'add');
          onToggleFavorite();
        }}
        className={`
          absolute top-1 right-1 min-w-11 min-h-11 flex items-center justify-center rounded-full transition-colors
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

// --- SimpleFacilityGrid (온보딩 추가) ---

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
      {/* 즐겨찾기 온보딩 (즐겨찾기가 없을 때만) */}
      {favoriteSchedules.length === 0 && otherSchedules.length > 0 && (
        <div className="flex items-center gap-3 px-4 py-3 bg-amber-50 border border-amber-200 rounded-xl">
          <div className="flex-shrink-0 w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </div>
          <p className="text-sm text-amber-800">
            자주 가는 수영장의 <span className="font-medium">★</span>를 눌러 즐겨찾기하면 여기에 바로 나타나요
          </p>
        </div>
      )}

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

// --- 메인 페이지 ---

function FacilityPage() {
  const [schedules, setSchedules] = useState<DailySchedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { favorites, toggleFavorite, isFavorite } = useFavorites();

  // 검색 & 필터
  const [searchQuery, setSearchQuery] = useState('');
  const [favoritesOnly, setFavoritesOnly] = useState(false);

  // 선택된 수영장 (null이면 목록 표시)
  const [selectedFacilityId, setSelectedFacilityId] = useState<number | null>(null);

  // 오늘 날짜
  const [today] = useState(() => new Date().toISOString().split('T')[0]);

  const formatDate = () => {
    const date = new Date(today + 'T00:00:00');
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    const weekday = weekdays[date.getDay()];
    return `${month}월 ${day}일 (${weekday})`;
  };

  // 필터링된 스케줄
  const filteredSchedules = useMemo(() => {
    let result = schedules;

    if (searchQuery.trim()) {
      const query = searchQuery.trim().toLowerCase();
      result = result.filter((s) =>
        s.facility_name.toLowerCase().includes(query)
      );
    }

    if (favoritesOnly) {
      result = result.filter((s) => favorites.includes(s.facility_id));
    }

    return result;
  }, [schedules, searchQuery, favoritesOnly, favorites]);

  // 필터 활성 여부
  const hasActiveFilter = searchQuery.trim() !== '' || favoritesOnly;

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

  // 필터 초기화
  const resetFilters = () => {
    setSearchQuery('');
    setFavoritesOnly(false);
  };

  // 목록 뷰 표시
  return (
    <div className="space-y-4">
      {/* 헤더 */}
      <div className="px-1">
        <h1 className="text-lg font-bold text-slate-800">시설별 일정</h1>
        <p className="text-sm text-slate-500">
          {loading ? '수영장을 선택해서 상세 일정을 확인하세요' : (
            <>
              {formatDate()} 기준 · {schedules.length}개 수영장
            </>
          )}
        </p>
      </div>

      {/* 검색 + 필터 */}
      {!loading && schedules.length > 0 && (
        <div className="space-y-2">
          {/* 검색 바 */}
          <div className="relative">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="수영장 이름으로 검색"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-9 py-2 bg-white border border-slate-200 rounded-xl text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-ocean-500 focus:border-transparent"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 w-6 h-6 flex items-center justify-center rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* 즐겨찾기 필터 칩 */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setFavoritesOnly(!favoritesOnly)}
              className={`
                inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium
                transition-colors border
                ${favoritesOnly
                  ? 'bg-amber-100 text-amber-700 border-amber-300'
                  : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                }
              `}
            >
              <svg className={`w-4 h-4 ${favoritesOnly ? 'text-amber-500' : 'text-slate-400'}`} fill={favoritesOnly ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              즐겨찾기
            </button>
          </div>
        </div>
      )}

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

      {/* 로딩 (스켈레톤) */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-xl border border-slate-200 p-4 animate-pulse">
              <div className="flex items-start gap-3">
                <div className="flex-1 min-w-0">
                  <div className="h-4 bg-slate-200 rounded w-2/3 mb-2" />
                  <div className="h-3 bg-slate-100 rounded w-1/2 mb-2" />
                  <div className="flex gap-2">
                    <div className="h-5 bg-slate-100 rounded-full w-16" />
                    <div className="h-5 bg-slate-100 rounded-full w-20" />
                  </div>
                </div>
                <div className="w-8 h-8 bg-slate-100 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      ) : schedules.length === 0 ? (
        <EmptyState
          message="등록된 수영장이 없습니다."
          icon="minus"
        />
      ) : filteredSchedules.length === 0 && hasActiveFilter ? (
        <div className="text-center py-12">
          <div className="text-slate-400 mb-3">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <p className="text-slate-500 text-sm mb-3">조건에 맞는 수영장이 없습니다</p>
          <button
            onClick={resetFilters}
            className="text-sm text-ocean-600 hover:text-ocean-700 font-medium"
          >
            필터 초기화
          </button>
        </div>
      ) : (
        <SimpleFacilityGrid
          schedules={filteredSchedules}
          favorites={favorites}
          onSelectFacility={handleSelectFacility}
          toggleFavorite={toggleFavorite}
        />
      )}
    </div>
  );
}

export default FacilityPage;
