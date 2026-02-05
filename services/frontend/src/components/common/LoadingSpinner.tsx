interface LoadingSpinnerProps {
  message?: string;
  variant?: 'spinner' | 'skeleton';
}

export function LoadingSpinner({ message = '로딩 중...', variant = 'spinner' }: LoadingSpinnerProps) {
  if (variant === 'skeleton') {
    return (
      <div className="space-y-4">
        {/* Skeleton Card */}
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-2xl shadow-soft border border-slate-200 overflow-hidden animate-pulse">
            <div className="p-6 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-slate-200" />
                <div className="space-y-2 flex-1">
                  <div className="h-6 bg-slate-200 rounded w-1/3" />
                  <div className="flex gap-2">
                    <div className="h-5 bg-slate-200 rounded w-16" />
                    <div className="h-5 bg-slate-200 rounded w-12" />
                  </div>
                </div>
              </div>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {[1, 2, 3].map((j) => (
                  <div key={j} className="bg-slate-100 rounded-xl p-4 space-y-3">
                    <div className="h-4 bg-slate-200 rounded w-2/3" />
                    <div className="h-6 bg-slate-200 rounded w-1/2" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center py-20">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
        <p className="text-slate-500">{message}</p>
      </div>
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-white rounded-2xl shadow-soft border border-slate-200 overflow-hidden animate-pulse">
      <div className="p-6 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-slate-200" />
          <div className="space-y-2 flex-1">
            <div className="h-6 bg-slate-200 rounded w-1/3" />
            <div className="flex gap-2">
              <div className="h-5 bg-slate-200 rounded w-16" />
              <div className="h-5 bg-slate-200 rounded w-12" />
            </div>
          </div>
        </div>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[1, 2, 3].map((j) => (
            <div key={j} className="bg-slate-100 rounded-xl p-4 space-y-3">
              <div className="h-4 bg-slate-200 rounded w-2/3" />
              <div className="h-6 bg-slate-200 rounded w-1/2" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function CalendarSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="grid grid-cols-7 gap-1">
        {Array.from({ length: 35 }).map((_, i) => (
          <div key={i} className="aspect-square bg-slate-100 rounded-xl" />
        ))}
      </div>
    </div>
  );
}
