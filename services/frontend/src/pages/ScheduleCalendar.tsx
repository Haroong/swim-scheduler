import { useState, useEffect } from 'react';
import { scheduleApi } from '../services/api';
import type { Facility, Schedule } from '../types/schedule';
import { openSourceUrl } from '../utils/urlUtils';

function ScheduleCalendar() {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [selectedFacility, setSelectedFacility] = useState<string>('');
  const [selectedMonth, setSelectedMonth] = useState<string>(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label htmlFor="facility" className="block text-sm font-medium text-slate-600 mb-2">
              수영장 선택
            </label>
            <select
              id="facility"
              value={selectedFacility}
              onChange={(e) => setSelectedFacility(e.target.value)}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            >
              <option value="">전체 수영장</option>
              {facilities.map((facility) => (
                <option key={facility.facility_name} value={facility.facility_name}>
                  {facility.facility_name}
                </option>
              ))}
            </select>
          </div>

          <div className="sm:w-48">
            <label htmlFor="month" className="block text-sm font-medium text-slate-600 mb-2">
              월 선택
            </label>
            <input
              id="month"
              type="month"
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
            <p className="text-slate-500">스케줄을 불러오는 중...</p>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {schedules.length === 0 ? (
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-12 text-center">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <p className="text-slate-500">스케줄 데이터가 없습니다.</p>
            </div>
          ) : (
            schedules.map((schedule) => (
              <div
                key={`${schedule.facility_id}-${schedule.valid_month}`}
                className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden"
              >
                {/* Header */}
                <div className="p-6 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
                  <div className="flex items-center justify-between">
                    <h2 className="text-xl font-bold text-slate-800">
                      {schedule.facility_name}
                    </h2>
                    <span className="inline-flex items-center px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                      {schedule.valid_month}
                    </span>
                  </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                  {schedule.schedules.map((detail, idx) => (
                    <div key={idx} className="space-y-4">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-slate-800">
                          {detail.day_type}
                          {detail.season && (
                            <span className="ml-2 text-primary-600 font-medium">
                              ({detail.season})
                            </span>
                          )}
                        </h3>
                        {detail.season_months && (
                          <span className="text-sm text-slate-500">
                            {detail.season_months}
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        {detail.sessions.map((session, sidx) => (
                          <div
                            key={sidx}
                            className="bg-slate-50 rounded-xl p-4 hover:bg-slate-100 transition-colors"
                          >
                            <div className="font-medium text-slate-800 mb-1">
                              {session.session_name}
                            </div>
                            <div className="text-primary-600 font-semibold">
                              {session.start_time} - {session.end_time}
                            </div>
                            {(session.capacity || session.lanes) && (
                              <div className="flex flex-wrap gap-2 mt-2">
                                {session.capacity && (
                                  <span className="text-xs text-slate-500 bg-white px-2 py-1 rounded">
                                    정원 {session.capacity}명
                                  </span>
                                )}
                                {session.lanes && (
                                  <span className="text-xs text-slate-500 bg-white px-2 py-1 rounded">
                                    {session.lanes}레인
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}

                  {/* Fees */}
                  {schedule.fees && schedule.fees.length > 0 && (
                    <div className="bg-green-50 border border-green-100 rounded-xl p-5">
                      <h3 className="text-sm font-medium text-green-800 mb-3 flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        이용료
                      </h3>
                      <div className="space-y-2">
                        {schedule.fees.map((fee, idx) => (
                          <div key={idx} className="flex items-center justify-between text-sm">
                            <span className="text-green-700">{fee.category}</span>
                            <div className="flex items-center gap-3">
                              <span className="font-semibold text-green-800">
                                {fee.price.toLocaleString()}원
                              </span>
                              {fee.note && (
                                <span className="text-green-600 text-xs">
                                  {fee.note}
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Notes */}
                  {schedule.notes && schedule.notes.length > 0 && (
                    <div className="bg-amber-50 border border-amber-100 rounded-xl p-5">
                      <h3 className="text-sm font-medium text-amber-800 mb-3 flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        유의사항
                      </h3>
                      <ul className="space-y-1">
                        {schedule.notes.map((note, idx) => (
                          <li key={idx} className="text-sm text-amber-700 flex items-start gap-2">
                            <span className="text-amber-400 mt-1">•</span>
                            {note}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Footer */}
                {schedule.source_url && (
                  <div className="px-6 pb-6">
                    <button
                      onClick={() => openSourceUrl(schedule.source_url!)}
                      className="w-full py-3 bg-slate-100 hover:bg-slate-200 rounded-xl text-slate-600 font-medium transition-colors flex items-center justify-center gap-2"
                    >
                      원본 공지 보기
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default ScheduleCalendar;
