import { useState, useEffect, useMemo, useRef } from 'react';
import { scheduleApi } from '../services/api';
import type { Facility, Schedule, Session, ScheduleDetail } from '../types/schedule';
import { openSourceUrl } from '../utils/urlUtils';
import { trackFilterUse, trackFacilityView } from '../utils/analytics';
import { EmptyState, Badge } from '../components/common';

// ===== Filter Drawer 컴포넌트 =====
function FilterDrawer({
  isOpen,
  onClose,
  facilities,
  selectedFacility,
  onFacilityChange,
  selectedMonth,
  onMonthChange,
}: {
  isOpen: boolean;
  onClose: () => void;
  facilities: Facility[];
  selectedFacility: string;
  onFacilityChange: (value: string) => void;
  selectedMonth: string;
  onMonthChange: (value: string) => void;
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
          <h3 className="text-lg font-bold text-slate-800">필터</h3>
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
        <div className="p-4 space-y-4 max-h-[60vh] overflow-y-auto">
          {/* 시설 선택 */}
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-2">수영장</label>
            <select
              value={selectedFacility}
              onChange={(e) => onFacilityChange(e.target.value)}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-ocean-500"
            >
              <option value="">전체 수영장</option>
              {facilities.map((facility) => (
                <option key={facility.facility_name} value={facility.facility_name}>
                  {facility.facility_name}
                </option>
              ))}
            </select>
          </div>

          {/* 월 선택 */}
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-2">월 선택</label>
            <input
              type="month"
              value={selectedMonth}
              onChange={(e) => onMonthChange(e.target.value)}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-ocean-500"
            />
          </div>
        </div>

        {/* 적용 버튼 */}
        <div className="p-4 border-t border-slate-100">
          <button
            onClick={onClose}
            className="w-full py-3 bg-ocean-500 hover:bg-ocean-600 text-white font-semibold rounded-xl transition-colors"
          >
            적용하기
          </button>
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

// ===== 컴팩트 시설 카드 (Sticky Header 적용) =====
function CompactScheduleCard({
  schedule,
  colorIndex,
  defaultExpanded = true,
}: {
  schedule: Schedule;
  colorIndex: number;
  defaultExpanded?: boolean;
}) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [showFees, setShowFees] = useState(false);
  const [showNotes, setShowNotes] = useState(false);
  const [isSticky, setIsSticky] = useState(false);
  const headerRef = useRef<HTMLDivElement>(null);

  const colorSchemes = ['ocean', 'wave', 'emerald'] as const;
  const colorScheme = colorSchemes[colorIndex % 3];

  const bgColors = {
    ocean: 'bg-ocean-500',
    wave: 'bg-wave-500',
    emerald: 'bg-emerald-500',
  };

  const stickyBgColors = {
    ocean: 'bg-gradient-to-r from-ocean-500 to-ocean-400',
    wave: 'bg-gradient-to-r from-wave-500 to-wave-400',
    emerald: 'bg-gradient-to-r from-emerald-500 to-emerald-400',
  };

  const totalSessions = useMemo(() => {
    return schedule.schedules.reduce((acc, d) => acc + d.sessions.length, 0);
  }, [schedule.schedules]);

  // Sticky 상태 감지
  useEffect(() => {
    const header = headerRef.current;
    if (!header) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsSticky(entry.intersectionRatio < 1);
      },
      { threshold: [1], rootMargin: '-1px 0px 0px 0px' }
    );

    observer.observe(header);
    return () => observer.disconnect();
  }, []);

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-visible">
      {/* Sticky 헤더 */}
      <div
        ref={headerRef}
        className={`sticky top-0 z-10 rounded-t-xl transition-all ${
          isSticky ? `${stickyBgColors[colorScheme]} shadow-md` : ''
        }`}
      >
        <button
          onClick={() => {
            if (!isExpanded) {
              trackFacilityView(schedule.facility_id, schedule.facility_name);
            }
            setIsExpanded(!isExpanded);
          }}
          className={`w-full flex items-center gap-3 p-3 rounded-t-xl transition-colors ${
            isSticky ? '' : 'hover:bg-slate-50'
          }`}
        >
          {/* 컬러바 */}
          <div className={`w-1 h-10 rounded-full ${isSticky ? 'bg-white/30' : bgColors[colorScheme]}`} />

          {/* 시설명 */}
          <div className="flex-1 text-left">
            <h3 className={`font-bold text-sm ${isSticky ? 'text-white' : 'text-slate-800'}`}>
              {schedule.facility_name}
            </h3>
            <p className={`text-xs mt-0.5 ${isSticky ? 'text-white/70' : 'text-slate-400'}`}>
              {schedule.valid_month} · {schedule.schedules.length}개 요일 · {totalSessions}개 세션
            </p>
          </div>

          {/* 화살표 */}
          <svg
            className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''} ${
              isSticky ? 'text-white/70' : 'text-slate-400'
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {/* 컨텐츠 */}
      {isExpanded && (
        <div className="border-t border-slate-100">
          {/* 요일별 세션 */}
          <div className="p-3 space-y-2">
            {schedule.schedules.map((detail, idx) => (
              <DayTypeSection
                key={idx}
                detail={detail}
                colorScheme={colorScheme}
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
      )}
    </div>
  );
}

// ===== 메인 컴포넌트 =====
function MonthlySchedule() {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [selectedFacility, setSelectedFacility] = useState<string>('');
  const [selectedMonth, setSelectedMonth] = useState<string>(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  useEffect(() => {
    loadFacilities();
  }, []);

  useEffect(() => {
    loadSchedules();
  }, [selectedFacility, selectedMonth]);

  const loadFacilities = async () => {
    try {
      setLoading(true);
      const data = await scheduleApi.getFacilities();
      setFacilities(data);
      setError(null);
    } catch (err) {
      setError('시설 목록을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadSchedules = async () => {
    try {
      setLoading(true);
      const data = await scheduleApi.getSchedules(
        selectedFacility || undefined,
        selectedMonth || undefined
      );
      setSchedules(data);
      setError(null);
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

  // 필터 적용 여부
  const hasFilter = selectedFacility !== '';

  return (
    <div className="space-y-4 pb-20">
      {/* 헤더 - 현재 필터 상태 표시 */}
      <div className="bg-gradient-to-r from-wave-500 to-emerald-500 rounded-xl p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/80 text-xs font-medium">월별 스케줄</p>
            <h1 className="text-xl font-bold text-white">{formatMonth()}</h1>
          </div>
          <div className="text-right">
            {selectedFacility ? (
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-white/20 rounded-lg">
                <span className="text-sm text-white font-medium">{selectedFacility}</span>
                <button
                  onClick={() => setSelectedFacility('')}
                  className="text-white/70 hover:text-white"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ) : (
              <span className="text-sm text-white/70">전체 수영장</span>
            )}
          </div>
        </div>
      </div>

      {/* 요약 정보 */}
      {!loading && !error && schedules.length > 0 && (
        <div className="flex items-center gap-2 px-1">
          <span className="text-sm font-medium text-slate-600">
            {schedules.length}개 시설
          </span>
          {hasFilter && (
            <>
              <span className="text-slate-300">·</span>
              <span className="text-xs text-ocean-600 font-medium">필터 적용됨</span>
            </>
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
            onClick={loadSchedules}
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
              <div className="flex items-center gap-3">
                <div className="w-1 h-10 bg-slate-200 rounded-full" />
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
            <EmptyState message="스케줄 데이터가 없습니다." icon="clipboard" />
          ) : (
            schedules.map((schedule, index) => (
              <CompactScheduleCard
                key={`${schedule.facility_id}-${schedule.valid_month}`}
                schedule={schedule}
                colorIndex={index}
                defaultExpanded={false}
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
        selectedMonth={selectedMonth}
        onMonthChange={(value) => {
          trackFilterUse('month', value);
          setSelectedMonth(value);
        }}
      />
    </div>
  );
}

export default MonthlySchedule;
