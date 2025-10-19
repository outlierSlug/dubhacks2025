import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import  useUser from '../context/UserContext'

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
    <div style={{ textAlign: 'center', marginTop: '5rem' }}>
      <h1>DubRally 🎾</h1>
      <p>Login or create an account to get started</p>

      <div style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Email or username"
          value={loginId}
          onChange={(e) => setLoginId(e.target.value)}
          style={{ padding: '0.5rem', width: '220px' }}
        />
      </div>
      <div>
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: '0.5rem', width: '220px' }}
        />
      </div>

      <div style={{ marginTop: '1.5rem' }}>
        <button onClick={handleLogin}>Login</button>
        <button onClick={handleSignup} style={{ marginLeft: '1rem' }}>
          Sign Up
        </button>
      </div>
    </div>
  )
}