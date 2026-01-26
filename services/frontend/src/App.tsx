import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import ScheduleCalendar from './pages/ScheduleCalendar'
import DailySchedule from './pages/DailySchedule'
import CalendarView from './pages/CalendarView'
import './App.css'

function Navigation() {
  const location = useLocation();

  return (
    <nav className="navigation">
      <Link
        to="/"
        className={location.pathname === '/' ? 'nav-link active' : 'nav-link'}
      >
        일별 스케줄
      </Link>
      <Link
        to="/monthly"
        className={location.pathname === '/monthly' ? 'nav-link active' : 'nav-link'}
      >
        월별 스케줄
      </Link>
      <Link
        to="/calendar"
        className={location.pathname === '/calendar' ? 'nav-link active' : 'nav-link'}
      >
        달력 보기
      </Link>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <header className="header">
          <h1>성남시 수영장 자유수영 스케줄</h1>
          <Navigation />
        </header>
        <main className="main">
          <Routes>
            <Route path="/" element={<DailySchedule />} />
            <Route path="/monthly" element={<ScheduleCalendar />} />
            <Route path="/calendar" element={<CalendarView />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
