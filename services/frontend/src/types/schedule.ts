export interface Session {
  session_name: string;
  start_time: string;
  end_time: string;
  capacity?: number;
  lanes?: number;
}

export interface ScheduleDetail {
  day_type: string; // "평일", "토요일", "일요일"
  season: string; // "하절기", "동절기", ""
  season_months: string; // "3~10월", "11~2월", ""
  sessions: Session[];
}

export interface Fee {
  category: string;
  price: number;
  note: string;
}

export interface ClosureInfo {
  is_closed: boolean;
  closure_type: 'monthly' | 'partial';
  reason?: string;
  specific_dates?: number;
  regular_closures?: {
    day_of_week: string;
    week_pattern: string | null;
    reason: string | null;
  }[];
}

export interface Schedule {
  facility_id: number;
  facility_name: string;
  valid_month: string;
  schedules: ScheduleDetail[];
  fees?: Fee[];
  notes?: string[];
  source_url?: string;
  created_at?: string;
  closure_info?: ClosureInfo;
}

export interface Facility {
  facility_name: string;
  latest_month: string;
  schedule_count: number;
}

export interface DailySchedule {
  facility_id: number;
  facility_name: string;
  address?: string | null;
  website_url?: string | null;
  date: string;
  day_type: string;
  season: string;
  valid_month: string;
  sessions: Session[];
  source_url?: string;
  notes?: string;
  is_closed: boolean;
  closure_reason?: string | null;
}

export interface CalendarData {
  year: number;
  month: number;
  schedules: Schedule[];
}
