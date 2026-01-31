import { useState, useEffect } from 'react';
import { scheduleApi } from '../services/api';
import type { CalendarData, DailySchedule } from '../types/schedule';
import { openSourceUrl } from '../utils/urlUtils';
import { LoadingSpinner, Badge } from '../components/common';

function CalendarView() {
  const [year, setYear] = useState<number>(() => new Date().getFullYear());
  const [month, setMonth] = useState<number>(() => new Date().getMonth() + 1);
  const [calendarData, setCalendarData] = useState<CalendarData | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [dailySchedules, setDailySchedules] = useState<DailySchedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCalendarData();
  }, [year, month]);

  useEffect(() => {
    const today = new Date();
    const isCurrentMonth = today.getFullYear() === year && today.getMonth() + 1 === month;

    if (isCurrentMonth && !selectedDate) {
      const todayStr = `${year}-${month.toString().padStart(2, '0')}-${today.getDate().toString().padStart(2, '0')}`;
      setSelectedDate(todayStr);
    }
  }, [calendarData, year, month]);

  useEffect(() => {
    if (selectedDate) {
      loadDailySchedules(selectedDate);
    }
  }, [selectedDate]);

  const loadCalendarData = async () => {
    try {
      setLoading(true);
      const data = await scheduleApi.getCalendarData(year, month);
      setCalendarData(data);
      setError(null);
    } catch (err) {
      setError('달력 데이터를 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadDailySchedules = async (dateStr: string) => {
    try {
      const data = await scheduleApi.getDailySchedules(dateStr);
      setDailySchedules(data);
    } catch (err) {
      console.error('일별 스케줄 로드 실패:', err);
      setDailySchedules([]);
    }
  };

  const getDaysInMonth = (year: number, month: number): number => {
    return new Date(year, month, 0).getDate();
  };

  const getFirstDayOfMonth = (year: number, month: number): number => {
    return new Date(year, month - 1, 1).getDay();
  };

  const handlePrevMonth = () => {
    if (month === 1) {
      setYear(year - 1);
      setMonth(12);
    } else {
      setMonth(month - 1);
    }
    setSelectedDate(null);
  };

  const handleNextMonth = () => {
    if (month === 12) {
      setYear(year + 1);
      setMonth(1);
    } else {
      setMonth(month + 1);
    }
    setSelectedDate(null);
  };

  const handleDateClick = (day: number) => {
    const dateStr = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
    setSelectedDate(dateStr);
  };

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(year, month);
    const firstDay = getFirstDayOfMonth(year, month);
    const days: JSX.Element[] = [];

    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="aspect-square"></div>);
    }

    const today = new Date();
    const isCurrentMonth = today.getFullYear() === year && today.getMonth() + 1 === month;

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
      const isToday = isCurrentMonth && today.getDate() === day;
      const isSelected = selectedDate === dateStr;
      const dayOfWeek = (firstDay + day - 1) % 7;
      const isSunday = dayOfWeek === 0;
      const isSaturday = dayOfWeek === 6;

      days.push(
        <button
          key={day}
          onClick={() => handleDateClick(day)}
          className={`
            aspect-square rounded-xl flex flex-col items-center justify-center transition-all relative
            ${isSelected
              ? 'bg-gradient-to-br from-ocean-500 to-wave-500 text-white shadow-glow scale-105'
              : isToday
                ? 'bg-ocean-50 text-ocean-700 font-semibold ring-2 ring-ocean-300'
                : 'hover:bg-slate-100 hover:scale-105'
            }
            ${!isSelected && isSunday ? 'text-red-500' : ''}
            ${!isSelected && isSaturday ? 'text-ocean-500' : ''}
          `}
        >
          <span className="text-sm sm:text-base font-semibold">{day}</span>
          {isToday && !isSelected && (
            <span className="w-1.5 h-1.5 bg-ocean-500 rounded-full mt-1"></span>
          )}
        </button>
      );
    }

    return days;
  };

  const formatSelectedDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    const weekday = weekdays[date.getDay()];
    return `${date.getDate()}일 (${weekday})`;
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
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Calendar */}
      <div className="bg-white rounded-2xl shadow-soft border border-slate-200 overflow-hidden">
        {/* Header with Ocean Gradient */}
        <div className="bg-gradient-to-r from-ocean-500 to-wave-500 p-6 relative overflow-hidden">
          {/* Wave decoration */}
          <div className="absolute inset-0 opacity-10">
            <svg className="absolute bottom-0 w-full h-16" viewBox="0 0 1440 100" preserveAspectRatio="none">
              <path fill="white" d="M0,50 C240,80 480,20 720,50 C960,80 1200,20 1440,50 L1440,100 L0,100 Z" />
            </svg>
          </div>

          <div className="flex items-center justify-between relative">
            <button
              onClick={handlePrevMonth}
              className="w-11 h-11 rounded-xl bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all hover:scale-110 shadow-lg"
            >
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {year}년 {month}월
            </h2>
            <button
              onClick={handleNextMonth}
              className="w-11 h-11 rounded-xl bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all hover:scale-110 shadow-lg"
            >
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        <div className="p-6">

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <LoadingSpinner message="로딩 중..." />
        ) : (
          <>
            {/* Weekdays */}
            <div className="grid grid-cols-7 gap-1 mb-2">
              {['일', '월', '화', '수', '목', '금', '토'].map((day, idx) => (
                <div
                  key={day}
                  className={`
                    text-center text-sm font-medium py-2
                    ${idx === 0 ? 'text-red-500' : idx === 6 ? 'text-blue-500' : 'text-slate-500'}
                  `}
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-1">
              {renderCalendar()}
            </div>

            {/* Info */}
            <div className="mt-6 text-center text-sm text-slate-400">
              날짜를 클릭하면 해당 날짜의 운영 시설을 확인할 수 있습니다
            </div>
          </>
        )}
        </div>
      </div>

      {/* Daily Detail */}
      <div className="bg-white rounded-2xl shadow-soft border border-slate-200 overflow-hidden">
        {selectedDate ? (
          <>
            {/* Detail Header */}
            <div className="p-6 bg-gradient-to-r from-wave-500 to-emerald-500 relative overflow-hidden">
              {/* Wave decoration */}
              <div className="absolute inset-0 opacity-10">
                <svg className="absolute bottom-0 w-full h-16" viewBox="0 0 1440 100" preserveAspectRatio="none">
                  <path fill="white" d="M0,50 C240,80 480,20 720,50 C960,80 1200,20 1440,50 L1440,100 L0,100 Z" />
                </svg>
              </div>

              <div className="flex items-center gap-4 relative">
                <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center text-white font-bold text-2xl shadow-lg">
                  {new Date(selectedDate).getDate()}
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-1">
                    {formatSelectedDate(selectedDate)}
                  </h3>
                  <p className="text-sm text-white/90 font-medium flex items-center gap-2">
                    {dailySchedules.length > 0 ? (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        {dailySchedules.length}개 수영장 운영
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                        </svg>
                        운영하는 수영장 없음
                      </>
                    )}
                  </p>
                </div>
              </div>
            </div>

            {/* Detail Content */}
            <div className="p-6 max-h-[600px] overflow-y-auto">
              {dailySchedules.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                    </svg>
                  </div>
                  <p className="text-slate-500">이 날은 운영하는 수영장이 없습니다.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {dailySchedules.map((schedule, idx) => (
                    <div
                      key={schedule.facility_id}
                      className="bg-gradient-to-br from-slate-50 to-slate-100/50 rounded-2xl p-5 border border-slate-200 hover:shadow-md transition-all"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-2">
                          <div className={`w-3 h-3 rounded-full ${idx % 3 === 0 ? 'bg-ocean-500' : idx % 3 === 1 ? 'bg-wave-500' : 'bg-emerald-500'}`} />
                          <h4 className="font-bold text-slate-800 text-lg">
                            {schedule.facility_name}
                          </h4>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Badge variant="ocean" size="sm">{schedule.day_type}</Badge>
                          {schedule.season && (
                            <Badge variant="wave" size="sm">{schedule.season}</Badge>
                          )}
                        </div>
                      </div>

                      <div className="grid grid-cols-1 gap-2">
                        {schedule.sessions.map((session, sidx) => (
                          <div
                            key={sidx}
                            className="flex items-center justify-between bg-white rounded-xl p-3.5 shadow-sm border border-slate-100"
                          >
                            <span className="font-semibold text-slate-700 text-sm">
                              {session.session_name}
                            </span>
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-wave-600 font-bold text-sm">
                              {session.start_time.substring(0, 5)} - {session.end_time.substring(0, 5)}
                            </span>
                          </div>
                        ))}
                      </div>

                      {parseNotes(schedule.notes).length > 0 && (
                        <div className="mt-3 pt-3 border-t border-slate-200">
                          <p className="text-xs text-amber-600">
                            {parseNotes(schedule.notes)[0]}
                          </p>
                        </div>
                      )}

                      {schedule.source_url && (
                        <button
                          onClick={() => openSourceUrl(schedule.source_url!)}
                          className="mt-3 w-full py-2 text-sm text-slate-500 hover:text-primary-600 transition-colors flex items-center justify-center gap-1"
                        >
                          원본 공지 보기
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full min-h-[400px]">
            <div className="text-center">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <p className="text-slate-500">날짜를 선택해주세요</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CalendarView;
