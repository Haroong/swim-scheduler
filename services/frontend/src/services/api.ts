import axios from 'axios';
import type { Facility, Schedule, CalendarData, DailySchedule } from '../types/schedule';
import type { Review, ReviewStats, ReviewCreatePayload, ReviewUpdatePayload } from '../types/review';
import type { User, AuthResponse } from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// JWT 토큰 자동 첨부 인터셉터
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
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

export const reviewApi = {
  getReviews: async (facilityId: number): Promise<Review[]> => {
    const response = await api.get<Review[]>('/api/reviews', {
      params: { facility_id: facilityId },
    });
    return response.data;
  },

  getReviewStats: async (facilityId: number): Promise<ReviewStats> => {
    const response = await api.get<ReviewStats>('/api/reviews/stats', {
      params: { facility_id: facilityId },
    });
    return response.data;
  },

  createReview: async (payload: ReviewCreatePayload): Promise<Review> => {
    const response = await api.post<Review>('/api/reviews', payload);
    return response.data;
  },

  updateReview: async (reviewId: number, payload: ReviewUpdatePayload): Promise<Review> => {
    const response = await api.put<Review>(`/api/reviews/${reviewId}`, payload);
    return response.data;
  },

  deleteReview: async (reviewId: number, password: string): Promise<void> => {
    await api.delete(`/api/reviews/${reviewId}`, {
      data: { password },
    });
  },
};

export const authApi = {
  googleLogin: async (credential: string): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/auth/google', { credential });
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/api/auth/me');
    return response.data;
  },
};

export default api;
