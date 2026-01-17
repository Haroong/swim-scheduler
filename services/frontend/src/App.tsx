import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ScheduleCalendar from './pages/ScheduleCalendar'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <header className="header">
          <h1>성남시 수영장 자유수영 스케줄</h1>
        </header>
        <main className="main">
          <Routes>
            <Route path="/" element={<ScheduleCalendar />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
