interface WavePatternProps {
  variant?: 'ocean' | 'wave' | 'white';
  opacity?: number;
  className?: string;
}

export function WavePattern({
  variant = 'ocean',
  opacity = 0.1,
  className = ''
}: WavePatternProps) {
  const colors = {
    ocean: '#0ea5e9',
    wave: '#14b8a6',
    white: '#ffffff',
  };

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      <svg
        className="absolute bottom-0 left-0 w-full h-auto"
        viewBox="0 0 1440 320"
        preserveAspectRatio="none"
        style={{ opacity }}
      >
        <path
          fill={colors[variant]}
          fillOpacity="1"
          d="M0,96L48,112C96,128,192,160,288,165.3C384,171,480,149,576,154.7C672,160,768,192,864,197.3C960,203,1056,181,1152,154.7C1248,128,1344,96,1392,80L1440,64L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
        />
      </svg>
    </div>
  );
}

export function WavePatternTop({
  variant = 'ocean',
  opacity = 0.1,
  className = ''
}: WavePatternProps) {
  const colors = {
    ocean: '#0ea5e9',
    wave: '#14b8a6',
    white: '#ffffff',
  };

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      <svg
        className="absolute top-0 left-0 w-full h-auto"
        viewBox="0 0 1440 320"
        preserveAspectRatio="none"
        style={{ opacity }}
      >
        <path
          fill={colors[variant]}
          fillOpacity="1"
          d="M0,224L48,213.3C96,203,192,181,288,176C384,171,480,181,576,176C672,171,768,149,864,154.7C960,160,1056,192,1152,197.3C1248,203,1344,181,1392,170.7L1440,160L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z"
        />
      </svg>
    </div>
  );
}
