import { useState, useEffect, useMemo, useRef } from 'react';
import { scheduleApi } from '../services/api';
import type { DailySchedule, Session, Facility } from '../types/schedule';
import { openSourceUrl } from '../utils/urlUtils';
import { trackFilterUse } from '../utils/analytics';
import { EmptyState, Badge } from '../components/common';

// ===== Filter Drawer 컴포넌트 =====
function FilterDrawer({
  isOpen,
  onClose,
  facilities,
  selectedFacility,
  onFacilityChange,
}: {
  isOpen: boolean;
  onClose: () => void;
  facilities: Facility[];
  selectedFacility: string;
  onFacilityChange: (value: string) => void;
}) {
  if (!isOpen) return null;

  return (
    <>
      {/* 배경 오버레이 */}
      <div
        className="fixed inset-0 bg-black/40 z-40 transition-opacity"
        onClick={onClose}
      />

      {/* 드로어 패널 */}
      <div className="fixed bottom-0 left-0 right-0 bg-white rounded-t-2xl z-50 shadow-xl animate-slide-up">
        {/* 핸들 */}
        <div className="flex justify-center py-3">
          <div className="w-10 h-1 bg-slate-300 rounded-full" />
        </div>

        {/* 헤더 */}
        <div className="flex items-center justify-between px-4 pb-3 border-b border-slate-100">
          <h3 className="text-lg font-bold text-slate-800">수영장 필터</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 필터 내용 */}
        <div className="p-4 max-h-[60vh] overflow-y-auto">
          <div className="space-y-2">
            <button
              onClick={() => {
                onFacilityChange('');
                onClose();
              }}
              className={`w-full text-left px-4 py-3 rounded-xl transition-colors ${
                selectedFacility === ''
                  ? 'bg-ocean-500 text-white'
                  : 'bg-slate-50 hover:bg-slate-100 text-slate-700'
              }`}
            >
              전체 수영장
            </button>
            {facilities.map((facility) => (
              <button
                key={facility.facility_name}
                onClick={() => {
                  onFacilityChange(facility.facility_name);
                  onClose();
                }}
                className={`w-full text-left px-4 py-3 rounded-xl transition-colors ${
                  selectedFacility === facility.facility_name
                    ? 'bg-ocean-500 text-white'
                    : 'bg-slate-50 hover:bg-slate-100 text-slate-700'
                }`}
              >
                {facility.facility_name}
              </button>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

// ===== FAB 필터 버튼 =====
function FilterFAB({
  onClick,
  hasFilter,
}: {
  onClick: () => void;
  hasFilter: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 w-14 h-14 bg-ocean-500 hover:bg-ocean-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all flex items-center justify-center z-30"
    >
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
      </svg>
      {hasFilter && (
        <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
          !
        </span>
      )}
    </button>
  );
}

// ===== 유틸리티 함수 =====

// 현재 시간 기준 세션 상태 판단
function getSessionStatus(session: Session, selectedDate: string): 'past' | 'upcoming' {
  const now = new Date();
  const today = now.toISOString().split('T')[0];

  if (selectedDate !== today) return 'upcoming';

  const currentMinutes = now.getHours() * 60 + now.getMinutes();
  const [endHour, endMin] = session.end_time.split(':').map(Number);
  const endMinutes = endHour * 60 + endMin;

  return currentMinutes >= endMinutes ? 'past' : 'upcoming';
}

// 다음 이용 가능한 세션 인덱스 찾기
function findNextSessionIndex(sessions: Session[], selectedDate: string): number {
  const now = new Date();
  const today = now.toISOString().split('T')[0];

  if (selectedDate !== today) return -1;

  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  for (let i = 0; i < sessions.length; i++) {
    const [startHour, startMin] = sessions[i].start_time.split(':').map(Number);
    const startMinutes = startHour * 60 + startMin;
    if (currentMinutes < startMinutes) {
      return i;
    }
  }
  return -1;
}

// 날짜 범위 생성 (중앙 기준 ±days)
function getDateRange(centerDate: string, days: number = 14): {
  date: string;
  day: number;
  weekday: string;
  month: number;
  isToday: boolean;
  isSunday: boolean;
  isSaturday: boolean;
}[] {
  const center = new Date(centerDate);
  const today = new Date().toISOString().split('T')[0];
  const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
  const dates = [];

  for (let i = -days; i <= days; i++) {
    const d = new Date(center);
    d.setDate(center.getDate() + i);
    const dateStr = d.toISOString().split('T')[0];
    const dayOfWeek = d.getDay();

    dates.push({
      date: dateStr,
      day: d.getDate(),
      month: d.getMonth() + 1,
      weekday: weekdays[dayOfWeek],
      isToday: dateStr === today,
      isSunday: dayOfWeek === 0,
      isSaturday: dayOfWeek === 6,
    });
  }
  return dates;
}

// ===== 컴포넌트: Horizontal Scrolling Date Picker =====
function HorizontalDatePicker({
  selectedDate,
  onDateSelect,
  onTodayClick,
}: {
  selectedDate: string;
  onDateSelect: (date: string) => void;
  onTodayClick: () => void;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const dateRefs = useRef<Map<string, HTMLButtonElement>>(new Map());
  const dates = useMemo(() => getDateRange(selectedDate, 14), [selectedDate]);

  // 선택된 날짜로 스크롤
  useEffect(() => {
    const selectedEl = dateRefs.current.get(selectedDate);
    if (selectedEl && scrollRef.current) {
      const container = scrollRef.current;
      const scrollLeft = selectedEl.offsetLeft - container.clientWidth / 2 + selectedEl.clientWidth / 2;
      container.scrollTo({ left: scrollLeft, behavior: 'smooth' });
    }
  }, [selectedDate]);

  const formatTitle = (dateStr: string) => {
    const date = new Date(dateStr);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    return `${month}월 ${day}일 (${weekdays[date.getDay()]})`;
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      {/* 타이틀 바 */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
        <h2 className="text-lg font-bold text-slate-800">
          {formatTitle(selectedDate)}
        </h2>
        <button
          onClick={onTodayClick}
          className="text-xs font-semibold text-ocean-600 hover:text-ocean-700 px-3 py-1.5 rounded-lg hover:bg-ocean-50 transition-colors"
        >
          오늘
        </button>
      </div>

      {/* 가로 스크롤 날짜 피커 */}
      <div
        ref={scrollRef}
        className="flex overflow-x-auto scrollbar-hide px-2 py-3 gap-1 snap-x snap-mandatory"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {dates.map((d) => {
          const isSelected = d.date === selectedDate;

          return (
            <button
              key={d.date}
              ref={(el) => {
                if (el) dateRefs.current.set(d.date, el);
              }}
              onClick={() => onDateSelect(d.date)}
              className={`
                flex-shrink-0 flex flex-col items-center justify-center
                w-12 h-14 rounded-xl transition-all snap-center
                ${isSelected
                  ? 'bg-ocean-500 text-white shadow-lg scale-105'
                  : d.isToday
                    ? 'bg-ocean-50 text-ocean-700 ring-2 ring-ocean-300'
                    : 'hover:bg-slate-100 active:scale-95'
                }
              `}
            >
              {/* 요일 */}
              <span className={`
                text-[10px] font-medium leading-none mb-1
                ${isSelected
                  ? 'text-white/80'
                  : d.isSunday
                    ? 'text-red-500'
                    : d.isSaturday
                      ? 'text-blue-500'
                      : 'text-slate-400'
                }
              `}>
                {d.weekday}
              </span>

              {/* 날짜 */}
              <span className={`
                text-base font-bold leading-none
                ${isSelected ? 'text-white' : 'text-slate-700'}
              `}>
                {d.day}
              </span>

              {/* 오늘 표시 */}
              {d.isToday && !isSelected && (
                <span className="w-1 h-1 bg-ocean-500 rounded-full mt-1" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ===== 컴포넌트: 슬림 세션 아이템 =====
function SlimSessionItem({
  session,
  isPast,
  isNext,
}: {
  session: Session;
  isPast: boolean;
  isNext: boolean;
}) {
  return (
    <div className={`
      flex items-center gap-2 px-3 py-2 rounded-lg transition-all
      ${isPast
        ? 'bg-slate-50 opacity-50'
        : isNext
          ? 'bg-ocean-50 border-l-4 border-ocean-500'
          : 'bg-slate-50/50 hover:bg-slate-50'
      }
    `}>
      {/* 세션명 */}
      <span className={`
        w-10 text-sm font-semibold
        ${isPast ? 'text-slate-400' : isNext ? 'text-ocean-700' : 'text-slate-700'}
      `}>
        {session.session_name}
      </span>

      {/* 시간 */}
      <span className={`
        flex-1 text-sm font-mono
        ${isPast ? 'text-slate-400 line-through' : isNext ? 'text-ocean-600 font-semibold' : 'text-slate-600'}
      `}>
        {session.start_time.substring(0, 5)} - {session.end_time.substring(0, 5)}
      </span>

      {/* 정원 */}
      {session.capacity && (
        <span className={`
          text-xs px-2 py-0.5 rounded-full
          ${isPast
            ? 'bg-slate-100 text-slate-400'
            : isNext
              ? 'bg-ocean-100 text-ocean-700'
              : 'bg-slate-100 text-slate-500'
          }
        `}>
          {session.capacity}명
        </span>
      )}

      {/* NEXT 뱃지 */}
      {isNext && (
        <span className="text-[10px] font-bold text-white bg-ocean-500 px-1.5 py-0.5 rounded">
          NEXT
        </span>
      )}
    </div>
  );
}

// ===== 컴포넌트: 컴팩트 시설 카드 (Sticky Header) =====
function CompactFacilityCard({
  schedule,
  selectedDate,
  colorIndex,
  defaultExpanded = true,
}: {
  schedule: DailySchedule;
  selectedDate: string;
  colorIndex: number;
  defaultExpanded?: boolean;
}) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const nextSessionIdx = useMemo(
    () => (schedule.is_closed ? -1 : findNextSessionIndex(schedule.sessions, selectedDate)),
    [schedule.sessions, selectedDate, schedule.is_closed]
  );

  const pastCount = useMemo(() => {
    if (schedule.is_closed) return 0;
    return schedule.sessions.filter((s) => getSessionStatus(s, selectedDate) === 'past').length;
  }, [schedule.sessions, selectedDate, schedule.is_closed]);

  const colorMap = ['ocean', 'wave', 'emerald'] as const;
  const color = colorMap[colorIndex % 3];

  const bgColors = {
    ocean: 'bg-ocean-500',
    wave: 'bg-wave-500',
    emerald: 'bg-emerald-500',
  };

  const parseNotes = (notesStr?: string): string[] => {
    if (!notesStr) return [];
    try {
      return JSON.parse(notesStr);
    } catch {
      return [];
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      {/* 시설 헤더 */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-2 p-3 hover:bg-slate-50 transition-colors"
      >
        {/* 컬러바 */}
        <div className={`w-1 h-8 rounded-full ${schedule.is_closed ? 'bg-slate-300' : bgColors[color]}`} />

        {/* 시설명 */}
        <div className="flex-1 text-left">
          <h3 className={`font-bold text-sm ${schedule.is_closed ? 'text-slate-400' : 'text-slate-800'}`}>
            {schedule.facility_name}
          </h3>
          <p className="text-xs mt-0.5 text-slate-400">
            {schedule.is_closed
              ? '휴관'
              : `${schedule.sessions.length}개 세션${pastCount > 0 ? ` · ${pastCount}개 종료` : ''}`}
          </p>
        </div>

        {/* 뱃지 */}
        {!schedule.is_closed && (
          <Badge variant={color} size="sm">
            {schedule.day_type}
          </Badge>
        )}

        {/* 화살표 */}
        <svg
          className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''} text-slate-400`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* 세션 리스트 */}
      {isExpanded && (
        <div className="border-t border-slate-100">
          {schedule.is_closed ? (
            <div className="flex items-center justify-center py-4 text-slate-400 text-sm">
              <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
              {schedule.closure_reason || '휴관일입니다'}
            </div>
          ) : (
            <div className="p-2 space-y-1">
              {schedule.sessions.map((session, idx) => (
                <SlimSessionItem
                  key={idx}
                  session={session}
                  isPast={getSessionStatus(session, selectedDate) === 'past'}
                  isNext={idx === nextSessionIdx}
                />
              ))}
            </div>
          )}

          {/* 유의사항 & 원본 링크 */}
          {!schedule.is_closed && (parseNotes(schedule.notes).length > 0 || schedule.source_url) && (
            <div className="px-3 pb-2 space-y-1.5">
              {parseNotes(schedule.notes).length > 0 && (
                <p className="text-xs text-amber-600 bg-amber-50 rounded px-2 py-1.5">
                  {parseNotes(schedule.notes)[0]}
                </p>
              )}
              {schedule.source_url && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    openSourceUrl(schedule.source_url!);
                  }}
                  className="w-full text-xs text-slate-400 hover:text-ocean-500 py-1 flex items-center justify-center gap-1"
                >
                  원본 공지
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ===== 메인 컴포넌트: CalendarView =====
function CalendarView() {
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    return new Date().toISOString().split('T')[0];
  });
  const [dailySchedules, setDailySchedules] = useState<DailySchedule[]>([]);
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [selectedFacility, setSelectedFacility] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  // 시설 목록 로드
  useEffect(() => {
    const loadFacilities = async () => {
      try {
        const data = await scheduleApi.getFacilities();
        setFacilities(data);
      } catch (err) {
        console.error('시설 목록 로드 실패:', err);
      }
    };
    loadFacilities();
  }, []);

  // 날짜 변경 시 데이터 로드
  useEffect(() => {
    loadDailySchedules(selectedDate);
  }, [selectedDate]);

  const loadDailySchedules = async (dateStr: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await scheduleApi.getDailySchedules(dateStr);
      setDailySchedules(data);
    } catch (err) {
      console.error('스케줄 로드 실패:', err);
      setError('데이터를 불러올 수 없습니다.');
      setDailySchedules([]);
    } finally {
      setLoading(false);
    }
  };

  const goToToday = () => {
    setSelectedDate(new Date().toISOString().split('T')[0]);
  };

  const formatDateShort = (dateStr: string) => {
    const date = new Date(dateStr);
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    return `${date.getMonth() + 1}월 ${date.getDate()}일 (${weekdays[date.getDay()]})`;
  };

  // 필터 적용
  const filteredSchedules = useMemo(() => {
    if (!selectedFacility) return dailySchedules;
    return dailySchedules.filter((s) => s.facility_name === selectedFacility);
  }, [dailySchedules, selectedFacility]);

  const hasFilter = selectedFacility !== '';
  const operatingCount = filteredSchedules.filter((s) => !s.is_closed).length;
  const closedCount = filteredSchedules.filter((s) => s.is_closed).length;

  return (
    <div className="space-y-4 pb-20">
      {/* Horizontal Date Picker */}
      <HorizontalDatePicker
        selectedDate={selectedDate}
        onDateSelect={(date) => {
          trackFilterUse('date', date);
          setSelectedDate(date);
        }}
        onTodayClick={goToToday}
      />

      {/* 요약 정보 */}
      {!loading && !error && filteredSchedules.length > 0 && (
        <div className="flex items-center gap-3 px-1">
          {operatingCount > 0 && (
            <span className="inline-flex items-center gap-1 text-sm font-medium text-ocean-600">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              운영 {operatingCount}개
            </span>
          )}
          {closedCount > 0 && (
            <span className="text-sm text-slate-400">
              · 휴관 {closedCount}개
            </span>
          )}
          {hasFilter && (
            <span className="inline-flex items-center gap-1 text-xs text-ocean-600 font-medium bg-ocean-50 px-2 py-0.5 rounded-full">
              {selectedFacility}
              <button
                onClick={() => setSelectedFacility('')}
                className="hover:text-ocean-800"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
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
            onClick={() => loadDailySchedules(selectedDate)}
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
              <div className="flex items-center gap-2">
                <div className="w-1 h-8 bg-slate-200 rounded-full" />
                <div className="flex-1">
                  <div className="h-4 bg-slate-200 rounded w-1/3 mb-1.5" />
                  <div className="h-3 bg-slate-100 rounded w-1/4" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredSchedules.length === 0 ? (
            <EmptyState
              message={hasFilter
                ? `${formatDateShort(selectedDate)}에 ${selectedFacility}의 일정이 없습니다.`
                : `${formatDateShort(selectedDate)}에 운영하는 수영장이 없습니다.`
              }
              icon="minus"
              action={hasFilter ? {
                label: '필터 해제',
                onClick: () => setSelectedFacility(''),
              } : {
                label: '다음 날 보기',
                onClick: () => {
                  const date = new Date(selectedDate);
                  date.setDate(date.getDate() + 1);
                  setSelectedDate(date.toISOString().split('T')[0]);
                },
              }}
            />
          ) : (
            [...filteredSchedules]
              .sort((a, b) => Number(a.is_closed) - Number(b.is_closed))
              .map((schedule, index) => (
                <CompactFacilityCard
                  key={schedule.facility_id}
                  schedule={schedule}
                  selectedDate={selectedDate}
                  colorIndex={index}
                  defaultExpanded={index < 2}
                />
              ))
          )}
        </div>
      )}

      {/* FAB 필터 버튼 */}
      <FilterFAB onClick={() => setIsFilterOpen(true)} hasFilter={hasFilter} />

      {/* Filter Drawer */}
      <FilterDrawer
        isOpen={isFilterOpen}
        onClose={() => setIsFilterOpen(false)}
        facilities={facilities}
        selectedFacility={selectedFacility}
        onFacilityChange={(value) => {
          trackFilterUse('facility', value || '전체');
          setSelectedFacility(value);
        }}
      />
    </div>
  );
}

export default CalendarView;
