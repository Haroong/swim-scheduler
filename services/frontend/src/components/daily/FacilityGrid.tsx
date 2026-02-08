import type { DailySchedule } from '../../types/schedule';
import { FacilityCard } from './FacilityCard';

interface FacilityGridProps {
  schedules: DailySchedule[];
  favorites: number[];
  onSelectFacility: (facilityId: number) => void;
  toggleFavorite: (facilityId: number) => void;
}

export function FacilityGrid({
  schedules,
  favorites,
  onSelectFacility,
  toggleFavorite,
}: FacilityGridProps) {
  // 즐겨찾기 시설과 나머지 분리 (외부 정렬 순서 유지)
  const favoriteSchedules = schedules.filter((s) => favorites.includes(s.facility_id));
  const otherSchedules = schedules.filter((s) => !favorites.includes(s.facility_id));

  return (
    <div className="space-y-6">
      {/* 즐겨찾기 온보딩 (즐겨찾기가 없을 때만) */}
      {favoriteSchedules.length === 0 && otherSchedules.length > 0 && (
        <div className="flex items-center gap-3 px-4 py-3 bg-amber-50 border border-amber-200 rounded-xl">
          <div className="flex-shrink-0 w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </div>
          <p className="text-sm text-amber-800">
            자주 가는 수영장의 <span className="font-medium">★</span>를 눌러 즐겨찾기하면 여기에 바로 나타나요
          </p>
        </div>
      )}

      {/* 즐겨찾기 섹션 */}
      {favoriteSchedules.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-4 h-4 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
            <h2 className="text-sm font-semibold text-slate-700">즐겨찾기</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {favoriteSchedules.map((schedule) => (
              <FacilityCard
                key={schedule.facility_id}
                schedule={schedule}
                isFavorite={true}
                onToggleFavorite={() => toggleFavorite(schedule.facility_id)}
                onClick={() => onSelectFacility(schedule.facility_id)}
              />
            ))}
          </div>
        </section>
      )}

      {/* 전체 수영장 섹션 */}
      {otherSchedules.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h2 className="text-sm font-semibold text-slate-700">전체 수영장</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {otherSchedules.map((schedule) => (
              <FacilityCard
                key={schedule.facility_id}
                schedule={schedule}
                isFavorite={false}
                onToggleFavorite={() => toggleFavorite(schedule.facility_id)}
                onClick={() => onSelectFacility(schedule.facility_id)}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
