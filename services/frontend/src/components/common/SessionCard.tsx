import type { Session } from '../../types/schedule';

interface SessionCardProps {
  session: Session;
  colorScheme?: 'ocean' | 'wave' | 'emerald' | 'violet';
}

export function SessionCard({ session, colorScheme = 'ocean' }: SessionCardProps) {
  const textColors = {
    ocean: 'text-ocean-700',
    wave: 'text-wave-700',
    emerald: 'text-emerald-700',
    violet: 'text-violet-700',
  };

  const bgColors = {
    ocean: 'from-ocean-50/50 to-wave-50/50',
    wave: 'from-wave-50/50 to-emerald-50/50',
    emerald: 'from-emerald-50/50 to-teal-50/50',
    violet: 'from-violet-50/50 to-purple-50/50',
  };

  return (
    <div className={`bg-gradient-to-br ${bgColors[colorScheme]} rounded-xl p-4 hover:shadow-md active:scale-[0.98] active:shadow-none transition-all border border-slate-200/50 relative overflow-hidden group`}>
      {/* Hover effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/0 to-white/50 opacity-0 group-hover:opacity-100 transition-opacity" />

      <div className="relative">
        <div className="font-semibold text-slate-800 mb-2 text-sm">
          {session.session_name}
        </div>
        <div className={`${textColors[colorScheme]} font-bold text-lg mb-3`}>
          {session.start_time.substring(0, 5)} - {session.end_time.substring(0, 5)}
        </div>
        {(session.capacity || session.lanes) && (
          <div className="flex flex-wrap gap-2">
            {session.capacity && (
              <span className="inline-flex items-center gap-1 text-xs text-slate-700 bg-white/80 px-2.5 py-1 rounded-full border border-slate-200">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                {session.capacity}명
              </span>
            )}
            {session.lanes && (
              <span className="inline-flex items-center gap-1 text-xs text-slate-700 bg-white/80 px-2.5 py-1 rounded-full border border-slate-200">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
                {session.lanes}레인
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
