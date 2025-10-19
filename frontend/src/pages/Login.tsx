import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/Login.css'
import useUser from '../context/UserContext'
import * as authService from '../services/auth'

export default function Login() {
  const navigate = useNavigate()
  const { setUser, setIsLoggedIn } = useUser()

  const [loginId, setLoginId] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    try {
      const player = await authService.login(loginId, password)
      
      setUser({
        id: player.id,
        username: loginId,
        email: player.email,
        firstName: player.fname,
        lastName: player.lname,
        birthday: player.bday,
        phoneNo: player.phone,
        rating: player.rating,
        gender: player.gender === 1 ? 'male' : player.gender === 2 ? 'female' : 'non-binary',
      })
      setIsLoggedIn(true)
      navigate('/home')
    } catch (err: any) {
      console.error('Login error:', err)
      setError(err.message || 'Login failed')
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">DubRally 🎾</h1>
        <p className="login-subtitle">Login or create an account to get started</p>

        {error && <div style={{ color: 'red', marginBottom: '1rem', padding: '0.5rem', background: '#fee', borderRadius: '4px' }}>{error}</div>}

        <form onSubmit={handleLogin} className="login-form">
          <input
            type="text"
            placeholder="Username"
            value={loginId}
            onChange={(e) => setLoginId(e.target.value)}
            className="login-input"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="login-input"
            required
          />

          <div className="login-buttons">
            <button type="submit" className="login-btn login-btn--primary">
              Log in
            </button>
            <button
              type="button"
              onClick={() => navigate('/onboarding')}
              className="login-btn login-btn--secondary"
            >
              Sign Up
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}