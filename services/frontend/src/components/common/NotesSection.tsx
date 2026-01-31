interface NotesSectionProps {
  notes: string[];
}

export function NotesSection({ notes }: NotesSectionProps) {
  if (notes.length === 0) return null;

  return (
    <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
      <h4 className="text-sm font-medium text-amber-800 mb-2 flex items-center gap-2">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        유의사항
      </h4>
      <ul className="space-y-1">
        {notes.map((note, idx) => (
          <li key={idx} className="text-sm text-amber-700 flex items-start gap-2">
            <span className="text-amber-400 mt-1">•</span>
            {note}
          </li>
        ))}
      </ul>
    </div>
  );
}
