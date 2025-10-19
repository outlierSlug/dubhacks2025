import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useUser from '../context/UserContext'
import '../styles/Login.css'

export default function Login() {
  const { login } = useUser()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await login(username, password)
      navigate('/home')
    } catch (err: any) {
      setError(err.message || 'Login failed')
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">DubRally 🎾</h1>
        <p className="login-subtitle">Login or create an account to get started</p>

        {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}

        <form onSubmit={handleLogin} className="login-form">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
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