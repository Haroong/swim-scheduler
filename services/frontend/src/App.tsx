import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import ScheduleCalendar from './pages/ScheduleCalendar'
import DailySchedule from './pages/DailySchedule'
import CalendarView from './pages/CalendarView'

function Navigation() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: '오늘의 자유수영' },
    { path: '/monthly', label: '월별 스케줄' },
    { path: '/calendar', label: '달력' },
  ];

  return (
    <nav className="flex gap-1 sm:gap-2">
      {navItems.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          className={`
            px-3 sm:px-4 py-2 rounded-lg text-sm sm:text-base font-medium transition-all
            ${location.pathname === item.path
              ? 'bg-white text-primary-600 shadow-sm'
              : 'text-white/90 hover:bg-white/20'
            }
          `}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-slate-50">
        {/* Header with Gradient */}
        <header className="bg-gradient-to-r from-primary-600 via-primary-500 to-cyan-500 sticky top-0 z-50 shadow-lg">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <Link to="/" className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-lg sm:text-xl font-bold text-white">
                    성남시 자유수영
                  </h1>
                  <p className="text-xs sm:text-sm text-white/80 hidden sm:block">
                    수영장 운영 시간을 한눈에
                  </p>
                </div>
              </Link>
              <Navigation />
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6">
            <Routes>
              <Route path="/" element={<DailySchedule />} />
              <Route path="/monthly" element={<ScheduleCalendar />} />
              <Route path="/calendar" element={<CalendarView />} />
            </Routes>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-slate-200 py-6">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center text-sm text-slate-500">
            <p>성남시 공공 수영장 자유수영 일정 정보</p>
            <p className="mt-1 text-xs text-slate-400">
              * 실제 운영 시간은 각 시설에 문의해주세요
            </p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
