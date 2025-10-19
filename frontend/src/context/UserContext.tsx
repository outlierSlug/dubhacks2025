import { createContext, useContext, useState } from 'react'
import type { ReactNode, Dispatch, SetStateAction } from 'react'
import * as api from '../services/api'
import { useNavigate } from 'react-router-dom'

type User = {
  id?: number
  email?: string
  username?: string
  password?: string
  firstName?: string
  lastName?: string
  birthday?: string
  gender?: string
  phoneNo?: string
  yearsExperience?: number
  skillLevel?: 'beginner' | 'intermediate' | 'advanced'
  hasPlayedCompetitive?: boolean
  utrRating?: number
  rating?: number
}

interface UserContextType {
  user: User | null
  setUser: Dispatch<SetStateAction<User | null>>
  isLoggedIn: boolean
  setIsLoggedIn: Dispatch<SetStateAction<boolean>>
  login: (username: string, password: string) => Promise<void>
  signup: (userData: any) => Promise<void>
  logout: () => void
}

const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  const login = async (username: string, password: string) => {
    const playerData = await api.loginUser(username, password)
    setUser({
      id: playerData.id,
      firstName: playerData.fname,
      lastName: playerData.lname,
      email: playerData.email,
      phoneNo: playerData.phone,
      birthday: playerData.bday,
      rating: playerData.rating,
      gender: playerData.gender === 1 ? 'male' : playerData.gender === 2 ? 'female' : 'other',
    })
    setIsLoggedIn(true)
  }

  const signup = async (userData: any) => {
    // Map frontend data to backend format
    const genderMap: Record<string, number> = {
      male: 1,
      female: 2,
      'non-binary': 3,
      'prefer-not-to-say': 3,
    }
    
    const payload = {
      username: userData.username,
      password: userData.password,
      id: userData.studentId || Date.now(), // Use studentId or generate
      fname: userData.firstName,
      lname: userData.lastName,
      rating: userData.rating || 50,
      email: userData.email,
      phone: userData.phoneNo,
      bday: userData.birthday,
      gender: genderMap[userData.gender] || 3,
    }
    
    const playerData = await api.signupUser(payload)
    setUser({
      id: playerData.id,
      firstName: playerData.fname,
      lastName: playerData.lname,
      email: playerData.email,
      phoneNo: playerData.phone,
      birthday: playerData.bday,
      rating: playerData.rating,
      gender: userData.gender,
      ...userData,
    })
    setIsLoggedIn(true)
  }

  const logout = () => {
        setUser(null)
        setIsLoggedIn(false)
        // Clear any stored session data if needed
        localStorage.removeItem('user')
    }

  return (
    <UserContext.Provider value={{ user, setUser, isLoggedIn, setIsLoggedIn, login, signup, logout }}>
      {children}
    </UserContext.Provider>
  )
}

export default function useUser() {
  const context = useContext(UserContext)
  if (!context) throw new Error('useUser must be used within a UserProvider')
  return context
}