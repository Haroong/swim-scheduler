import axios from 'axios';
import type { Facility, Schedule, CalendarData, DailySchedule } from '../types/schedule';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const scheduleApi = {
  // 시설 목록 조회
  getFacilities: async (): Promise<Facility[]> => {
    const response = await api.get<Facility[]>('/api/facilities');
    return response.data;
  },

  // 스케줄 조회
  getSchedules: async (
    facility?: string,
    month?: string
  ): Promise<Schedule[]> => {
    const params: Record<string, string> = {};
    if (facility) params.facility = facility;
    if (month) params.month = month;

    const response = await api.get<Schedule[]>('/api/schedules', { params });
    return response.data;
  },

  // 일별 스케줄 조회
  getDailySchedules: async (date: string): Promise<DailySchedule[]> => {
    const response = await api.get<DailySchedule[]>('/api/schedules/daily', {
      params: { date },
    });
    return response.data;
  },

  // 달력용 스케줄 조회
  getCalendarData: async (year: number, month: number): Promise<CalendarData> => {
    const response = await api.get<CalendarData>('/api/schedules/calendar', {
      params: { year, month },
    });
    return response.data;
  },
};

export default api;
