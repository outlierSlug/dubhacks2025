import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom'
import Login from './pages/Login'
import HomePage from './pages/HomePage'
import Schedule from './pages/Schedule'
import Matchmaking from './pages/Matchmaking'
import Profile from './pages/Profile'
import Onboarding from './pages/Onboarding'
import useUser from './context/UserContext'
import './App.css'


function App() {
  const {isLoggedIn} = useUser(); // Local state for now, will hook up to backend 

  return (
    <Router>
      {isLoggedIn && (<nav className="nav">
          <Link to="/home">Home</Link>
          <Link to="/schedule">Schedule</Link>
          <Link to="/matchmaking">Matchmaking</Link>
          <Link to="/profile">Profile</Link>
        </nav>
      )}
      
      <Routes>
        <Route path="/" element={isLoggedIn ? <Navigate to="/home" /> : <Login />} />
        <Route path="/onboarding" element={<Onboarding />} />
        
        <Route path="/home" element={<HomePage />} />
        <Route path="/schedule" element={<Schedule />} />
        <Route path="/matchmaking" element={<Matchmaking />} />
        <Route path="/profile" element={<Profile />} />
        
        <Route path="*" element={<div style={{ padding: '2rem' }}>404 - Not Found</div>} />
      </Routes>
    </Router>
  )
}

export default App
