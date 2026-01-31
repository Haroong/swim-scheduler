interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'ocean' | 'wave' | 'cyan' | 'emerald' | 'violet' | 'amber' | 'slate';
  size?: 'sm' | 'md';
}

export function Badge({ children, variant = 'ocean', size = 'md' }: BadgeProps) {
  const variants = {
    primary: 'bg-primary-50 text-primary-700 border border-primary-100',
    ocean: 'bg-ocean-50 text-ocean-700 border border-ocean-100',
    wave: 'bg-wave-50 text-wave-700 border border-wave-100',
    cyan: 'bg-cyan-50 text-cyan-700 border border-cyan-100',
    emerald: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
    violet: 'bg-violet-50 text-violet-700 border border-violet-100',
    amber: 'bg-amber-50 text-amber-700 border border-amber-100',
    slate: 'bg-slate-100 text-slate-600 border border-slate-200',
  };

  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
  };

  return (
    <span className={`inline-flex items-center rounded-lg font-medium ${variants[variant]} ${sizes[size]}`}>
      {children}
    </span>
  );
}
