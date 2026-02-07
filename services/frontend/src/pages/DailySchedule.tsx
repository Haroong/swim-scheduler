import { useState, useEffect, useCallback } from 'react';
import { scheduleApi } from '../services/api';
import type { DailySchedule } from '../types/schedule';
import { trackFacilityView } from '../utils/analytics';
import { EmptyState } from '../components/common';
import { FacilityGrid, ScheduleDetail } from '../components/daily';
import { useFavorites } from '../hooks';

function DailySchedulePage() {
  const [schedules, setSchedules] = useState<DailySchedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [, setTick] = useState(0);
  const { favorites, toggleFavorite, isFavorite } = useFavorites();

  // 선택된 수영장 (null이면 목록 표시)
  const [selectedFacilityId, setSelectedFacilityId] = useState<number | null>(null);

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

  // 목록 뷰 표시
  return (
    <div className="space-y-4">
      {/* 날짜 */}
      <div className="px-1">
        <span className="text-sm font-semibold text-slate-700">{formatDate()}</span>
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
          action={{
            label: '다른 날짜 보기',
            onClick: () => {
              window.location.href = '/calendar';
            },
          }}
        />
      ) : (
        <FacilityGrid
          schedules={schedules}
          favorites={favorites}
          onSelectFacility={handleSelectFacility}
          toggleFavorite={toggleFavorite}
        />
      )}
    </div>
  );
}

export default DailySchedulePage;
