import type { DailySchedule, Session } from '../../types/schedule';
import { trackFavoriteToggle } from '../../utils/analytics';

interface FacilityCardProps {
  schedule: DailySchedule;
  isFavorite: boolean;
  onToggleFavorite: () => void;
  onClick: () => void;
}

type AvailabilityStatus =
  | { status: 'closed'; label: string }
  | { status: 'available'; label: string; session: Session }
  | { status: 'upcoming'; label: string; session: Session }
  | { status: 'ended'; label: string };

// 현재 이용 가능 상태 계산
function getAvailabilityStatus(schedule: DailySchedule): AvailabilityStatus {
  if (schedule.is_closed) {
    return { status: 'closed', label: schedule.closure_reason || '휴관' };
  }

  if (schedule.sessions.length === 0) {
    return { status: 'closed', label: '세션 없음' };
  }

  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  // 현재 진행 중인 세션 찾기
  const currentSession = schedule.sessions.find((s) => {
    const [startH, startM] = s.start_time.split(':').map(Number);
    const [endH, endM] = s.end_time.split(':').map(Number);
    const startMinutes = startH * 60 + startM;
    const endMinutes = endH * 60 + endM;
    return currentMinutes >= startMinutes && currentMinutes < endMinutes;
  });

  if (currentSession) {
    return { status: 'available', label: '이용 가능', session: currentSession };
  }

  // 다음 세션 찾기
  const nextSession = schedule.sessions.find((s) => {
    const [startH, startM] = s.start_time.split(':').map(Number);
    const startMinutes = startH * 60 + startM;
    return currentMinutes < startMinutes;
  });

  if (nextSession) {
    return { status: 'upcoming', label: `${nextSession.start_time}~`, session: nextSession };
  }

  return { status: 'ended', label: '오늘 종료' };
}

// 남은 세션 수 계산
function countRemainingSessions(schedule: DailySchedule): number {
  if (schedule.is_closed) return 0;

  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  return schedule.sessions.filter((session) => {
    const [endHour, endMin] = session.end_time.split(':').map(Number);
    const endMinutes = endHour * 60 + endMin;
    return currentMinutes < endMinutes;
  }).length;
}

// 상태별 스타일 설정
const statusStyles = {
  available: {
    badge: 'bg-emerald-100 text-emerald-700',
    dot: 'bg-emerald-500',
    icon: '●',
  },
  upcoming: {
    badge: 'bg-amber-100 text-amber-700',
    dot: 'bg-amber-500',
    icon: '○',
  },
  ended: {
    badge: 'bg-slate-100 text-slate-500',
    dot: 'bg-slate-400',
    icon: '—',
  },
  closed: {
    badge: 'bg-slate-100 text-slate-400',
    dot: 'bg-slate-300',
    icon: '✕',
  },
};

export function FacilityCard({
  schedule,
  isFavorite,
  onToggleFavorite,
  onClick,
}: FacilityCardProps) {
  const availability = getAvailabilityStatus(schedule);
  const remainingCount = countRemainingSessions(schedule);
  const style = statusStyles[availability.status];

  const isClosed = availability.status === 'closed';

  return (
    <div
      className={`
        relative rounded-xl border overflow-hidden
        transition-all active:scale-[0.98]
        ${isClosed
          ? 'bg-slate-100 border-slate-200 border-dashed'
          : 'bg-white hover:shadow-md hover:border-ocean-200'
        }
        ${isFavorite && !isClosed ? 'border-amber-300 ring-1 ring-amber-200' : ''}
        ${!isFavorite && !isClosed ? 'border-slate-200' : ''}
      `}
    >
      {/* 메인 클릭 영역 */}
      <button
        onClick={onClick}
        className="w-full p-4 text-left"
      >
        <div className="flex items-start gap-3">
          {/* 휴관 아이콘 */}
          {isClosed && (
            <div className="flex-shrink-0 w-8 h-8 bg-slate-200 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
          )}

          <div className="flex-1 min-w-0">
            <h3 className={`font-bold text-base truncate pr-8 ${isClosed ? 'text-slate-400' : 'text-slate-800'}`}>
              {schedule.facility_name}
            </h3>

            {/* 상태 배지 */}
            <div className="flex items-center gap-2 mt-1.5">
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${style.badge}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
                {availability.status === 'available' ? '이용 가능' : availability.label}
              </span>

              {/* 추가 정보 */}
              {availability.status === 'available' && 'session' in availability && (
                <span className="text-xs text-slate-400">
                  ~{availability.session.end_time}까지
                </span>
              )}
              {availability.status === 'upcoming' && remainingCount > 0 && (
                <span className="text-xs text-slate-400">
                  오늘 {remainingCount}개 세션
                </span>
              )}
              {availability.status === 'ended' && (
                <span className="text-xs text-slate-400">
                  {schedule.sessions.length}개 세션 모두 종료
                </span>
              )}
            </div>
          </div>
        </div>
      </button>

      {/* 즐겨찾기 버튼 (우측 상단) */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          trackFavoriteToggle(schedule.facility_id, schedule.facility_name, isFavorite ? 'remove' : 'add');
          onToggleFavorite();
        }}
        className={`
          absolute top-3 right-3 p-1.5 rounded-full transition-colors
          ${isFavorite ? 'text-amber-500 bg-amber-50' : 'text-slate-300 hover:text-amber-400 hover:bg-amber-50'}
        `}
        aria-label={isFavorite ? '즐겨찾기 해제' : '즐겨찾기 추가'}
      >
        <svg
          className="w-5 h-5"
          fill={isFavorite ? 'currentColor' : 'none'}
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
      </button>
    </div>
  );
}
