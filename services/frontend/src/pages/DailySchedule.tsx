import { useState, useEffect, useMemo } from 'react';
import { scheduleApi } from '../services/api';
import type { DailySchedule, Session } from '../types/schedule';
import { openSourceUrl } from '../utils/urlUtils';
import { EmptyState, Badge } from '../components/common';
import { Link } from 'react-router-dom';
import { useFavorites } from '../hooks';

// ===== 유틸리티 함수 =====

// 현재 시간 기준 세션 상태 판단
function getSessionStatus(session: Session): 'past' | 'current' | 'upcoming' {
  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  const [startHour, startMin] = session.start_time.split(':').map(Number);
  const [endHour, endMin] = session.end_time.split(':').map(Number);
  const startMinutes = startHour * 60 + startMin;
  const endMinutes = endHour * 60 + endMin;

  if (currentMinutes >= endMinutes) {
    return 'past';
  } else if (currentMinutes >= startMinutes && currentMinutes < endMinutes) {
    return 'current';
  }
  return 'upcoming';
}

// 다음 이용 가능한 세션 인덱스 찾기
function findNextSessionIndex(sessions: Session[]): number {
  const now = new Date();
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

// ===== 컴포넌트: 슬림 세션 아이템 =====
function SlimSessionItem({
  session,
  status,
  isNext,
}: {
  session: Session;
  status: 'past' | 'current' | 'upcoming';
  isNext: boolean;
}) {
  const isPast = status === 'past';
  const isCurrent = status === 'current';

  return (
    <div className={`
      flex items-center gap-2 px-3 py-2.5 rounded-lg transition-all
      ${isPast
        ? 'bg-slate-50 opacity-50'
        : isCurrent
          ? 'bg-green-50 border-l-4 border-green-500'
          : isNext
            ? 'bg-ocean-50 border-l-4 border-ocean-500'
            : 'bg-slate-50/50 hover:bg-slate-50'
      }
    `}>
      {/* 세션명 */}
      <span className={`
        w-10 text-sm font-semibold
        ${isPast ? 'text-slate-400' : isCurrent ? 'text-green-700' : isNext ? 'text-ocean-700' : 'text-slate-700'}
      `}>
        {session.session_name}
      </span>

      {/* 시간 */}
      <span className={`
        flex-1 text-sm font-mono
        ${isPast ? 'text-slate-400 line-through' : isCurrent ? 'text-green-600 font-semibold' : isNext ? 'text-ocean-600 font-semibold' : 'text-slate-600'}
      `}>
        {session.start_time.substring(0, 5)} - {session.end_time.substring(0, 5)}
      </span>

      {/* 정원 */}
      {session.capacity && (
        <span className={`
          text-xs px-2 py-0.5 rounded-full
          ${isPast
            ? 'bg-slate-100 text-slate-400'
            : isCurrent
              ? 'bg-green-100 text-green-700'
              : isNext
                ? 'bg-ocean-100 text-ocean-700'
                : 'bg-slate-100 text-slate-500'
          }
        `}>
          {session.capacity}명
        </span>
      )}

      {/* 상태 뱃지 */}
      {isCurrent && (
        <span className="text-[10px] font-bold text-white bg-green-500 px-1.5 py-0.5 rounded animate-pulse">
          NOW
        </span>
      )}
      {isNext && !isCurrent && (
        <span className="text-[10px] font-bold text-white bg-ocean-500 px-1.5 py-0.5 rounded">
          NEXT
        </span>
      )}
    </div>
  );
}

// ===== 컴포넌트: 컴팩트 시설 카드 =====
function CompactFacilityCard({
  schedule,
  colorIndex,
  defaultExpanded = true,
  isFavorite,
  onToggleFavorite,
}: {
  schedule: DailySchedule;
  colorIndex: number;
  defaultExpanded?: boolean;
  isFavorite: boolean;
  onToggleFavorite: () => void;
}) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const nextSessionIdx = useMemo(
    () => (schedule.is_closed ? -1 : findNextSessionIndex(schedule.sessions)),
    [schedule.sessions, schedule.is_closed]
  );

  const pastCount = useMemo(() => {
    if (schedule.is_closed) return 0;
    return schedule.sessions.filter((s) => getSessionStatus(s) === 'past').length;
  }, [schedule.sessions, schedule.is_closed]);

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
    <div className={`bg-white rounded-xl border overflow-hidden ${isFavorite ? 'border-amber-300 ring-1 ring-amber-200' : 'border-slate-200'}`}>
      {/* 시설 헤더 */}
      <div className="flex items-center">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex-1 flex items-center gap-2 p-3 hover:bg-slate-50 transition-colors"
        >
          {/* 컬러바 */}
          <div className={`w-1 h-8 rounded-full ${schedule.is_closed ? 'bg-slate-300' : bgColors[color]}`} />

          {/* 시설명 */}
          <div className="flex-1 text-left">
            <h3 className={`font-bold text-sm ${schedule.is_closed ? 'text-slate-400' : 'text-slate-800'}`}>
              {schedule.facility_name}
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
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
            className={`w-4 h-4 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* 즐겨찾기 버튼 */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleFavorite();
          }}
          className={`p-3 transition-colors ${isFavorite ? 'text-amber-500 hover:text-amber-600' : 'text-slate-300 hover:text-amber-400'}`}
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
                  status={getSessionStatus(session)}
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

// ===== 메인 컴포넌트 =====
function DailySchedulePage() {
  const [schedules, setSchedules] = useState<DailySchedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const { toggleFavorite, isFavorite } = useFavorites();

  // 오늘 날짜 (자정에 자동 갱신)
  const [today, setToday] = useState(() => new Date().toISOString().split('T')[0]);

  // 1분마다 현재 시간 업데이트 (세션 상태 갱신용)
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
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

  const formatTime = () => {
    return currentTime.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  const operatingCount = schedules.filter((s) => !s.is_closed).length;
  const closedCount = schedules.filter((s) => s.is_closed).length;

  return (
    <div className="space-y-4">
      {/* 오늘 날짜 헤더 (고정) */}
      <div className="bg-gradient-to-r from-ocean-500 to-wave-500 rounded-xl p-4 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/80 text-sm font-medium">오늘</p>
            <h1 className="text-2xl font-bold">{formatDate()}</h1>
          </div>
          <div className="text-right">
            <p className="text-white/80 text-sm font-medium">현재 시간</p>
            <p className="text-xl font-bold font-mono">{formatTime()}</p>
          </div>
        </div>

        {/* 다른 날짜 보기 링크 */}
        <Link
          to="/calendar"
          className="mt-3 flex items-center justify-center gap-1.5 text-sm text-ocean-700 hover:text-ocean-800 bg-white/90 hover:bg-white rounded-lg py-2 font-medium transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          다른 날짜 보기
        </Link>
      </div>

      {/* 요약 정보 */}
      {!loading && !error && schedules.length > 0 && (
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
          {schedules.length === 0 ? (
            <EmptyState
              message="오늘 운영하는 수영장이 없습니다."
              icon="minus"
              action={{
                label: '다른 날짜 보기',
                onClick: () => {
                  window.location.href = '/calendar';
                },
              }}
            />
          ) : (
            [...schedules]
              .sort((a, b) => {
                // 1. 즐겨찾기 우선
                const aFav = isFavorite(a.facility_id) ? 0 : 1;
                const bFav = isFavorite(b.facility_id) ? 0 : 1;
                if (aFav !== bFav) return aFav - bFav;
                // 2. 휴관 시설은 뒤로
                return Number(a.is_closed) - Number(b.is_closed);
              })
              .map((schedule, index) => (
                <CompactFacilityCard
                  key={schedule.facility_id}
                  schedule={schedule}
                  colorIndex={index}
                  defaultExpanded={isFavorite(schedule.facility_id) || index < 3}
                  isFavorite={isFavorite(schedule.facility_id)}
                  onToggleFavorite={() => toggleFavorite(schedule.facility_id)}
                />
              ))
          )}
        </div>
      )}
    </div>
  );
}

export default DailySchedulePage;
