import { useState, useEffect, useCallback, useMemo } from 'react';
import { scheduleApi } from '../services/api';
import type { DailySchedule, Session, Fee } from '../types/schedule';
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

function getNextSessionTime(schedule: DailySchedule): number | null {
  if (schedule.is_closed || schedule.sessions.length === 0) return null;
  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  for (const s of schedule.sessions) {
    const [startH, startM] = s.start_time.split(':').map(Number);
    const startMinutes = startH * 60 + startM;
    if (currentMinutes < startMinutes) return startMinutes;
  }
  return null;
}

function getRepresentativeFee(fees?: Fee[]): Fee | null {
  if (!fees || fees.length === 0) return null;
  const general = fees.find(f => f.category.includes('일반') || f.category.includes('성인'));
  return general || fees[0];
}

function getMaxLanes(sessions: Session[]): number | null {
  let maxLanes = 0;
  for (const s of sessions) {
    if (s.lanes && s.lanes > maxLanes) maxLanes = s.lanes;
  }
  return maxLanes > 0 ? maxLanes : null;
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

type SortOption = 'name' | 'nextSession' | 'remainingSessions';

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
  const representativeFee = getRepresentativeFee(schedule.fees);
  const maxLanes = getMaxLanes(schedule.sessions);

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
        {/* 상태 배지 (최상단) */}
        <div className="flex items-center gap-2 mb-2">
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
              <div className="flex items-center gap-1 mt-0.5">
                <svg className="w-3 h-3 text-slate-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span className="text-xs text-slate-400 truncate">{schedule.address}</span>
              </div>
            )}

            {/* 현재/다음 세션 시간 + 스펙 (비휴관일만) */}
            {!isClosed && schedule.sessions.length > 0 && (
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2">
                {/* 현재 세션 시간 */}
                {availability.status === 'available' && 'session' in availability && (
                  <span className="text-xs text-emerald-600 font-medium">
                    {availability.session.start_time.substring(0, 5)}-{availability.session.end_time.substring(0, 5)}
                    {availability.session.capacity && ` · ${availability.session.capacity}명`}
                  </span>
                )}
                {/* 다음 세션 시간 */}
                {availability.status === 'upcoming' && 'session' in availability && (
                  <span className="text-xs text-amber-600 font-medium">
                    다음 {availability.session.start_time.substring(0, 5)}-{availability.session.end_time.substring(0, 5)}
                    {availability.session.capacity && ` · ${availability.session.capacity}명`}
                  </span>
                )}
                {/* 레인 수 */}
                {maxLanes && (
                  <span className="text-xs text-slate-400">{maxLanes}레인</span>
                )}
                {/* 대표 요금 */}
                {representativeFee && (
                  <span className="text-xs text-slate-400">
                    {representativeFee.category} {representativeFee.price.toLocaleString()}원
                  </span>
                )}
              </div>
            )}

            {/* CTA */}
            {!isClosed && (
              <div className="mt-2">
                <span className="text-xs font-medium text-ocean-500">일정 보기 →</span>
              </div>
            )}
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

// --- 상태 요약 바 ---

function StatusSummaryBar({
  schedules,
  activeStatusFilter,
  onStatusFilter,
}: {
  schedules: DailySchedule[];
  activeStatusFilter: string | null;
  onStatusFilter: (status: string | null) => void;
}) {
  const counts = useMemo(() => {
    const result = { available: 0, upcoming: 0, ended: 0, closed: 0 };
    schedules.forEach((s) => {
      const { status } = getAvailabilityStatus(s);
      result[status]++;
    });
    return result;
  }, [schedules]);

  const items: { key: string; label: string; count: number; dotClass: string; activeClass: string }[] = [
    { key: 'available', label: '이용가능', count: counts.available, dotClass: 'bg-emerald-500', activeClass: 'bg-emerald-50 border-emerald-300 text-emerald-700' },
    { key: 'upcoming', label: '예정', count: counts.upcoming, dotClass: 'bg-amber-500', activeClass: 'bg-amber-50 border-amber-300 text-amber-700' },
    { key: 'ended', label: '종료', count: counts.ended, dotClass: 'bg-slate-400', activeClass: 'bg-slate-100 border-slate-300 text-slate-600' },
    { key: 'closed', label: '휴관', count: counts.closed, dotClass: 'bg-slate-300', activeClass: 'bg-slate-100 border-slate-300 text-slate-500' },
  ];

  return (
    <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-hide" style={{ scrollbarWidth: 'none' }}>
      {items.map((item) => (
        <button
          key={item.key}
          onClick={() => onStatusFilter(activeStatusFilter === item.key ? null : item.key)}
          className={`
            inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium
            border transition-colors whitespace-nowrap flex-shrink-0
            ${activeStatusFilter === item.key
              ? item.activeClass
              : 'bg-white border-slate-200 text-slate-500 hover:border-slate-300'
            }
          `}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${item.dotClass}`} />
          {item.count} {item.label}
        </button>
      ))}
    </div>
  );
}

// --- SimpleFacilityGrid (구조 개편: 활성 / 휴관 분리) ---

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
  const favoriteSchedules = schedules.filter((s) => favorites.includes(s.facility_id) && !s.is_closed);
  const activeSchedules = schedules.filter((s) => !favorites.includes(s.facility_id) && !s.is_closed);
  const closedSchedules = schedules.filter((s) => s.is_closed);

  return (
    <div className="space-y-6">
      {/* 즐겨찾기 온보딩 (즐겨찾기가 없을 때만) */}
      {favoriteSchedules.length === 0 && (activeSchedules.length > 0 || closedSchedules.length > 0) && (
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

      {/* 전체 수영장 섹션 (활성만) */}
      {activeSchedules.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h2 className="text-sm font-semibold text-slate-700">전체 수영장</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {activeSchedules.map((schedule) => (
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

      {/* 휴관 시설 섹션 */}
      {closedSchedules.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <h2 className="text-sm font-semibold text-slate-400">휴관 시설</h2>
            <span className="text-xs text-slate-400">{closedSchedules.length}개</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {closedSchedules.map((schedule) => (
              <SimpleFacilityCard
                key={schedule.facility_id}
                schedule={schedule}
                isFavorite={favorites.includes(schedule.facility_id)}
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
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [districtFilter, setDistrictFilter] = useState<string | null>(null);
  const [sortOption, setSortOption] = useState<SortOption>('name');
  const [availableOnly, setAvailableOnly] = useState(false);

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

  // 지역(구) 추출
  const districts = useMemo(() => {
    const set = new Set<string>();
    schedules.forEach(s => {
      const match = s.address?.match(/(?:성남시\s+)?(\S+구)/);
      if (match) set.add(match[1]);
    });
    return Array.from(set).sort();
  }, [schedules]);

  // 필터링된 스케줄
  const filteredSchedules = useMemo(() => {
    let result = schedules;

    // 텍스트 검색 (이름 + 주소)
    if (searchQuery.trim()) {
      const query = searchQuery.trim().toLowerCase();
      result = result.filter((s) =>
        s.facility_name.toLowerCase().includes(query) ||
        (s.address && s.address.toLowerCase().includes(query))
      );
    }

    if (favoritesOnly) {
      result = result.filter((s) => favorites.includes(s.facility_id));
    }

    // 상태 필터
    if (statusFilter) {
      result = result.filter((s) => {
        const { status } = getAvailabilityStatus(s);
        return status === statusFilter;
      });
    }

    // 이용가능만 필터
    if (availableOnly) {
      result = result.filter((s) => !s.is_closed);
    }

    // 지역 필터
    if (districtFilter) {
      result = result.filter((s) =>
        s.address?.includes(districtFilter)
      );
    }

    // 정렬
    result = [...result].sort((a, b) => {
      switch (sortOption) {
        case 'nextSession': {
          const aNext = getNextSessionTime(a);
          const bNext = getNextSessionTime(b);
          if (aNext === null && bNext === null) return a.facility_name.localeCompare(b.facility_name);
          if (aNext === null) return 1;
          if (bNext === null) return -1;
          return aNext - bNext;
        }
        case 'remainingSessions': {
          const aCount = countRemainingSessions(a);
          const bCount = countRemainingSessions(b);
          if (bCount !== aCount) return bCount - aCount;
          return a.facility_name.localeCompare(b.facility_name);
        }
        case 'name':
        default:
          return a.facility_name.localeCompare(b.facility_name);
      }
    });

    return result;
  }, [schedules, searchQuery, favoritesOnly, favorites, statusFilter, availableOnly, districtFilter, sortOption]);

  // 필터 활성 여부
  const hasActiveFilter = searchQuery.trim() !== '' || favoritesOnly || statusFilter !== null || availableOnly || districtFilter !== null;

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
        fees={selectedSchedule.fees}
        sessions={selectedSchedule.sessions}
        crawledAt={selectedSchedule.crawled_at}
        isClosed={selectedSchedule.is_closed}
        closureReason={selectedSchedule.closure_reason}
      />
    );
  }

  // 필터 초기화
  const resetFilters = () => {
    setSearchQuery('');
    setFavoritesOnly(false);
    setStatusFilter(null);
    setAvailableOnly(false);
    setDistrictFilter(null);
    setSortOption('name');
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
              성남시 공공 시설 공식 공지 기반 · {formatDate()} · {schedules.length}개 수영장
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
              placeholder="수영장 이름 또는 주소로 검색"
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

          {/* 상태 요약 바 */}
          <StatusSummaryBar
            schedules={schedules}
            activeStatusFilter={statusFilter}
            onStatusFilter={setStatusFilter}
          />

          {/* 필터 칩 행 */}
          <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide" style={{ scrollbarWidth: 'none' }}>
            {/* 즐겨찾기 필터 */}
            <button
              onClick={() => setFavoritesOnly(!favoritesOnly)}
              className={`
                inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium
                transition-colors border whitespace-nowrap flex-shrink-0
                ${favoritesOnly
                  ? 'bg-amber-100 text-amber-700 border-amber-300'
                  : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                }
              `}
            >
              <svg className={`w-3.5 h-3.5 ${favoritesOnly ? 'text-amber-500' : 'text-slate-400'}`} fill={favoritesOnly ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              즐겨찾기
            </button>

            {/* 이용가능만 토글 */}
            <button
              onClick={() => setAvailableOnly(!availableOnly)}
              className={`
                inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium
                transition-colors border whitespace-nowrap flex-shrink-0
                ${availableOnly
                  ? 'bg-emerald-100 text-emerald-700 border-emerald-300'
                  : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                }
              `}
            >
              이용가능만
            </button>

            {/* 지역 필터 칩 */}
            {districts.map((district) => (
              <button
                key={district}
                onClick={() => setDistrictFilter(districtFilter === district ? null : district)}
                className={`
                  inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium
                  transition-colors border whitespace-nowrap flex-shrink-0
                  ${districtFilter === district
                    ? 'bg-ocean-100 text-ocean-700 border-ocean-300'
                    : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                  }
                `}
              >
                {district}
              </button>
            ))}

            {/* 구분선 */}
            <div className="w-px h-5 bg-slate-200 flex-shrink-0" />

            {/* 정렬 옵션 */}
            <select
              value={sortOption}
              onChange={(e) => setSortOption(e.target.value as SortOption)}
              className="px-3 py-1.5 rounded-full text-xs font-medium border border-slate-200 bg-white text-slate-600 focus:outline-none focus:ring-2 focus:ring-ocean-500 flex-shrink-0"
            >
              <option value="name">이름순</option>
              <option value="nextSession">다음 세션 빠른순</option>
              <option value="remainingSessions">남은 세션 많은순</option>
            </select>
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
