import { useState, useEffect } from 'react';
import { scheduleApi } from '../services/api';
import type { DailySchedule } from '../types/schedule';
import { openSourceUrl } from '../utils/urlUtils';
import { LoadingSpinner, EmptyState, SessionCard, NotesSection, Badge } from '../components/common';

function DailySchedulePage() {
  const [schedules, setSchedules] = useState<DailySchedule[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDailySchedules();
  }, [selectedDate]);

  const loadDailySchedules = async () => {
    if (!selectedDate) return;

    try {
      setLoading(true);
      const data = await scheduleApi.getDailySchedules(selectedDate);
      setSchedules(data);
      setError(null);
    } catch (err) {
      setError('스케줄을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    const weekday = weekdays[date.getDay()];
    return `${year}년 ${month}월 ${day}일 (${weekday})`;
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
    <div className="space-y-6">
      {/* Date Selector with Ocean Theme */}
      <div className="bg-gradient-to-r from-ocean-500 to-wave-500 rounded-2xl shadow-soft p-6 sm:p-8 relative overflow-hidden">
        {/* Wave Pattern Background */}
        <div className="absolute inset-0 opacity-10">
          <svg className="absolute bottom-0 w-full h-24" viewBox="0 0 1440 100" preserveAspectRatio="none">
            <path fill="white" d="M0,50 C240,80 480,20 720,50 C960,80 1200,20 1440,50 L1440,100 L0,100 Z" />
          </svg>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6 relative">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <label htmlFor="date" className="block text-sm font-semibold text-white/90 mb-1">
                날짜 선택
              </label>
              <input
                id="date"
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="text-lg font-bold text-white bg-transparent border-none focus:outline-none cursor-pointer"
              />
            </div>
          </div>
          <div className="sm:ml-auto">
            <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-white/20 backdrop-blur-sm rounded-2xl text-base font-bold text-white shadow-lg">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {formatDate(selectedDate)}
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <LoadingSpinner message="스케줄을 불러오는 중..." />
      ) : (
        <div className="space-y-4">
          {schedules.length === 0 ? (
            <EmptyState message={`${selectedDate}에 운영하는 수영장이 없습니다.`} icon="minus" />
          ) : (
            <>
              {/* Header */}
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <svg className="w-6 h-6 text-ocean-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                  수영장 현황
                </h2>
                <div className="flex items-center gap-2">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-ocean-50 to-wave-50 text-ocean-700 rounded-lg text-sm font-bold border border-ocean-200">
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    운영 {schedules.filter(s => !s.is_closed).length}개
                  </div>
                  {schedules.filter(s => s.is_closed).length > 0 && (
                    <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 text-slate-500 rounded-lg text-sm font-bold border border-slate-200">
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      휴관 {schedules.filter(s => s.is_closed).length}개
                    </div>
                  )}
                </div>
              </div>

              {/* Schedule Cards */}
              {schedules.map((schedule, index) => (
                <div
                  key={schedule.facility_id}
                  className="bg-white rounded-2xl shadow-soft border border-slate-200 overflow-hidden hover:shadow-lg transition-all flex"
                >
                  {/* Left Color Bar */}
                  <div className={`w-2 ${schedule.is_closed ? 'bg-gradient-to-b from-slate-400 to-slate-500' : index % 3 === 0 ? 'bg-gradient-to-b from-ocean-500 to-wave-500' : index % 3 === 1 ? 'bg-gradient-to-b from-wave-500 to-emerald-500' : 'bg-gradient-to-b from-emerald-500 to-teal-500'}`} />

                  <div className="flex-1">
                  {/* Card Header */}
                  <div className="p-6 border-b border-slate-100">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${schedule.is_closed ? 'bg-slate-400' : index % 3 === 0 ? 'bg-ocean-500' : index % 3 === 1 ? 'bg-wave-500' : 'bg-emerald-500'}`} />
                        <div>
                          <h3 className={`text-xl font-bold ${schedule.is_closed ? 'text-slate-500' : 'text-slate-800'}`}>
                            {schedule.facility_name}
                          </h3>
                          <div className="flex items-center gap-2 mt-2">
                            {schedule.is_closed ? (
                              <Badge variant="slate">휴관</Badge>
                            ) : (
                              <>
                                <Badge variant={index % 3 === 0 ? 'ocean' : index % 3 === 1 ? 'wave' : 'emerald'}>
                                  {schedule.day_type}
                                </Badge>
                                {schedule.season && (
                                  <Badge variant="wave">{schedule.season}</Badge>
                                )}
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Sessions Grid or Closure Notice */}
                  <div className="p-6">
                    {schedule.is_closed ? (
                      <div className="flex flex-col items-center justify-center py-8 bg-slate-50 rounded-xl">
                        <svg className="w-12 h-12 text-slate-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6" />
                        </svg>
                        <p className="text-lg font-bold text-slate-500 mb-1">휴관</p>
                        {schedule.closure_reason && (
                          <p className="text-sm text-slate-400">{schedule.closure_reason}</p>
                        )}
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        {schedule.sessions.map((session, idx) => (
                          <SessionCard
                            key={idx}
                            session={session}
                            colorScheme={index % 3 === 0 ? 'ocean' : index % 3 === 1 ? 'wave' : 'emerald'}
                          />
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Notes Section */}
                  {parseNotes(schedule.notes).length > 0 && (
                    <div className="px-5 pb-5">
                      <NotesSection notes={parseNotes(schedule.notes)} />
                    </div>
                  )}

                  {/* Card Footer */}
                  {schedule.source_url && (
                    <div className="px-6 pb-6">
                      <button
                        onClick={() => openSourceUrl(schedule.source_url!)}
                        className="w-full py-3.5 bg-gradient-to-r from-slate-50 to-slate-100 hover:from-slate-100 hover:to-slate-200 rounded-xl text-slate-700 font-semibold transition-all flex items-center justify-center gap-2 border border-slate-200 hover:border-slate-300 hover:shadow-md"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                        원본 공지 보기
                      </button>
                    </div>
                  )}
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default DailySchedulePage;
