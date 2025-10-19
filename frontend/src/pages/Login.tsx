import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import  useUser from '../context/UserContext'
import "../styles/Login.css"

export default function Login() {
  const { setUser, setIsLoggedIn } = useUser()
  const [loginId, setLoginId] = useState('') // email or username
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const handleLogin = () => {
    const isEmail = loginId.includes('@')
    setUser({
      email: isEmail ? loginId : undefined,
      username: !isEmail ? loginId : undefined,
      password,
    })
    setIsLoggedIn(true)
    navigate('/home')
  }

  const handleSignup = () => {
    navigate('/onboarding')
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">DubRally 🎾</h1>
        <p className="login-subtitle">Login or create an account to get started</p>

        <form onSubmit={handleLogin} className="login-form">
          <input
            type="text"
            placeholder="Email or username"
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
              onClick={handleSignup}
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