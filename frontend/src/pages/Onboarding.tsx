import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import useUser from '../context/UserContext'

export default function Onboarding() {
  const navigate = useNavigate()
  const { setUser, setIsLoggedIn } = useUser()

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
      const utr = Number(form.utrRating)
      if (isNaN(utr)) errs.utrRating = 'UTR must be a number'
      else if (utr < 1 || utr > 16.5) errs.utrRating = 'UTR must be between 1.00 and 16.50'
      else if (Math.round(utr * 100) !== utr * 100) errs.utrRating = 'Use hundredths (e.g., 7.25)'
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
      yearsExperience: Number(form.yearsExperience),
      skillLevel: form.skillLevel as 'beginner' | 'intermediate' | 'advanced',
      hasPlayedCompetitive: form.hasPlayedCompetitive,
      utrRating: form.utrRating ? parseFloat(Number(form.utrRating).toFixed(2)) : undefined,
    })
    setIsLoggedIn(true)
    navigate('/home')
  }

  const inputStyle = (fieldName: string) => ({
    width: '100%',
    padding: '0.75rem',
    borderRadius: 8,
    border: `1px solid ${errors[fieldName] ? 'crimson' : '#ccc'}`,
  })

  return (
    <div style={{ padding: '2rem', maxWidth: 600, margin: '0 auto', textAlign: 'left' }}>
      <h1>Set up your DubRally account</h1>
      <p style={{ color: '#666' }}>Create your login and tell us about your tennis experience.</p>

      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1rem', marginTop: '1.5rem' }}>
        <fieldset style={{ border: '1px solid #eee', borderRadius: 8, padding: '1rem' }}>
          <legend>Account</legend>

          <div>
            <Label htmlFor="email" required>Email</Label>
            <input id="email" placeholder="Email (username)" type="email" value={form.email} onChange={onChange('email')}
              style={inputStyle('email')} />
            {errors.email && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.email}</div>}
          </div>

          <div style={{ marginTop: 8 }}>
            <Label htmlFor="username" required>Username</Label>
            <input id="username" placeholder="Choose a username" value={form.username} onChange={onChange('username')}
              style={inputStyle('username')} />
            {errors.username && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.username}</div>}
          </div>

          <div style={{ marginTop: 8 }}>
            <Label htmlFor="password" required>Password</Label>
            <input id="password" placeholder="Password" type="password" value={form.password} onChange={onChange('password')}
              style={inputStyle('password')} />
            {errors.password && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.password}</div>}
          </div>

          <div style={{ marginTop: 8 }}>
            <Label htmlFor="confirmPassword" required>Confirm Password</Label>
            <input id="confirmPassword" placeholder="Confirm Password" type="password" value={form.confirmPassword} onChange={onChange('confirmPassword')}
              style={inputStyle('confirmPassword')} />
            {errors.confirmPassword && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.confirmPassword}</div>}
          </div>
        </fieldset>

        <fieldset style={{ border: '1px solid #eee', borderRadius: 8, padding: '1rem' }}>
          <legend>Profile</legend>

          <div>
            <Label htmlFor="studentId" required>Husky ID</Label>
            <input id="studentId" placeholder="Husky ID" type="number" value={form.studentId} onChange={onChange('studentId')}
              style={inputStyle('studentId')} />
            {errors.studentId && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.studentId}</div>}
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: 8 }}>
            <div style={{ flex: 1 }}>
              <Label htmlFor="firstName" required>First Name</Label>
              <input id="firstName" placeholder="First Name" value={form.firstName} onChange={onChange('firstName')}
                style={inputStyle('firstName')} />
              {errors.firstName && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.firstName}</div>}
            </div>
            <div style={{ flex: 1 }}>
              <Label htmlFor="lastName" required>Last Name</Label>
              <input id="lastName" placeholder="Last Name" value={form.lastName} onChange={onChange('lastName')}
                style={inputStyle('lastName')} />
              {errors.lastName && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.lastName}</div>}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: 8 }}>
            <div style={{ flex: 1 }}>
              <Label htmlFor="birthday" required>Birthday</Label>
              <input id="birthday" placeholder="Birthday (YYYY-MM-DD)" type="date" value={form.birthday} onChange={onChange('birthday')}
                style={inputStyle('birthday')} />
              {errors.birthday && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.birthday}</div>}
            </div>
            <div style={{ flex: 1 }}>
              <Label htmlFor="gender" required>Gender</Label>
              <select id="gender" value={form.gender} onChange={onChange('gender')}
                style={inputStyle('gender')}>
                <option value="">Select gender</option>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="non-binary">Non-binary</option>
                <option value="prefer-not-to-say">Prefer not to say</option>
              </select>
              {errors.gender && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.gender}</div>}
            </div>
          </div>

          <div style={{ marginTop: 8 }}>
            <Label htmlFor="phoneNo" required>Phone Number</Label>
            <input id="phoneNo" placeholder="Phone Number" value={form.phoneNo} onChange={onChange('phoneNo')}
              style={inputStyle('phoneNo')} />
            {errors.phoneNo && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.phoneNo}</div>}
          </div>
        </fieldset>

        <fieldset style={{ border: '1px solid #eee', borderRadius: 8, padding: '1rem' }}>
          <legend>Tennis</legend>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <div style={{ flex: 1 }}>
              <Label htmlFor="yearsExperience" required>Years of Experience</Label>
              <input id="yearsExperience" placeholder="Years of Experience" type="number" value={form.yearsExperience} onChange={onChange('yearsExperience')}
                style={inputStyle('yearsExperience')} />
              {errors.yearsExperience && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.yearsExperience}</div>}
            </div>
            <div style={{ flex: 1 }}>
              <Label htmlFor="skillLevel" required>Relative Level</Label>
              <select id="skillLevel" value={form.skillLevel} onChange={onChange('skillLevel')}
                style={inputStyle('skillLevel')}>
                <option value="">Select level</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
              {errors.skillLevel && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.skillLevel}</div>}
            </div>
          </div>

          <div style={{ marginTop: 8 }}>
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
              style={inputStyle('utrRating')}
            />
            {errors.utrRating && <div style={{ color: 'crimson', fontSize: '0.85rem', marginTop: 4 }}>{errors.utrRating}</div>}
          </div>

          <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <input
              type="checkbox"
              id="competitive"
              checked={form.hasPlayedCompetitive}
              onChange={onChange('hasPlayedCompetitive')}
              style={{ width: 'auto' }}
            />
            <label htmlFor="competitive">Have you played competitive tennis on a varsity team/club?</label>
          </div>
        </fieldset>

        <button
          type="submit"
          disabled={hasErrors || !isComplete}
          style={{
            padding: '0.9rem',
            borderRadius: 8,
            background: (hasErrors || !isComplete) ? '#aaa' : '#4b2e83',
            color: 'white',
            border: 'none',
            cursor: (hasErrors || !isComplete) ? 'not-allowed' : 'pointer',
            fontWeight: 600
          }}
        >
          Sign Up
        </button>
      </form>
    </div>
  )
}