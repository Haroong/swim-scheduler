import type { DailySchedule } from '../../types/schedule';
import { trackFavoriteToggle } from '../../utils/analytics';

interface FacilityCardProps {
  schedule: DailySchedule;
  isFavorite: boolean;
  onToggleFavorite: () => void;
  onClick: () => void;
}

// 종료된 세션 수 계산
function countPastSessions(schedule: DailySchedule): number {
  if (schedule.is_closed) return 0;

  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  return schedule.sessions.filter((session) => {
    const [endHour, endMin] = session.end_time.split(':').map(Number);
    const endMinutes = endHour * 60 + endMin;
    return currentMinutes >= endMinutes;
  }).length;
}

export function FacilityCard({
  schedule,
  isFavorite,
  onToggleFavorite,
  onClick,
}: FacilityCardProps) {
  const sessionCount = schedule.sessions.length;
  const pastCount = countPastSessions(schedule);

  return (
    <div
      className={`
        relative bg-white rounded-xl border overflow-hidden
        transition-all active:scale-[0.98]
        ${isFavorite ? 'border-amber-300 ring-1 ring-amber-200' : 'border-slate-200'}
        ${schedule.is_closed ? 'opacity-60' : 'hover:shadow-md hover:border-ocean-200'}
      `}
    >
      {/* 메인 클릭 영역 */}
      <button
        onClick={onClick}
        className="w-full p-4 text-left"
      >
        <h3 className={`font-bold text-base truncate pr-8 ${schedule.is_closed ? 'text-slate-400' : 'text-slate-800'}`}>
          {schedule.facility_name}
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          {schedule.is_closed
            ? (schedule.closure_reason || '휴관')
            : `${sessionCount}개 세션${pastCount > 0 ? ` · ${pastCount}개 종료` : ''}`
          }
        </p>
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
