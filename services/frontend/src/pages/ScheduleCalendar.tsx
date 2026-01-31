import { useState, useEffect } from 'react';
import { scheduleApi } from '../services/api';
import type { Facility, Schedule } from '../types/schedule';
import { openSourceUrl } from '../utils/urlUtils';
import { LoadingSpinner, EmptyState, SessionCard, NotesSection } from '../components/common';

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
      {/* Filters with Ocean Theme */}
      <div className="bg-gradient-to-r from-wave-500 to-emerald-500 rounded-2xl shadow-soft p-6 sm:p-8 relative overflow-hidden">
        {/* Wave Pattern Background */}
        <div className="absolute inset-0 opacity-10">
          <svg className="absolute bottom-0 w-full h-24" viewBox="0 0 1440 100" preserveAspectRatio="none">
            <path fill="white" d="M0,50 C240,80 480,20 720,50 C960,80 1200,20 1440,50 L1440,100 L0,100 Z" />
          </svg>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 relative">
          <div className="flex-1">
            <label htmlFor="facility" className="block text-sm font-semibold text-white/90 mb-2 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
              수영장 선택
            </label>
            <select
              id="facility"
              value={selectedFacility}
              onChange={(e) => setSelectedFacility(e.target.value)}
              className="w-full px-4 py-3 bg-white/95 backdrop-blur-sm border-none rounded-xl focus:outline-none focus:ring-2 focus:ring-white/50 transition-all text-slate-700 font-semibold shadow-lg"
            >
              <option value="">전체 수영장</option>
              {facilities.map((facility) => (
                <option key={facility.facility_name} value={facility.facility_name}>
                  {facility.facility_name}
                </option>
              ))}
            </select>
          </div>

          <div className="sm:w-64">
            <label htmlFor="month" className="block text-sm font-semibold text-white/90 mb-2 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              월 선택
            </label>
            <input
              id="month"
              type="month"
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="w-full px-4 py-3 bg-white/95 backdrop-blur-sm border-none rounded-xl focus:outline-none focus:ring-2 focus:ring-white/50 transition-all text-slate-700 font-semibold shadow-lg"
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
        <LoadingSpinner message="스케줄을 불러오는 중..." />
      ) : (
        <div className="space-y-6">
          {schedules.length === 0 ? (
            <EmptyState message="스케줄 데이터가 없습니다." icon="clipboard" />
          ) : (
            schedules.map((schedule, index) => (
              <div
                key={`${schedule.facility_id}-${schedule.valid_month}`}
                className="bg-white rounded-2xl shadow-soft border border-slate-200 overflow-hidden hover:shadow-lg transition-all"
              >
                {/* Header */}
                <div className={`p-6 border-b border-slate-100 relative overflow-hidden ${index % 3 === 0 ? 'bg-gradient-to-r from-ocean-500 to-wave-500' : index % 3 === 1 ? 'bg-gradient-to-r from-wave-500 to-emerald-500' : 'bg-gradient-to-r from-emerald-500 to-teal-500'}`}>
                  {/* Wave decoration */}
                  <div className="absolute inset-0 opacity-10">
                    <svg className="absolute bottom-0 w-full h-16" viewBox="0 0 1440 100" preserveAspectRatio="none">
                      <path fill="white" d="M0,50 C240,80 480,20 720,50 C960,80 1200,20 1440,50 L1440,100 L0,100 Z" />
                    </svg>
                  </div>

                  <div className="flex items-center justify-between relative">
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full bg-white/80`} />
                      {schedule.facility_name}
                    </h2>
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/20 text-white rounded-xl text-sm font-bold backdrop-blur-sm shadow-lg">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {schedule.valid_month}
                    </div>
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
                          <SessionCard
                            key={sidx}
                            session={session}
                            colorScheme={index % 3 === 0 ? 'ocean' : index % 3 === 1 ? 'wave' : 'emerald'}
                          />
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
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default ScheduleCalendar;
