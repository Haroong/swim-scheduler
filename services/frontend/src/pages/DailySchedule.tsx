import { useState, useEffect, useCallback, useMemo } from 'react';
import { scheduleApi } from '../services/api';
import type { DailySchedule } from '../types/schedule';
import { trackFacilityView } from '../utils/analytics';
import { EmptyState } from '../components/common';
import { FacilityGrid, ScheduleDetail } from '../components/daily';
import { useFavorites } from '../hooks';

type SortOption = 'name' | 'nextSession' | 'remainingSessions';

interface FilterState {
  availableOnly: boolean;
  favoritesOnly: boolean;
  sort: SortOption;
}

const FILTER_STORAGE_KEY = 'swim-schedule-filters';

// 로컬 스토리지에서 필터 설정 불러오기
function loadFilters(): FilterState {
  try {
    const saved = localStorage.getItem(FILTER_STORAGE_KEY);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch {
    // ignore
  }
  return { availableOnly: false, favoritesOnly: false, sort: 'name' };
}

// 로컬 스토리지에 필터 설정 저장
function saveFilters(filters: FilterState) {
  try {
    localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(filters));
  } catch {
    // ignore
  }
}

// 시설의 이용 가능 여부 및 다음 세션 시간 계산
function getScheduleInfo(schedule: DailySchedule) {
  if (schedule.is_closed || schedule.sessions.length === 0) {
    return { isAvailable: false, nextSessionMinutes: Infinity, remainingSessions: 0 };
  }

  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  let isCurrentlyAvailable = false;
  let nextSessionMinutes = Infinity;
  let remainingSessions = 0;

  for (const session of schedule.sessions) {
    const [startH, startM] = session.start_time.split(':').map(Number);
    const [endH, endM] = session.end_time.split(':').map(Number);
    const startMinutes = startH * 60 + startM;
    const endMinutes = endH * 60 + endM;

    if (currentMinutes >= startMinutes && currentMinutes < endMinutes) {
      isCurrentlyAvailable = true;
      remainingSessions++;
    } else if (currentMinutes < startMinutes) {
      nextSessionMinutes = Math.min(nextSessionMinutes, startMinutes);
      remainingSessions++;
    }
  }

  return {
    isAvailable: isCurrentlyAvailable || remainingSessions > 0,
    nextSessionMinutes,
    remainingSessions,
  };
}

function DailySchedulePage() {
  const [schedules, setSchedules] = useState<DailySchedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [, setTick] = useState(0);
  const { favorites, toggleFavorite, isFavorite } = useFavorites();

  // 필터 상태
  const [filters, setFilters] = useState<FilterState>(loadFilters);

  // 선택된 수영장 (null이면 목록 표시)
  const [selectedFacilityId, setSelectedFacilityId] = useState<number | null>(null);

  // 필터 변경 핸들러
  const updateFilter = useCallback(<K extends keyof FilterState>(key: K, value: FilterState[K]) => {
    setFilters((prev) => {
      const next = { ...prev, [key]: value };
      saveFilters(next);
      return next;
    });
  }, []);

  // 필터링 및 정렬된 스케줄
  const filteredSchedules = useMemo(() => {
    let result = [...schedules];

    // 이용 가능만 필터
    if (filters.availableOnly) {
      result = result.filter((s) => {
        const info = getScheduleInfo(s);
        return info.isAvailable;
      });
    }

    // 즐겨찾기만 필터
    if (filters.favoritesOnly) {
      result = result.filter((s) => favorites.includes(s.facility_id));
    }

    // 정렬
    result.sort((a, b) => {
      // 휴관 시설은 항상 뒤로
      if (a.is_closed !== b.is_closed) {
        return a.is_closed ? 1 : -1;
      }

      switch (filters.sort) {
        case 'nextSession': {
          const infoA = getScheduleInfo(a);
          const infoB = getScheduleInfo(b);
          return infoA.nextSessionMinutes - infoB.nextSessionMinutes;
        }
        case 'remainingSessions': {
          const infoA = getScheduleInfo(a);
          const infoB = getScheduleInfo(b);
          return infoB.remainingSessions - infoA.remainingSessions;
        }
        case 'name':
        default:
          return a.facility_name.localeCompare(b.facility_name, 'ko');
      }
    });

    return result;
  }, [schedules, filters, favorites]);

  // 오늘 날짜 (자정에 자동 갱신)
  const [today, setToday] = useState(() => new Date().toISOString().split('T')[0]);

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

  // 1분마다 리렌더 (세션 상태 갱신용)
  useEffect(() => {
    const timer = setInterval(() => {
      setTick((t) => t + 1);
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  // 자정에 날짜 갱신
  useEffect(() => {
    const scheduleMidnightUpdate = () => {
      const now = new Date();
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(0, 0, 0, 0);
      const msUntilMidnight = tomorrow.getTime() - now.getTime();

      return setTimeout(() => {
        setToday(new Date().toISOString().split('T')[0]);
        // 다음 자정을 위해 재설정
        timerId = scheduleMidnightUpdate();
      }, msUntilMidnight);
    };

    let timerId = scheduleMidnightUpdate();
    return () => clearTimeout(timerId);
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
      setError('스케줄을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = () => {
    const date = new Date(today);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    const weekday = weekdays[date.getDay()];
    return `${month}월 ${day}일 (${weekday})`;
  };

  // 선택된 수영장의 스케줄
  const selectedSchedule = selectedFacilityId
    ? schedules.find((s) => s.facility_id === selectedFacilityId)
    : null;

  // 상세 뷰 표시
  if (selectedSchedule) {
    return (
      <ScheduleDetail
        schedule={selectedSchedule}
        dateString={formatDate()}
        isFavorite={isFavorite(selectedSchedule.facility_id)}
        onToggleFavorite={() => toggleFavorite(selectedSchedule.facility_id)}
        onBack={handleBack}
      />
    );
  }

  const sortOptions: { value: SortOption; label: string }[] = [
    { value: 'name', label: '이름순' },
    { value: 'nextSession', label: '빠른 세션순' },
    { value: 'remainingSessions', label: '세션 많은순' },
  ];

  // 목록 뷰 표시
  return (
    <div className="space-y-4">
      {/* 날짜 + 필터 */}
      <div className="space-y-3">
        <div className="px-1">
          <span className="text-sm font-semibold text-slate-700">{formatDate()}</span>
        </div>

        {/* 필터 칩 */}
        {!loading && schedules.length > 0 && (
          <div className="flex flex-wrap items-center gap-2">
            {/* 이용 가능만 */}
            <button
              onClick={() => updateFilter('availableOnly', !filters.availableOnly)}
              className={`
                inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium
                transition-colors border
                ${filters.availableOnly
                  ? 'bg-emerald-100 text-emerald-700 border-emerald-300'
                  : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                }
              `}
            >
              <span className={`w-2 h-2 rounded-full ${filters.availableOnly ? 'bg-emerald-500' : 'bg-slate-300'}`} />
              이용 가능
            </button>

            {/* 즐겨찾기만 */}
            <button
              onClick={() => updateFilter('favoritesOnly', !filters.favoritesOnly)}
              className={`
                inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium
                transition-colors border
                ${filters.favoritesOnly
                  ? 'bg-amber-100 text-amber-700 border-amber-300'
                  : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                }
              `}
            >
              <svg className={`w-4 h-4 ${filters.favoritesOnly ? 'text-amber-500' : 'text-slate-400'}`} fill={filters.favoritesOnly ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              즐겨찾기
            </button>

            {/* 정렬 드롭다운 */}
            <div className="relative ml-auto">
              <select
                value={filters.sort}
                onChange={(e) => updateFilter('sort', e.target.value as SortOption)}
                className="appearance-none bg-white border border-slate-200 rounded-full pl-3 pr-8 py-1.5 text-sm text-slate-600 hover:border-slate-300 focus:outline-none focus:ring-2 focus:ring-ocean-500 focus:border-transparent cursor-pointer"
              >
                {sortOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
              <svg className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        )}
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
          message="오늘 운영하는 수영장이 없습니다."
          icon="minus"
        />
      ) : filteredSchedules.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-slate-400 mb-3">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <p className="text-slate-500 text-sm mb-3">조건에 맞는 수영장이 없습니다</p>
          <button
            onClick={() => {
              setFilters({ availableOnly: false, favoritesOnly: false, sort: 'name' });
              saveFilters({ availableOnly: false, favoritesOnly: false, sort: 'name' });
            }}
            className="text-sm text-ocean-600 hover:text-ocean-700 font-medium"
          >
            필터 초기화
          </button>
        </div>
      ) : (
        <FacilityGrid
          schedules={filteredSchedules}
          favorites={favorites}
          onSelectFacility={handleSelectFacility}
          toggleFavorite={toggleFavorite}
        />
      )}
    </div>
  );
}

export default DailySchedulePage;
