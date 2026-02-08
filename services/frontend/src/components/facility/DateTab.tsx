import { useState, useEffect, useMemo, useRef } from 'react';
import { scheduleApi } from '../../services/api';
import type { DailySchedule, Session } from '../../types/schedule';
import { openSourceUrl } from '../../utils/urlUtils';
import { trackFilterUse } from '../../utils/analytics';
import { EmptyState, Badge } from '../common';
import { SlimSessionItem } from '../daily';

// ===== 유틸리티 함수 =====

// 현재 시간 기준 세션 상태 판단
function getSessionStatus(session: Session, selectedDate: string): 'past' | 'current' | 'upcoming' {
  const now = new Date();
  const today = now.toISOString().split('T')[0];

  if (selectedDate !== today) return 'upcoming';

  const currentMinutes = now.getHours() * 60 + now.getMinutes();
  const [startHour, startMin] = session.start_time.split(':').map(Number);
  const [endHour, endMin] = session.end_time.split(':').map(Number);
  const startMinutes = startHour * 60 + startMin;
  const endMinutes = endHour * 60 + endMin;

  if (currentMinutes >= endMinutes) return 'past';
  if (currentMinutes >= startMinutes && currentMinutes < endMinutes) return 'current';
  return 'upcoming';
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

// 노트 파싱
function parseNotes(notesStr?: string): string[] {
  if (!notesStr) return [];
  try {
    return JSON.parse(notesStr);
  } catch {
    return [];
  }
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

// ===== Props =====
interface DateTabProps {
  facilityId: number;
  facilityName: string;
}

// ===== 메인 컴포넌트: DateTab =====
export function DateTab({ facilityId, facilityName }: DateTabProps) {
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    return new Date().toISOString().split('T')[0];
  });
  const [dailySchedules, setDailySchedules] = useState<DailySchedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 날짜 변경 시 데이터 로드
  useEffect(() => {
    loadDailySchedules(selectedDate);
  }, [selectedDate, facilityId]);

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

  // 선택된 시설의 스케줄만 필터링
  const schedule = useMemo(() => {
    return dailySchedules.find((s) => s.facility_id === facilityId);
  }, [dailySchedules, facilityId]);

  const nextSessionIdx = useMemo(() => {
    if (!schedule || schedule.is_closed) return -1;
    return findNextSessionIndex(schedule.sessions, selectedDate);
  }, [schedule, selectedDate]);

  const notes = useMemo(() => {
    if (!schedule) return [];
    return parseNotes(schedule.notes);
  }, [schedule]);

  return (
    <div className="space-y-4">
      {/* Horizontal Date Picker */}
      <HorizontalDatePicker
        selectedDate={selectedDate}
        onDateSelect={(date) => {
          trackFilterUse('date', date);
          setSelectedDate(date);
        }}
        onTodayClick={goToToday}
      />

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
        <div className="bg-white rounded-xl border border-slate-200 p-4 animate-pulse">
          <div className="h-4 bg-slate-200 rounded w-1/3 mb-3" />
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-10 bg-slate-100 rounded" />
            ))}
          </div>
        </div>
      ) : !schedule ? (
        <EmptyState
          message={`이 날짜에 ${facilityName}의 일정이 없습니다.`}
          icon="minus"
          action={{
            label: '다음 날 보기',
            onClick: () => {
              const date = new Date(selectedDate);
              date.setDate(date.getDate() + 1);
              setSelectedDate(date.toISOString().split('T')[0]);
            },
          }}
        />
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          {schedule.is_closed ? (
            <div className="flex flex-col items-center justify-center py-8 text-slate-400">
              <svg className="w-10 h-10 mb-2 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
              <p className="text-sm font-medium">{schedule.closure_reason || '휴관일입니다'}</p>
            </div>
          ) : (
            <>
              {/* 세션 카운트 */}
              <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
                <span className="text-sm text-slate-600">
                  <strong className="text-slate-800">{schedule.sessions.length}개</strong> 세션
                </span>
                <Badge variant="ocean" size="sm">{schedule.day_type}</Badge>
              </div>

              {/* 세션 리스트 */}
              <div className="p-2 space-y-1">
                {schedule.sessions.map((session, idx) => (
                  <SlimSessionItem
                    key={idx}
                    session={session}
                    status={getSessionStatus(session, selectedDate)}
                    isNext={idx === nextSessionIdx}
                  />
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* 유의사항 */}
      {notes.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-start gap-2">
            <svg className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div className="space-y-1">
              <p className="text-sm font-medium text-amber-800">유의사항</p>
              {notes.map((note, idx) => (
                <p key={idx} className="text-sm text-amber-700">{note}</p>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 원본 공지 링크 */}
      {schedule?.source_url && (
        <button
          onClick={() => openSourceUrl(schedule.source_url!)}
          className="w-full flex items-center justify-center gap-2 py-3 text-sm text-slate-500 hover:text-ocean-600 hover:bg-slate-50 rounded-xl border border-slate-200 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          원본 공지 보기
        </button>
      )}
    </div>
  );
}
