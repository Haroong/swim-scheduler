import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import MonthlySchedule from './pages/MonthlySchedule'
import DailySchedule from './pages/DailySchedule'
import CalendarView from './pages/CalendarView'
import { initGA, trackPageView } from './utils/analytics'

// 페이지뷰 추적
function PageTracker() {
  const location = useLocation();

  useEffect(() => {
    trackPageView(location.pathname);
  }, [location.pathname]);

  return null;
}

function Navigation() {
  const location = useLocation();

  const navItems = [
    { path: '/today', label: '오늘', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
    { path: '/calendar', label: '달력', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
    { path: '/monthly', label: '월별', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' },
  ];

  return (
    <nav className="flex gap-2">
      {navItems.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          className={`
            px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-all
            flex items-center gap-1 sm:gap-1.5
            ${location.pathname === item.path || (item.path === '/today' && location.pathname === '/')
              ? 'bg-white text-ocean-600 shadow-lg scale-105'
              : 'text-white/95 hover:bg-white/20 hover:scale-105 active:scale-95 active:bg-white/30'
            }
          `}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
          </svg>
          <span>{item.label}</span>
        </Link>
      ))}
    </nav>
  );
}

function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* Header with Ocean Gradient & Wave Pattern */}
      <header className="bg-gradient-to-r from-ocean-600 via-ocean-500 to-wave-500 sticky top-0 z-50 shadow-lg relative overflow-hidden">
          {/* Wave Pattern Background */}
          <div className="absolute inset-0 opacity-10">
            <svg className="absolute bottom-0 w-full h-20" viewBox="0 0 1440 100" preserveAspectRatio="none">
              <path fill="white" d="M0,50 C240,80 480,20 720,50 C960,80 1200,20 1440,50 L1440,100 L0,100 Z" />
            </svg>
          </div>

          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 relative">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <Link to="/" className="flex items-center gap-3 group">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center group-hover:bg-white/30 transition-all group-hover:scale-105 shadow-lg">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
                    오늘수영
                  </h1>
                  <p className="text-xs sm:text-sm text-white/90 font-medium">
                    성남시 자유수영 일정을 한눈에
                  </p>
                </div>
              </Link>
              <Navigation />
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
          <Route path="/monthly" element={<MonthlySchedule />} />
          <Route path="/calendar" element={<CalendarView />} />
        </Routes>
      </AppLayout>
    </Router>
  )
}

export default App
