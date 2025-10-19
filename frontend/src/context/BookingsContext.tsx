import { createContext, useContext, useState, useCallback } from 'react'
import type { ReactNode } from 'react'
import * as api from '../services/api'
import useUser from './UserContext'

type Booking = {
  id: number
  dateISO: string
  timeSlot: string
  court: number
  status: string
}

interface BookingsContextType {
  bookings: Booking[]
  loadMine: () => Promise<void>
  createBooking: (data: { startISO: string; timeSlot: string; court: number }) => Promise<Booking>
}

const BookingsContext = createContext<BookingsContextType | undefined>(undefined)

export function BookingsProvider({ children }: { children: ReactNode }) {
  const [bookings, setBookings] = useState<Booking[]>([])
  const { user } = useUser()

  const loadMine = useCallback(async () => {
    if (!user?.id) return
    const events = await api.getMyEvents(user.id)
    const mapped = events.map((ev: any) => ({
      id: ev.id,
      dateISO: ev.start_time,
      timeSlot: new Date(ev.start_time).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }),
      court: ev.court,
      status: 'confirmed',
    }))
    setBookings(mapped)
  }, [user])

  const createBooking = async (data: { startISO: string; timeSlot: string; court: number }) => {
    if (!user?.id) throw new Error('Must be logged in')
    
    // Create the event
    const event = await api.createEvent({
      id: 0, // Server will assign the real ID
      start_time: data.startISO,
      max_players: 4,
      gender: 3, // co-ed
      court: data.court,
      description: `Court ${data.court} booking`,
    })

    // Add current user to the event
    await api.addPlayerToEvent(event.id, user.id)

    const newBooking = {
      id: event.id,
      dateISO: data.startISO,
      timeSlot: data.timeSlot,
      court: data.court,
      status: 'confirmed',
    }
    setBookings([...bookings, newBooking])
    return newBooking
  }

  return (
    <BookingsContext.Provider value={{ bookings, loadMine, createBooking }}>
      {children}
    </BookingsContext.Provider>
  )
}

export default function useBookings() {
  const context = useContext(BookingsContext)
  if (!context) throw new Error('useBookings must be used within BookingsProvider')
  return context
}