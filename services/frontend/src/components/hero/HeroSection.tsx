import { Link } from 'react-router-dom';

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background - Ocean Gradient with Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-ocean-900 to-wave-900">
        {/* Animated Wave Pattern */}
        <div className="absolute inset-0 opacity-20">
          <svg className="absolute bottom-0 w-full h-64 animate-wave" viewBox="0 0 1440 320" preserveAspectRatio="none">
            <path
              fill="currentColor"
              className="text-ocean-500"
              d="M0,160L48,144C96,128,192,96,288,101.3C384,107,480,149,576,154.7C672,160,768,128,864,122.7C960,117,1056,139,1152,138.7C1248,139,1344,117,1392,106.7L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            />
          </svg>
          <svg className="absolute bottom-0 w-full h-64 animate-wave" style={{ animationDelay: '0.5s' }} viewBox="0 0 1440 320" preserveAspectRatio="none">
            <path
              fill="currentColor"
              className="text-wave-600 opacity-50"
              d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,213.3C672,224,768,224,864,213.3C960,203,1056,181,1152,181.3C1248,181,1344,203,1392,213.3L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            />
          </svg>
        </div>

        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-slate-900/60" />
      </div>

      {/* Hero Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 text-center">
        {/* Small Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-md rounded-full border border-white/20 mb-8 animate-fade-in">
          <svg className="w-4 h-4 text-wave-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
          <span className="text-sm font-medium text-white/90">성남시 공공 수영장</span>
        </div>

        {/* Main Headline */}
        <h1 className="font-display text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold text-white mb-6 leading-tight animate-slide-up">
          Dive into
          <br />
          <span className="bg-gradient-to-r from-ocean-400 via-wave-400 to-emerald-400 bg-clip-text text-transparent">
            today's swim
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-lg sm:text-xl md:text-2xl text-white/80 font-medium mb-12 max-w-2xl mx-auto animate-fade-in" style={{ animationDelay: '0.2s' }}>
          성남시 자유수영 정보를 한눈에 확인하고
          <br className="hidden sm:block" />
          나에게 딱 맞는 시간을 찾아보세요
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in" style={{ animationDelay: '0.4s' }}>
          <Link
            to="/today"
            className="group px-8 py-4 bg-white text-ocean-700 rounded-2xl font-bold text-lg shadow-2xl hover:shadow-ocean-500/50 hover:scale-105 transition-all duration-300 flex items-center gap-3"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            오늘의 일정 보기
            <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>

          <Link
            to="/calendar"
            className="px-8 py-4 bg-transparent border-2 border-white/80 text-white rounded-2xl font-semibold text-lg hover:bg-white/10 hover:border-white hover:scale-105 transition-all duration-300 flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            달력으로 보기
          </Link>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <svg className="w-6 h-6 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </div>
    </section>
  );
}
