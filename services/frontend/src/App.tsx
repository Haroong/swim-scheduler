import { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import DailySchedule from './pages/DailySchedule'
import FacilityPage from './pages/FacilityPage'
import { initGA, trackPageView } from './utils/analytics'

// 페이지뷰 추적
function PageTracker() {
  const location = useLocation();

  useEffect(() => {
    trackPageView(location.pathname);
  }, [location.pathname]);

  return null;
}

function Navigation({ isCompact = false }: { isCompact?: boolean }) {
  const location = useLocation();

  const navItems = [
    { path: '/today', label: '오늘', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
    { path: '/facility', label: '시설별', icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' },
  ];

  return (
    <nav className="flex gap-2">
      {navItems.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          className={`
            rounded-lg font-medium transition-all flex items-center
            ${isCompact ? 'px-2.5 py-1.5 text-xs gap-1' : 'px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm gap-1 sm:gap-1.5'}
            ${location.pathname === item.path || (item.path === '/today' && location.pathname === '/')
              ? 'bg-white text-ocean-600 shadow-lg scale-105'
              : 'text-white/95 hover:bg-white/20 hover:scale-105 active:scale-95 active:bg-white/30'
            }
          `}
        >
          <svg className={`transition-all ${isCompact ? 'w-3.5 h-3.5' : 'w-4 h-4'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
          </svg>
          <span>{item.label}</span>
        </Link>
      ))}
    </nav>
  );
}

function AppLayout({ children }: { children: React.ReactNode }) {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* Header with Ocean Gradient & Wave Pattern */}
      <header className={`
        bg-gradient-to-r from-ocean-600 via-ocean-500 to-wave-500 sticky top-0 z-50 shadow-lg relative overflow-hidden
        transition-all duration-300
      `}>
          {/* Wave Pattern Background */}
          <div className={`absolute inset-0 transition-opacity duration-300 ${isScrolled ? 'opacity-5' : 'opacity-10'}`}>
            <svg className="absolute bottom-0 w-full h-20" viewBox="0 0 1440 100" preserveAspectRatio="none">
              <path fill="white" d="M0,50 C240,80 480,20 720,50 C960,80 1200,20 1440,50 L1440,100 L0,100 Z" />
            </svg>
          </div>

          <div className={`max-w-6xl mx-auto px-4 sm:px-6 relative transition-all duration-300 ${isScrolled ? 'py-2' : 'py-4'}`}>
            <div className={`flex items-center justify-between transition-all duration-300 ${isScrolled ? 'gap-2' : 'flex-col sm:flex-row gap-4'}`}>
              <Link to="/" className="flex items-center gap-3 group">
                <div>
                  <h1 className={`font-bold text-white flex items-center gap-2 transition-all ${isScrolled ? 'text-lg' : 'text-xl sm:text-2xl'}`}>
                    오늘수영
                  </h1>
                  <p className={`
                    text-white/90 font-medium transition-all duration-300 overflow-hidden
                    ${isScrolled ? 'max-h-0 opacity-0' : 'max-h-6 opacity-100 text-xs sm:text-sm'}
                  `}>
                    성남시 자유수영 일정을 한눈에
                  </p>
                </div>
              </Link>
              <Navigation isCompact={isScrolled} />
            </div>
          </div>
        </header>

      {/* Main Content */}
      <main className="flex-1">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-slate-100 border-t border-slate-200 py-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center space-y-1">
            <p className="text-xs text-slate-600 font-medium">
              성남시 자유수영 일정 정보
            </p>
            <p className="text-xs text-slate-400">
              매일 업데이트 · 시설별 상세 일정은 직접 확인해주세요
            </p>
            <p className="text-xs text-slate-400">
              © 2026 오늘수영 ·{' '}
              <a
                href="mailto:absolutecool18@gmail.com"
                className="hover:text-ocean-600 transition-colors"
              >
                문의하기
              </a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function App() {
  useEffect(() => {
    initGA();
  }, []);

  return (
    <Router>
      <PageTracker />
      <AppLayout>
        <Routes>
          <Route path="/" element={<DailySchedule />} />
          <Route path="/today" element={<DailySchedule />} />
          <Route path="/facility" element={<FacilityPage />} />
        </Routes>
      </AppLayout>
    </Router>
  )
}

export default App
