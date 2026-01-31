import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  variant?: 'default' | 'gradient' | 'glass';
  colorBar?: 'ocean' | 'wave' | 'violet' | 'emerald' | 'none';
  className?: string;
  onClick?: () => void;
}

export function Card({
  children,
  variant = 'default',
  colorBar = 'none',
  className = '',
  onClick
}: CardProps) {
  const variants = {
    default: 'bg-white border border-slate-200',
    gradient: 'bg-gradient-to-br from-white to-slate-50 border border-slate-200',
    glass: 'bg-white/80 backdrop-blur-sm border border-white/20',
  };

  const colorBars = {
    ocean: 'bg-gradient-to-b from-ocean-500 to-wave-500',
    wave: 'bg-gradient-to-b from-wave-500 to-emerald-500',
    violet: 'bg-gradient-to-b from-violet-500 to-purple-500',
    emerald: 'bg-gradient-to-b from-emerald-500 to-teal-500',
    none: '',
  };

  return (
    <div
      onClick={onClick}
      className={`
        rounded-2xl shadow-soft overflow-hidden transition-all
        ${variants[variant]}
        ${onClick ? 'cursor-pointer hover:shadow-lg' : ''}
        ${className}
        flex
      `}
    >
      {colorBar !== 'none' && (
        <div className={`w-1.5 flex-shrink-0 ${colorBars[colorBar]}`} />
      )}
      <div className="flex-1">
        {children}
      </div>
    </div>
  );
}
