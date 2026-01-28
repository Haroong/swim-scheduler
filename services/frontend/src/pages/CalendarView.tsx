import { useState, useEffect } from 'react';
import { scheduleApi } from '../services/api';
import type { CalendarData, DailySchedule } from '../types/schedule';
import { openSourceUrl } from '../utils/urlUtils';
import './CalendarView.css';

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

  // 오늘 날짜 자동 선택 (현재 월인 경우에만)
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

    // 이전 달의 빈 칸
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    // 현재 달의 날짜
    const today = new Date();
    const isCurrentMonth = today.getFullYear() === year && today.getMonth() + 1 === month;

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
      const isToday = isCurrentMonth && today.getDate() === day;
      const isSelected = selectedDate === dateStr;

      days.push(
        <div
          key={day}
          className={`calendar-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}`}
          onClick={() => handleDateClick(day)}
        >
          <div className="day-number">{day}</div>
          <div className="day-indicator"></div>
        </div>
      );
    }

    return days;
  };

  const formatSelectedDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    const weekday = weekdays[date.getDay()];
    return `${year}년 ${month}월 ${date.getDate()}일 (${weekday})`;
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
    <div className="calendar-view">
      <div className="calendar-container">
        <div className="calendar-header">
          <button onClick={handlePrevMonth} className="nav-button">‹</button>
          <h2>{year}년 {month}월</h2>
          <button onClick={handleNextMonth} className="nav-button">›</button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="loading">로딩 중...</div>
        ) : (
          <>
            <div className="calendar-weekdays">
              <div className="weekday sunday">일</div>
              <div className="weekday">월</div>
              <div className="weekday">화</div>
              <div className="weekday">수</div>
              <div className="weekday">목</div>
              <div className="weekday">금</div>
              <div className="weekday saturday">토</div>
            </div>

            <div className="calendar-grid">
              {renderCalendar()}
            </div>

            <div className="calendar-info">
              날짜를 클릭하면 해당 날짜의 운영 시설을 확인할 수 있습니다.
            </div>
          </>
        )}
      </div>

      {selectedDate && (
        <div className="daily-detail">
          <h3>{formatSelectedDate(selectedDate)}</h3>
          {dailySchedules.length === 0 ? (
            <div className="no-schedules">
              이 날은 운영하는 수영장이 없습니다.
            </div>
          ) : (
            <div className="schedules-list">
              {dailySchedules.map((schedule) => (
                <div key={schedule.facility_id} className="schedule-card">
                  <div className="card-header">
                    <h4>{schedule.facility_name}</h4>
                    <span className="day-type-badge">
                      {schedule.day_type}
                      {schedule.season && ` · ${schedule.season}`}
                    </span>
                  </div>

                  <div className="sessions">
                    {schedule.sessions.map((session, idx) => (
                      <div key={idx} className="session">
                        <div className="session-name">{session.session_name}</div>
                        <div className="session-time">
                          {session.start_time.substring(0, 5)} - {session.end_time.substring(0, 5)}
                        </div>
                        <div className="session-details">
                          {session.capacity && <span>정원 {session.capacity}명</span>}
                          {session.lanes && <span>{session.lanes}레인</span>}
                        </div>
                      </div>
                    ))}
                  </div>

                  {parseNotes(schedule.notes).length > 0 && (
                    <div className="notes">
                      <h5>유의사항</h5>
                      <ul>
                        {parseNotes(schedule.notes).map((note, idx) => (
                          <li key={idx}>{note}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {schedule.source_url && (
                    <button
                      onClick={() => openSourceUrl(schedule.source_url!)}
                      className="source-link"
                    >
                      원본 공지 보기 →
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default CalendarView;
