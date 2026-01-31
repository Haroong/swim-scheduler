import { ReactNode } from 'react';

interface ChipProps {
  label: string;
  selected?: boolean;
  onClick?: () => void;
  icon?: ReactNode;
  variant?: 'ocean' | 'wave' | 'slate';
  size?: 'sm' | 'md' | 'lg';
}

export function Chip({
  label,
  selected = false,
  onClick,
  icon,
  variant = 'ocean',
  size = 'md'
}: ChipProps) {
  const variants = {
    ocean: selected
      ? 'bg-ocean-500 text-white shadow-glow'
      : 'bg-ocean-50 text-ocean-700 hover:bg-ocean-100',
    wave: selected
      ? 'bg-wave-500 text-white shadow-wave'
      : 'bg-wave-50 text-wave-700 hover:bg-wave-100',
    slate: selected
      ? 'bg-slate-700 text-white'
      : 'bg-slate-100 text-slate-700 hover:bg-slate-200',
  };

  const sizes = {
    sm: 'px-3 py-1 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-base',
  };

  return (
    <button
      onClick={onClick}
      className={`
        inline-flex items-center gap-2 rounded-full font-medium
        transition-all duration-200
        ${variants[variant]}
        ${sizes[size]}
        ${selected ? 'scale-105' : 'hover:scale-105'}
        ${onClick ? 'cursor-pointer' : 'cursor-default'}
      `}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      {label}
    </button>
  );
}
