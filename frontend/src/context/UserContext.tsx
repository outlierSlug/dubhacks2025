import { createContext, useContext, useState } from 'react'
import type { ReactNode, Dispatch, SetStateAction } from 'react'

type User = {
  email?: string
  password?: string
  name?: string
  firstName?: string
  lastName?: string
  age?: number
  birthday?: string
  gender?: string
  studentId?: number
  phoneNo?: string
  yearsExperience?: number
  skillLevel?: 'beginner' | 'intermediate' | 'advanced'
  hasPlayedCompetitive?: boolean
  utrRating?: number
}

interface UserContextType {
  user: User | null
  setUser: Dispatch<SetStateAction<User | null>>
  isLoggedIn: boolean
  setIsLoggedIn: Dispatch<SetStateAction<boolean>>
}

// Provide a default (empty) value to satisfy TypeScript
const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  return (
    <UserContext.Provider value={{ user, setUser, isLoggedIn, setIsLoggedIn }}>
      {children}
    </UserContext.Provider>
  )
}
export default function useUser() {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}