import { useMemo } from 'react';
import type { DailySchedule, Session } from '../../types/schedule';
import { openSourceUrl } from '../../utils/urlUtils';
import { trackFavoriteToggle } from '../../utils/analytics';
import { SlimSessionItem } from './SlimSessionItem';
import { Badge } from '../common';

// 현재 시간 기준 세션 상태 판단
function getSessionStatus(session: Session): 'past' | 'current' | 'upcoming' {
  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  const [startHour, startMin] = session.start_time.split(':').map(Number);
  const [endHour, endMin] = session.end_time.split(':').map(Number);
  const startMinutes = startHour * 60 + startMin;
  const endMinutes = endHour * 60 + endMin;

  if (currentMinutes >= endMinutes) {
    return 'past';
  } else if (currentMinutes >= startMinutes && currentMinutes < endMinutes) {
    return 'current';
  }
  return 'upcoming';
}

// 다음 이용 가능한 세션 인덱스 찾기
function findNextSessionIndex(sessions: Session[]): number {
  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  for (let i = 0; i < sessions.length; i++) {
    const [startHour, startMin] = sessions[i].start_time.split(':').map(Number);
    const startMinutes = startHour * 60 + startMin;
    if (currentMinutes < startMinutes) {
      return i;
    }
  }
  return -1;
}

// 노트 파싱
function parseNotes(notesStr?: string): string[] {
  if (!notesStr) return [];
  try {
    return JSON.parse(notesStr);
  } catch {
    return [];
  }
}

interface ScheduleDetailProps {
  schedule: DailySchedule;
  dateString: string;
  isFavorite: boolean;
  onToggleFavorite: () => void;
  onBack: () => void;
}

export function ScheduleDetail({
  schedule,
  dateString,
  isFavorite,
  onToggleFavorite,
  onBack,
}: ScheduleDetailProps) {
  const nextSessionIdx = useMemo(
    () => (schedule.is_closed ? -1 : findNextSessionIndex(schedule.sessions)),
    [schedule.sessions, schedule.is_closed]
  );

  const notes = parseNotes(schedule.notes);

  return (
    <div className="space-y-4">
      {/* 헤더 */}
      <div className="flex items-center gap-3">
        <button
          onClick={onBack}
          className="min-w-11 min-h-11 -ml-2 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors"
          aria-label="뒤로가기"
        >
          <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <div className="flex-1 min-w-0">
          <h1 className="font-bold text-lg text-slate-800 truncate">
            {schedule.facility_name}
          </h1>
          <p className="text-sm text-slate-500">
            {dateString} · {schedule.day_type}
          </p>
        </div>

        {/* 즐겨찾기 버튼 - 44x44 터치 영역 확보 */}
        <button
          onClick={() => {
            trackFavoriteToggle(schedule.facility_id, schedule.facility_name, isFavorite ? 'remove' : 'add');
            onToggleFavorite();
          }}
          className={`
            min-w-11 min-h-11 flex items-center justify-center rounded-lg transition-colors
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

      {/* 세션 목록 */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        {schedule.is_closed ? (
          <div className="flex items-center justify-center py-8 text-slate-400">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            </svg>
            {schedule.closure_reason || '휴관일입니다'}
          </div>
        ) : (
          <>
            {/* 세션 카운트 */}
            <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
              <span className="text-sm text-slate-600">
                오늘 <strong className="text-slate-800">{schedule.sessions.length}개</strong> 세션
              </span>
              <Badge variant="ocean" size="sm">{schedule.day_type}</Badge>
            </div>

            {/* 세션 리스트 */}
            <div className="p-2 space-y-1">
              {schedule.sessions.map((session, idx) => (
                <SlimSessionItem
                  key={idx}
                  session={session}
                  status={getSessionStatus(session)}
                  isNext={idx === nextSessionIdx}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* 유의사항 */}
      {notes.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-start gap-2">
            <svg className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div className="space-y-1">
              <p className="text-sm font-medium text-amber-800">유의사항</p>
              {notes.map((note, idx) => (
                <p key={idx} className="text-sm text-amber-700">{note}</p>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 원본 공지 링크 */}
      {schedule.source_url && (
        <button
          onClick={() => openSourceUrl(schedule.source_url!)}
          className="w-full flex items-center justify-center gap-2 py-3 text-sm text-slate-500 hover:text-ocean-600 hover:bg-slate-50 rounded-xl border border-slate-200 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          원본 공지 보기
        </button>
      )}
    </div>
  );
}
