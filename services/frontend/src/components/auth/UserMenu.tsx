import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

export default function UserMenu({ isCompact = false }: { isCompact?: boolean }) {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!user) return null;

  const imgSize = isCompact ? 'w-7 h-7' : 'w-8 h-8';

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 rounded-full transition-all hover:scale-105 active:scale-95"
      >
        {user.profile_image ? (
          <img
            src={user.profile_image}
            alt={user.name}
            className={`${imgSize} rounded-full border-2 border-white/50`}
            referrerPolicy="no-referrer"
          />
        ) : (
          <div className={`${imgSize} rounded-full bg-white/30 flex items-center justify-center text-white font-bold text-sm`}>
            {user.name.charAt(0)}
          </div>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-48 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-50">
          <div className="px-4 py-2 border-b border-slate-100">
            <p className="text-sm font-medium text-slate-900 truncate">{user.name}</p>
            <p className="text-xs text-slate-500 truncate">{user.email}</p>
          </div>
          <button
            onClick={() => {
              logout();
              setIsOpen(false);
            }}
            className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
          >
            로그아웃
          </button>
        </div>
      )}
    </div>
  );
}
