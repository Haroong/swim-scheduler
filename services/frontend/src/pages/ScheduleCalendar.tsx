import { useState, useEffect } from 'react';
import { scheduleApi } from '../services/api';
import type { Facility, Schedule } from '../types/schedule';
import './ScheduleCalendar.css';

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

  // 초기 시설 목록 로드
  useEffect(() => {
    loadFacilities();
  }, []);

  // 시설 또는 월이 변경되면 스케줄 로드
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
    <div className="schedule-calendar">
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="facility">시설</label>
          <select
            id="facility"
            value={selectedFacility}
            onChange={(e) => setSelectedFacility(e.target.value)}
          >
            <option value="">전체</option>
            {facilities.map((facility) => (
              <option key={facility.facility_name} value={facility.facility_name}>
                {facility.facility_name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="month">월</label>
          <input
            id="month"
            type="month"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
          />
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">로딩 중...</div>
      ) : (
        <div className="schedules-list">
          {schedules.length === 0 ? (
            <div className="no-data">스케줄 데이터가 없습니다.</div>
          ) : (
            schedules.map((schedule) => (
              <div key={`${schedule.facility_id}-${schedule.valid_month}`} className="schedule-card">
                <div className="schedule-header">
                  <h2>{schedule.facility_name}</h2>
                  <span className="valid-month">{schedule.valid_month}</span>
                </div>

                <div className="schedule-content">
                  {schedule.schedules.map((detail, idx) => (
                    <div key={idx} className="schedule-detail">
                      <h3>
                        {detail.day_type}
                        {detail.season && ` (${detail.season})`}
                      </h3>
                      {detail.season_months && (
                        <p className="season-months">{detail.season_months}</p>
                      )}
                      <div className="sessions">
                        {detail.sessions.map((session, sidx) => (
                          <div key={sidx} className="session">
                            <span className="session-name">{session.session_name}</span>
                            <span className="session-time">
                              {session.start_time} - {session.end_time}
                            </span>
                            {session.capacity && (
                              <span className="session-capacity">
                                정원: {session.capacity}명
                              </span>
                            )}
                            {session.lanes && (
                              <span className="session-lanes">
                                레인: {session.lanes}개
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}

                  {schedule.fees && schedule.fees.length > 0 && (
                    <div className="fees">
                      <h3>이용료</h3>
                      {schedule.fees.map((fee, idx) => (
                        <div key={idx} className="fee-item">
                          <span>{fee.category}</span>
                          <span>{fee.price.toLocaleString()}원</span>
                          <span className="fee-note">{fee.note}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {schedule.notes && schedule.notes.length > 0 && (
                    <div className="notes">
                      <h3>유의사항</h3>
                      <ul>
                        {schedule.notes.map((note, idx) => (
                          <li key={idx}>{note}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {schedule.source_url && (
                  <div className="schedule-footer">
                    <a
                      href={schedule.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      원본 보기
                    </a>
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
