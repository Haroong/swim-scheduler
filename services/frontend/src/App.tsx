import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Landing from './pages/Landing'
import MonthlySchedule from './pages/MonthlySchedule'
import DailySchedule from './pages/DailySchedule'
import CalendarView from './pages/CalendarView'

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
            min-h-11 px-4 sm:px-5 py-2 sm:py-2.5 rounded-xl text-sm sm:text-base font-semibold transition-all
            flex items-center gap-1.5 sm:gap-2
            ${location.pathname === item.path
              ? 'bg-white text-ocean-600 shadow-lg scale-105'
              : 'text-white/95 hover:bg-white/20 hover:scale-105 active:scale-95 active:bg-white/30'
            }
          `}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
          </svg>
          <span>{item.label}</span>
        </Link>
      ))}
    </nav>
  );
}

function AppLayout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isLandingPage = location.pathname === '/';

  // Landing 페이지에서는 헤더/푸터 숨김
  if (isLandingPage) {
    return <>{children}</>;
  }

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
                    성남시 자유수영 일정 정보
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
      <footer className="bg-white border-t border-slate-200 py-8 pb-[calc(2rem+env(safe-area-inset-bottom))]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center">
            <p className="text-sm text-slate-600 font-medium">
              성남시 공공 수영장 자유수영 일정 정보
            </p>
            <p className="mt-2 text-xs text-slate-500">
              실제 운영 시간은 각 시설에 문의해주세요
            </p>
            <div className="mt-4 flex items-center justify-center gap-1.5 text-xs text-slate-500">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>데이터는 공공기관 공지사항을 기반으로 수집됩니다</span>
              <span className="mx-1.5 text-slate-300">·</span>
              <span>Made by 조혜륜</span>
              <a href="https://github.com/haroong" target="_blank" rel="noopener noreferrer" className="hover:text-slate-600 transition-colors">
                <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/today" element={<DailySchedule />} />
          <Route path="/monthly" element={<MonthlySchedule />} />
          <Route path="/calendar" element={<CalendarView />} />
        </Routes>
      </AppLayout>
    </Router>
  )
}

export default App
