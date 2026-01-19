import { useState, useEffect } from 'react';
import { scheduleApi } from '../services/api';
import type { DailySchedule } from '../types/schedule';
import './DailySchedule.css';

function DailySchedulePage() {
  const [schedules, setSchedules] = useState<DailySchedule[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    // 기본값: 오늘 날짜
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
      // JSON 문자열을 파싱
      return JSON.parse(notesStr);
    } catch {
      // 파싱 실패 시 빈 배열 반환
      return [];
    }
  };

  return (
    <div className="daily-schedule-page">
      <div className="date-selector">
        <label htmlFor="date">날짜 선택</label>
        <input
          id="date"
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        />
        <span className="selected-date">{formatDate(selectedDate)}</span>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">로딩 중...</div>
      ) : (
        <div className="daily-schedules-list">
          {schedules.length === 0 ? (
            <div className="no-data">
              {selectedDate}에 운영하는 수영장이 없습니다.
            </div>
          ) : (
            <>
              <div className="schedules-header">
                <h2>운영 중인 수영장 ({schedules.length}개)</h2>
              </div>
              {schedules.map((schedule) => (
                <div key={schedule.facility_id} className="daily-schedule-card">
                  <div className="card-header">
                    <h3>{schedule.facility_name}</h3>
                    <span className="day-type-badge">
                      {schedule.day_type}
                      {schedule.season && ` · ${schedule.season}`}
                    </span>
                  </div>

                  <div className="sessions-grid">
                    {schedule.sessions.map((session, idx) => (
                      <div key={idx} className="session-item">
                        <div className="session-name">{session.session_name}</div>
                        <div className="session-time">
                          {session.start_time.substring(0, 5)} - {session.end_time.substring(0, 5)}
                        </div>
                        <div className="session-info">
                          {session.capacity && (
                            <span className="info-badge">
                              정원 {session.capacity}명
                            </span>
                          )}
                          {session.lanes && (
                            <span className="info-badge">
                              {session.lanes}레인
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {parseNotes(schedule.notes).length > 0 && (
                    <div className="notes-section">
                      <h4>유의사항</h4>
                      <ul>
                        {parseNotes(schedule.notes).map((note, idx) => (
                          <li key={idx}>{note}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {schedule.source_url && (
                    <div className="card-footer">
                      <a
                        href={schedule.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-link"
                      >
                        원본 공지 보기 →
                      </a>
                    </div>
                  )}
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
