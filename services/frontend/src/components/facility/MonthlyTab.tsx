import { useState, useEffect, useMemo } from 'react';
import { scheduleApi } from '../../services/api';
import type { Schedule, Session, ScheduleDetail } from '../../types/schedule';
import { openSourceUrl } from '../../utils/urlUtils';
import { trackFilterUse } from '../../utils/analytics';
import { EmptyState, Badge } from '../common';

// ===== 슬림 세션 아이템 =====
function SlimSessionItem({
  session,
  colorScheme,
}: {
  session: Session;
  colorScheme: 'ocean' | 'wave' | 'emerald';
}) {
  const borderColors = {
    ocean: 'border-l-ocean-400',
    wave: 'border-l-wave-400',
    emerald: 'border-l-emerald-400',
  };

  const badgeColors = {
    ocean: 'bg-ocean-100 text-ocean-700',
    wave: 'bg-wave-100 text-wave-700',
    emerald: 'bg-emerald-100 text-emerald-700',
  };

  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50/50 hover:bg-slate-50 border-l-4 ${borderColors[colorScheme]} transition-colors`}>
      {/* 세션명 */}
      <span className="w-10 text-sm font-semibold text-slate-700">
        {session.session_name}
      </span>

      {/* 시간 */}
      <span className="flex-1 text-sm font-mono text-slate-600">
        {session.start_time.substring(0, 5)} - {session.end_time.substring(0, 5)}
      </span>

      {/* 정원/레인 */}
      <div className="flex items-center gap-1.5">
        {session.capacity && (
          <span className={`text-xs px-2 py-0.5 rounded-full ${badgeColors[colorScheme]}`}>
            {session.capacity}명
          </span>
        )}
        {session.lanes && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
            {session.lanes}레인
          </span>
        )}
      </div>
    </div>
  );
}

// ===== 요일 타입 섹션 =====
function DayTypeSection({
  detail,
  colorScheme,
  defaultExpanded = true,
}: {
  detail: ScheduleDetail;
  colorScheme: 'ocean' | 'wave' | 'emerald';
  defaultExpanded?: boolean;
}) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className="border border-slate-100 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-2 px-3 py-2 bg-slate-50 hover:bg-slate-100 transition-colors"
      >
        <span className="font-semibold text-sm text-slate-800">
          {detail.day_type}
        </span>
        {detail.season && (
          <Badge variant={colorScheme} size="sm">
            {detail.season}
          </Badge>
        )}
        {detail.season_months && (
          <span className="text-xs text-slate-400">{detail.season_months}</span>
        )}
        <span className="flex-1" />
        <span className="text-xs text-slate-400">{detail.sessions.length}개 세션</span>
        <svg
          className={`w-4 h-4 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="p-2 space-y-1">
          {detail.sessions.map((session, idx) => (
            <SlimSessionItem
              key={idx}
              session={session}
              colorScheme={colorScheme}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ===== Props =====
interface MonthlyTabProps {
  facilityName: string;
}

// ===== 메인 컴포넌트: MonthlyTab =====
export function MonthlyTab({ facilityName }: MonthlyTabProps) {
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [selectedMonth, setSelectedMonth] = useState<string>(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showFees, setShowFees] = useState(false);
  const [showNotes, setShowNotes] = useState(false);

  useEffect(() => {
    loadSchedule();
  }, [facilityName, selectedMonth]);

  const loadSchedule = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await scheduleApi.getSchedules(facilityName, selectedMonth);
      setSchedule(data.length > 0 ? data[0] : null);
    } catch (err) {
      setError('스케줄을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 선택된 월 포맷
  const formatMonth = () => {
    if (!selectedMonth) return '';
    const [year, month] = selectedMonth.split('-');
    return `${year}년 ${parseInt(month)}월`;
  };

  // 월 전체 휴장 여부
  const isMonthClosed = schedule?.closure_info?.is_closed === true;

  const totalSessions = useMemo(() => {
    if (!schedule) return 0;
    return schedule.schedules.reduce((acc, d) => acc + d.sessions.length, 0);
  }, [schedule]);

  return (
    <div className="space-y-4">
      {/* 월 선택 헤더 */}
      <div className="bg-white rounded-xl border border-slate-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">월별 스케줄</p>
            <h2 className="text-lg font-bold text-slate-800">{formatMonth()}</h2>
          </div>
          <input
            type="month"
            value={selectedMonth}
            onChange={(e) => {
              trackFilterUse('month', e.target.value);
              setSelectedMonth(e.target.value);
            }}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-ocean-500"
          />
        </div>
      </div>

      {/* 에러 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
          <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span className="flex-1 text-sm text-red-700">{error}</span>
          <button
            onClick={loadSchedule}
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
              <div key={i} className="h-12 bg-slate-100 rounded" />
            ))}
          </div>
        </div>
      ) : !schedule ? (
        <EmptyState
          message={`${formatMonth()} ${facilityName}의 스케줄 정보가 없습니다.`}
          icon="clipboard"
        />
      ) : isMonthClosed ? (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center">
          <svg className="w-12 h-12 mx-auto mb-3 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
          <p className="text-slate-600 font-medium">{schedule.closure_info?.reason || '휴장'}</p>
          <p className="text-sm text-slate-400 mt-1">이번 달은 운영하지 않습니다</p>
        </div>
      ) : (
        <>
          {/* 요약 */}
          <div className="flex items-center gap-2 px-1">
            <span className="text-sm font-medium text-slate-600">
              {schedule.schedules.length}개 요일 · {totalSessions}개 세션
            </span>
          </div>

          {/* 요일별 세션 */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="p-3 space-y-2">
              {schedule.schedules.map((detail, idx) => (
                <DayTypeSection
                  key={idx}
                  detail={detail}
                  colorScheme="ocean"
                  defaultExpanded={idx === 0}
                />
              ))}
            </div>

            {/* 이용료 & 유의사항 토글 */}
            <div className="px-3 pb-3 space-y-2">
              {/* 이용료 */}
              {schedule.fees && schedule.fees.length > 0 && (
                <div className="border border-green-100 rounded-lg overflow-hidden">
                  <button
                    onClick={() => setShowFees(!showFees)}
                    className="w-full flex items-center gap-2 px-3 py-2 bg-green-50 hover:bg-green-100 transition-colors"
                  >
                    <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm font-medium text-green-700">이용료</span>
                    <span className="flex-1" />
                    <svg
                      className={`w-4 h-4 text-green-400 transition-transform ${showFees ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {showFees && (
                    <div className="px-3 py-2 space-y-1.5 bg-green-50/50">
                      {schedule.fees.map((fee, idx) => (
                        <div key={idx} className="flex items-center justify-between text-sm">
                          <span className="text-green-700">{fee.category}</span>
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-green-800">
                              {fee.price.toLocaleString()}원
                            </span>
                            {fee.note && (
                              <span className="text-green-600 text-xs">({fee.note})</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* 유의사항 */}
              {schedule.notes && schedule.notes.length > 0 && (
                <div className="border border-amber-100 rounded-lg overflow-hidden">
                  <button
                    onClick={() => setShowNotes(!showNotes)}
                    className="w-full flex items-center gap-2 px-3 py-2 bg-amber-50 hover:bg-amber-100 transition-colors"
                  >
                    <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm font-medium text-amber-700">유의사항</span>
                    <span className="text-xs text-amber-500 ml-1">({schedule.notes.length})</span>
                    <span className="flex-1" />
                    <svg
                      className={`w-4 h-4 text-amber-400 transition-transform ${showNotes ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {showNotes && (
                    <div className="px-3 py-2 space-y-1 bg-amber-50/50">
                      {schedule.notes.map((note, idx) => (
                        <p key={idx} className="text-sm text-amber-700 flex items-start gap-2">
                          <span className="text-amber-400 mt-0.5">•</span>
                          {note}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* 원본 링크 */}
              {schedule.source_url && (
                <button
                  onClick={() => openSourceUrl(schedule.source_url!)}
                  className="w-full text-xs text-slate-400 hover:text-ocean-500 py-2 flex items-center justify-center gap-1 hover:bg-slate-50 rounded-lg transition-colors"
                >
                  원본 공지
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
