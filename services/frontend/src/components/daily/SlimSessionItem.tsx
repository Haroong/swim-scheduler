import type { Session } from '../../types/schedule';

interface SlimSessionItemProps {
  session: Session;
  status: 'past' | 'current' | 'upcoming';
  isNext: boolean;
}

export function SlimSessionItem({ session, status, isNext }: SlimSessionItemProps) {
  const isPast = status === 'past';
  const isCurrent = status === 'current';

  return (
    <div className={`
      flex items-center gap-2 px-3 py-2.5 rounded-lg transition-all
      ${isPast
        ? 'bg-slate-50 opacity-50'
        : isCurrent
          ? 'bg-green-50 border-l-4 border-green-500'
          : isNext
            ? 'bg-ocean-50 border-l-4 border-ocean-500'
            : 'bg-slate-50/50 hover:bg-slate-50'
      }
    `}>
      {/* 세션명 */}
      <span className={`
        w-10 text-sm font-semibold
        ${isPast ? 'text-slate-400' : isCurrent ? 'text-green-700' : isNext ? 'text-ocean-700' : 'text-slate-700'}
      `}>
        {session.session_name}
      </span>

      {/* 시간 */}
      <span className={`
        flex-1 text-sm font-mono
        ${isPast ? 'text-slate-400 line-through' : isCurrent ? 'text-green-600 font-semibold' : isNext ? 'text-ocean-600 font-semibold' : 'text-slate-600'}
      `}>
        {session.start_time.substring(0, 5)} - {session.end_time.substring(0, 5)}
      </span>

      {/* 정원 */}
      {session.capacity && (
        <span className={`
          text-xs px-2 py-0.5 rounded-full
          ${isPast
            ? 'bg-slate-100 text-slate-400'
            : isCurrent
              ? 'bg-green-100 text-green-700'
              : isNext
                ? 'bg-ocean-100 text-ocean-700'
                : 'bg-slate-100 text-slate-500'
          }
        `}>
          {session.capacity}명
        </span>
      )}

      {/* 상태 뱃지 */}
      {isCurrent && (
        <span className="text-[10px] font-bold text-white bg-green-500 px-1.5 py-0.5 rounded animate-pulse">
          NOW
        </span>
      )}
      {isNext && !isCurrent && (
        <span className="text-[10px] font-bold text-white bg-ocean-500 px-1.5 py-0.5 rounded">
          NEXT
        </span>
      )}
    </div>
  );
}
