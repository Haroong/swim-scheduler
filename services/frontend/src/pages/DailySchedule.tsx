import { useState, useEffect } from 'react';
import { scheduleApi } from '../services/api';
import type { DailySchedule } from '../types/schedule';
import { openSourceUrl } from '../utils/urlUtils';

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
      {/* Date Selector */}
      <div className="bg-gradient-to-r from-primary-500 to-cyan-500 rounded-2xl shadow-lg p-6">
        <div className="flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <label htmlFor="date" className="block text-sm font-medium text-white/80">
                날짜 선택
              </label>
              <input
                id="date"
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="mt-1 text-lg font-semibold text-white bg-transparent border-none focus:outline-none cursor-pointer"
              />
            </div>
          </div>
          <div className="sm:ml-auto">
            <span className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur rounded-full text-sm font-medium text-white">
              {formatDate(selectedDate)}
            </span>
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
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
            <p className="text-slate-500">스케줄을 불러오는 중...</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {schedules.length === 0 ? (
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-12 text-center">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                </svg>
              </div>
              <p className="text-slate-500">{selectedDate}에 운영하는 수영장이 없습니다.</p>
            </div>
          ) : (
            <>
              {/* Header */}
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-800">
                  운영 중인 수영장
                </h2>
                <span className="inline-flex items-center px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                  {schedules.length}개
                </span>
              </div>

              {/* Schedule Cards */}
              {schedules.map((schedule, index) => (
                <div
                  key={schedule.facility_id}
                  className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow flex"
                >
                  {/* Left Color Bar */}
                  <div className={`w-1.5 ${index % 3 === 0 ? 'bg-gradient-to-b from-primary-500 to-cyan-500' : index % 3 === 1 ? 'bg-gradient-to-b from-emerald-500 to-teal-500' : 'bg-gradient-to-b from-violet-500 to-purple-500'}`} />

                  <div className="flex-1">
                  {/* Card Header */}
                  <div className="p-5 border-b border-slate-100">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-lg font-bold text-slate-800">
                          {schedule.facility_name}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-sm ${index % 3 === 0 ? 'bg-primary-50 text-primary-700' : index % 3 === 1 ? 'bg-emerald-50 text-emerald-700' : 'bg-violet-50 text-violet-700'}`}>
                            {schedule.day_type}
                          </span>
                          {schedule.season && (
                            <span className="inline-flex items-center px-2.5 py-0.5 bg-cyan-50 text-cyan-700 rounded-md text-sm">
                              {schedule.season}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Sessions Grid */}
                  <div className="p-5">
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                      {schedule.sessions.map((session, idx) => (
                        <div
                          key={idx}
                          className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl p-4 hover:from-slate-100 hover:to-slate-150 transition-all border border-slate-200/50"
                        >
                          <div className="font-medium text-slate-800 mb-1">
                            {session.session_name}
                          </div>
                          <div className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-cyan-600 font-bold text-lg">
                            {session.start_time.substring(0, 5)} - {session.end_time.substring(0, 5)}
                          </div>
                          {(session.capacity || session.lanes) && (
                            <div className="flex flex-wrap gap-2 mt-2">
                              {session.capacity && (
                                <span className="text-xs text-slate-600 bg-white px-2 py-1 rounded-full border border-slate-200">
                                  정원 {session.capacity}명
                                </span>
                              )}
                              {session.lanes && (
                                <span className="text-xs text-slate-600 bg-white px-2 py-1 rounded-full border border-slate-200">
                                  {session.lanes}레인
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Notes Section */}
                  {parseNotes(schedule.notes).length > 0 && (
                    <div className="px-5 pb-5">
                      <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
                        <h4 className="text-sm font-medium text-amber-800 mb-2 flex items-center gap-2">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          유의사항
                        </h4>
                        <ul className="space-y-1">
                          {parseNotes(schedule.notes).map((note, idx) => (
                            <li key={idx} className="text-sm text-amber-700 flex items-start gap-2">
                              <span className="text-amber-400 mt-1">•</span>
                              {note}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  {/* Card Footer */}
                  {schedule.source_url && (
                    <div className="px-5 pb-5">
                      <button
                        onClick={() => openSourceUrl(schedule.source_url!)}
                        className="w-full py-3 bg-gradient-to-r from-slate-100 to-slate-200 hover:from-slate-200 hover:to-slate-300 rounded-xl text-slate-700 font-medium transition-all flex items-center justify-center gap-2"
                      >
                        원본 공지 보기
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
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
