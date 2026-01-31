interface LoadingSpinnerProps {
  message?: string;
}

export function LoadingSpinner({ message = '로딩 중...' }: LoadingSpinnerProps) {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
        <p className="text-slate-500">{message}</p>
      </div>
    </div>
  );
}
