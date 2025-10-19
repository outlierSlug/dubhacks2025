import React, { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { TennisRating } from '../utils/TennisRating'
import '../styles/Onboarding.css'
import useUser from '../context/UserContext'

export default function Onboarding() {
  const navigate = useNavigate()
  const { setUser, setIsLoggedIn } = useUser()

  const handleBack = () => navigate('/')
  const [form, setForm] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    studentId: '',
    firstName: '',
    lastName: '',
    birthday: '',
    gender: '',
    phoneNo: '',
    yearsExperience: '',
    skillLevel: '',
    hasPlayedCompetitive: false,
    utrRating: '',
  })


  const [touched, setTouched] = useState<Record<string, boolean>>({})

  const onChange = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const value = e.target.type === 'checkbox' ? (e.target as HTMLInputElement).checked : e.target.value
    setForm({ ...form, [key]: value })
    setTouched({ ...touched, [key]: true })
  }

  const errors = useMemo(() => {
    const errs: Record<string, string> = {}
    if (touched.email && (!form.email || !form.email.includes('@'))) errs.email = 'Enter a valid email'
    if (touched.username && (!form.username || form.username.trim().length < 3)) errs.username = 'Username must be at least 3 characters'
    if (touched.password && form.password.length < 6) errs.password = 'Password must be at least 6 characters'
    if (touched.confirmPassword && form.password !== form.confirmPassword) errs.confirmPassword = 'Passwords do not match'

    const studentIdNum = Number(form.studentId)
    if (touched.studentId && (!form.studentId || isNaN(studentIdNum))) errs.studentId = 'Enter a valid Husky ID number'

    if (touched.firstName && !form.firstName) errs.firstName = 'First name is required'
    if (touched.lastName && !form.lastName) errs.lastName = 'Last name is required'

    if (touched.birthday) {
      const birthdayDate = new Date(form.birthday)
      const age = (Date.now() - birthdayDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25)
      if (!form.birthday || isNaN(birthdayDate.getTime())) errs.birthday = 'Enter a valid date'
      else if (age < 13) errs.birthday = 'Must be at least 13 years old'
    }

    if (touched.gender && !form.gender) errs.gender = 'Select a gender'
    if (touched.phoneNo && !form.phoneNo) errs.phoneNo = 'Phone number is required'

    const yearsNum = Number(form.yearsExperience)
    if (touched.yearsExperience && (isNaN(yearsNum) || yearsNum < 0)) errs.yearsExperience = 'Enter valid years of experience'

    if (touched.skillLevel && !form.skillLevel) errs.skillLevel = 'Select a relative level'

    // UTR validation (optional). If provided, must be number in [1.00, 16.50] with hundredths.
    if (touched.utrRating && form.utrRating !== '') {
      const utr = parseFloat(form.utrRating)
      if (isNaN(utr)) errs.utrRating = 'UTR must be a number'
      else if (utr < 1 || utr > 16.5) errs.utrRating = 'UTR must be between 1.00 and 16.50'
      else {
        // Check if it has more than 2 decimal places
        const scaled = Math.round(utr * 100)
        if (Math.abs(utr * 100 - scaled) > 0.0001) {
          errs.utrRating = 'Use hundredths (e.g., 7.25)'
        }
      }
    }

    return errs
  }, [form, touched])

  const hasErrors = Object.keys(errors).length > 0
  const isComplete =
    form.email &&
    form.username && // now required
    form.password &&
    form.confirmPassword &&
    form.studentId &&
    form.firstName &&
    form.lastName &&
    form.birthday &&
    form.gender &&
    form.phoneNo &&
    form.yearsExperience &&
    form.skillLevel

// helper to render labels with required asterisk
  const Label = ({ htmlFor, children, required = false }: { htmlFor?: string; children: React.ReactNode; required?: boolean }) => (
    <label htmlFor={htmlFor} style={{ fontWeight: 600, display: 'block', marginBottom: 4 }}>
      {children}
      {required && <span style={{ color: 'crimson', marginLeft: 4 }}>*</span>}
    </label>
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (hasErrors || !isComplete) return

    const birthdayDate = new Date(form.birthday)
    const age = Math.floor((Date.now() - birthdayDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25))

    // Map skillLevel string -> numeric 1-3 for the rating algorithm
    const skillMap = { beginner: 1, intermediate: 2, advanced: 3 } as const
    const skillNumeric = skillMap[form.skillLevel as keyof typeof skillMap]

    const yearsPlayed = Number(form.yearsExperience)
    const utr = form.utrRating ? parseFloat(Number(form.utrRating).toFixed(2)) : undefined

    const rating = TennisRating.calculate({
      utr,
      skillLevel: skillNumeric,
      yearsPlayed,
      hasCompExperience: form.hasPlayedCompetitive,
    })

    setUser({
      email: form.email,
      username: form.username,
      password: form.password,
      studentId: Number(form.studentId),
      name: `${form.firstName} ${form.lastName}`,
      firstName: form.firstName,
      lastName: form.lastName,
      birthday: form.birthday,
      age,
      gender: form.gender,
      phoneNo: form.phoneNo,
      yearsExperience: yearsPlayed,
      skillLevel: form.skillLevel as 'beginner' | 'intermediate' | 'advanced',
      hasPlayedCompetitive: form.hasPlayedCompetitive,
      utrRating: utr,
      rating, // save calculated rating
    })
    setIsLoggedIn(true)
    navigate('/home')
  }

  return (
    <div className="ob-container">
      <button type="button" className="ob-back-btn" onClick={handleBack}>
        ← Back to Login
      </button>

      <h1 className="ob-title">Set up your DubRally account</h1>
      <p className="ob-subtitle">Create your login and tell us about your tennis experience.</p>

      <form onSubmit={handleSubmit} className="ob-form">
        <fieldset className="ob-fieldset">
          <legend>Account</legend>

          <div>
            <Label htmlFor="email" required>Email</Label>
            <input
              id="email"
              placeholder="Email (username)"
              type="email"
              value={form.email}
              onChange={onChange('email')}
              className={`ob-input ${errors.email ? 'ob-input-error' : ''}`}
            />
            {errors.email && <div className="ob-error">{errors.email}</div>}
          </div>

          <div className="ob-field">
            <Label htmlFor="username" required>Username</Label>
            <input
              id="username"
              placeholder="Choose a username"
              value={form.username}
              onChange={onChange('username')}
              className={`ob-input ${errors.username ? 'ob-input-error' : ''}`}
            />
            {errors.username && <div className="ob-error">{errors.username}</div>}
          </div>

          <div className="ob-field">
            <Label htmlFor="password" required>Password</Label>
            <input
              id="password"
              placeholder="Password"
              type="password"
              value={form.password}
              onChange={onChange('password')}
              className={`ob-input ${errors.password ? 'ob-input-error' : ''}`}
            />
            {errors.password && <div className="ob-error">{errors.password}</div>}
          </div>

          <div className="ob-field">
            <Label htmlFor="confirmPassword" required>Confirm Password</Label>
            <input
              id="confirmPassword"
              placeholder="Confirm Password"
              type="password"
              value={form.confirmPassword}
              onChange={onChange('confirmPassword')}
              className={`ob-input ${errors.confirmPassword ? 'ob-input-error' : ''}`}
            />
            {errors.confirmPassword && <div className="ob-error">{errors.confirmPassword}</div>}
          </div>
        </fieldset>

        <fieldset className="ob-fieldset">
          <legend>Profile</legend>

          <div>
            <Label htmlFor="studentId" required>Husky ID</Label>
            <input
              id="studentId"
              placeholder="Husky ID"
              type="number"
              value={form.studentId}
              onChange={onChange('studentId')}
              className={`ob-input ${errors.studentId ? 'ob-input-error' : ''}`}
            />
            {errors.studentId && <div className="ob-error">{errors.studentId}</div>}
          </div>

          <div className="ob-row">
            <div className="ob-col">
              <Label htmlFor="firstName" required>First Name</Label>
              <input
                id="firstName"
                placeholder="First Name"
                value={form.firstName}
                onChange={onChange('firstName')}
                className={`ob-input ${errors.firstName ? 'ob-input-error' : ''}`}
              />
              {errors.firstName && <div className="ob-error">{errors.firstName}</div>}
            </div>
            <div className="ob-col">
              <Label htmlFor="lastName" required>Last Name</Label>
              <input
                id="lastName"
                placeholder="Last Name"
                value={form.lastName}
                onChange={onChange('lastName')}
                className={`ob-input ${errors.lastName ? 'ob-input-error' : ''}`}
              />
              {errors.lastName && <div className="ob-error">{errors.lastName}</div>}
            </div>
          </div>

          <div className="ob-row">
            <div className="ob-col">
              <Label htmlFor="birthday" required>Birthday</Label>
              <input
                id="birthday"
                placeholder="Birthday (YYYY-MM-DD)"
                type="date"
                value={form.birthday}
                onChange={onChange('birthday')}
                className={`ob-input ${errors.birthday ? 'ob-input-error' : ''}`}
              />
              {errors.birthday && <div className="ob-error">{errors.birthday}</div>}
            </div>
            <div className="ob-col">
              <Label htmlFor="gender" required>Gender</Label>
              <select
                id="gender"
                value={form.gender}
                onChange={onChange('gender')}
                className={`ob-input ${errors.gender ? 'ob-input-error' : ''}`}
              >
                <option value="">Select gender</option>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="non-binary">Non-binary</option>
                <option value="prefer-not-to-say">Prefer not to say</option>
              </select>
              {errors.gender && <div className="ob-error">{errors.gender}</div>}
            </div>
          </div>

          <div className="ob-field">
            <Label htmlFor="phoneNo" required>Phone Number</Label>
            <input
              id="phoneNo"
              placeholder="Phone Number"
              value={form.phoneNo}
              onChange={onChange('phoneNo')}
              className={`ob-input ${errors.phoneNo ? 'ob-input-error' : ''}`}
            />
            {errors.phoneNo && <div className="ob-error">{errors.phoneNo}</div>}
          </div>
        </fieldset>

        <fieldset className="ob-fieldset">
          <legend>Tennis</legend>
          <div className="ob-row">
            <div className="ob-col">
              <Label htmlFor="yearsExperience" required>Years of Experience</Label>
              <input
                id="yearsExperience"
                placeholder="Years of Experience"
                type="number"
                value={form.yearsExperience}
                onChange={onChange('yearsExperience')}
                className={`ob-input ${errors.yearsExperience ? 'ob-input-error' : ''}`}
              />
              {errors.yearsExperience && <div className="ob-error">{errors.yearsExperience}</div>}
            </div>
            <div className="ob-col">
              <Label htmlFor="skillLevel" required>Relative Level</Label>
              <select
                id="skillLevel"
                value={form.skillLevel}
                onChange={onChange('skillLevel')}
                className={`ob-input ${errors.skillLevel ? 'ob-input-error' : ''}`}
              >
                <option value="">Select level</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
              {errors.skillLevel && <div className="ob-error">{errors.skillLevel}</div>}
            </div>
          </div>

          <div className="ob-field">
            <Label htmlFor="utrRating">UTR (optional)</Label>
            <input
              id="utrRating"
              placeholder="UTR (optional)"
              type="number"
              step="0.01"
              min="1"
              max="16.5"
              value={form.utrRating}
              onChange={onChange('utrRating')}
              className={`ob-input ${errors.utrRating ? 'ob-input-error' : ''}`}
            />
            {errors.utrRating && <div className="ob-error">{errors.utrRating}</div>}
          </div>

          <div className="ob-checkbox-group">
            <input
              type="checkbox"
              id="competitive"
              checked={form.hasPlayedCompetitive}
              onChange={onChange('hasPlayedCompetitive')}
              className="ob-checkbox"
            />
            <label htmlFor="competitive">Have you played competitive tennis on a varsity team/club?</label>
          </div>
        </fieldset>

        <button type="submit" disabled={hasErrors || !isComplete} className="ob-submit-btn">
          Sign Up
        </button>
      </form>
    </div>
  )
}