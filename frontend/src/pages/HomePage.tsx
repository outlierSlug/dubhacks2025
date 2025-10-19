import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import useUser from '../context/UserContext'
import useBookings from '../context/BookingsContext'
import '../styles/HomePage.css'

export default function HomePage() {
  const { user, logout } = useUser()
  const { bookings, loadMine } = useBookings()
  const navigate = useNavigate()
  const [isLoggingOut, setIsLoggingOut] = useState(false)


  useEffect(() => {
    if (user) loadMine()
  }, [user, loadMine])

  const handleLogout = async () => {
    setIsLoggingOut(true)
    
    // Add a small delay for graceful animation
    await new Promise(resolve => setTimeout(resolve, 600))
    
    logout()
    navigate('/')
  }

  return (
    <div className={`home ${isLoggingOut ? 'home--logging-out' : ''}`}>
      <header className="home-header">
        <h2 className="home-title">Welcome, {user?.firstName ?? user?.username ?? 'Player'}</h2>
        <div className="home-actions">
          <Link to="/schedule" className="btn btn-primary">New booking</Link>
          <button 
            onClick={handleLogout} 
            className="btn btn-logout"
            disabled={isLoggingOut}
          >
            {isLoggingOut ? 'Logging out...' : 'Log out'}
          </button>
        </div>
      </header>

      <section className="home-section">
        <h3 className="home-section-title">My bookings</h3>

        {bookings.length === 0 ? (
          <div className="home-card home-empty">
            <p>No bookings yet.</p>
            <Link to="/schedule" className="btn btn-primary">Create your first booking</Link>
          </div>
        ) : (
          <div className="home-card">
            <ul className="booking-list">
              {bookings.map(b => (
                <li key={b.id} className="booking-item">
                  <div className="booking-main">
                    <div className="booking-date">
                      {new Date(b.dateISO).toLocaleDateString()}
                    </div>
                    <div className="booking-meta">
                      {b.timeSlot} • Court {b.court}
                    </div>
                  </div>
                  <span className={`booking-status booking-status--${b.status}`}>
                    {b.status}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
    </div>
  )
}