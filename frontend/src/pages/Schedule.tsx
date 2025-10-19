import React, { useState, useEffect } from 'react'
import '../styles/Schedule.css'
import CalendarPicker from '../components/CalendarPicker'
import TimeSlots from '../components/TimeSlots'
import CourtPicker from '../components/CourtPicker'
import BookingSummary from '../components/BookingSummary'
import useBookings from '../context/BookingsContext'
import useUser from '../context/UserContext'
import * as api from '../services/api'

// Helper function to convert "6:00 AM" to ISO datetime string
function toStartISO(date: Date, timeSlot: string): string {
  const [time, meridiem] = timeSlot.split(' ')
  const [hours, minutes] = time.split(':').map(Number)
  
  // Convert to 24-hour format
  let hour24 = hours
  if (meridiem === 'AM' && hours === 12) {
    hour24 = 0 // 12 AM is midnight (0:00)
  } else if (meridiem === 'PM' && hours !== 12) {
    hour24 = hours + 12 // 1 PM = 13, 2 PM = 14, etc.
  }
  // 12 PM stays as 12
  
  const dt = new Date(date)
  dt.setHours(hour24, minutes || 0, 0, 0)
  return dt.toISOString()
}

// Helper to get hour from time slot string
function getHourFromSlot(timeSlot: string): number {
  const [time, meridiem] = timeSlot.split(' ')
  const [hours] = time.split(':').map(Number)
  
  let hour24 = hours
  if (meridiem === 'AM' && hours === 12) {
    hour24 = 0
  } else if (meridiem === 'PM' && hours !== 12) {
    hour24 = hours + 12
  }
  
  return hour24
}

export default function Schedule() {
  const [date, setDate] = useState(new Date())
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null)
  const [selectedCourt, setSelectedCourt] = useState<number | null>(null)
  const [bookedSlots, setBookedSlots] = useState<Map<string, Set<number>>>(new Map())
  const [loading, setLoading] = useState(false)
  const { createBooking } = useBookings()
  const { user } = useUser()

  const timeSlots = [
    '6:00 AM', '7:00 AM', '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM',
    '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM',
    '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM', '8:00 PM', '9:00 PM'
  ]

  const courts = [1, 2, 3, 4, 5, 6]

  // Fetch all bookings and filter by selected date
  useEffect(() => {
    const fetchBookings = async () => {
      setLoading(true)
      try {
        const allEvents = await api.getAllEvents()
        
        // Filter events for the selected date
        const selectedDateStr = date.toISOString().split('T')[0]
        
        // Build a map: timeSlot -> Set of booked courts
        const slots = new Map<string, Set<number>>()
        
        allEvents.forEach((event: any) => {
          const eventDate = new Date(event.start_time)
          const eventDateStr = eventDate.toISOString().split('T')[0]
          
          // Only process events for the selected date
          if (eventDateStr === selectedDateStr) {
            const hour = eventDate.getHours()
            
            // Find matching time slot
            const matchingSlot = timeSlots.find(slot => getHourFromSlot(slot) === hour)
            
            if (matchingSlot) {
              if (!slots.has(matchingSlot)) {
                slots.set(matchingSlot, new Set())
              }
              slots.get(matchingSlot)!.add(event.court)
            }
          }
        })
        
        setBookedSlots(slots)
      } catch (error) {
        console.error('Failed to fetch bookings:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchBookings()
  }, [date])

  const handleDateChange = (d: Date) => {
    setDate(d)
    setSelectedSlot(null)
    setSelectedCourt(null)
  }

  const handleTimeSelect = (slot: string | null) => {
    setSelectedSlot(slot)
    setSelectedCourt(null) // Reset court when time changes
  }

  const handleCourtSelect = (court: number | null) => {
    setSelectedCourt(court)
  }

  // Get disabled slots (fully booked)
  const getDisabledSlots = (): string[] => {
    const disabled: string[] = []
    bookedSlots.forEach((courts, slot) => {
      if (courts.size === 6) { // All courts booked
        disabled.push(slot)
      }
    })
    return disabled
  }

  // Get disabled courts for the selected time slot
  const getDisabledCourts = (): number[] => {
    if (!selectedSlot || !bookedSlots.has(selectedSlot)) {
      return []
    }
    return Array.from(bookedSlots.get(selectedSlot)!)
  }

  const canConfirm = Boolean(user && selectedSlot && selectedCourt)

  const handleConfirm = async () => {
    if (!canConfirm || !user || !selectedSlot) return
    
    try {
      const startISO = toStartISO(date, selectedSlot)
      console.log('Creating booking:', { date: date.toISOString(), selectedSlot, startISO })
      
      const created = await createBooking({
        startISO,
        timeSlot: selectedSlot,
        court: selectedCourt!,
      })
      console.log('Booking created:', created)
      alert(`Booking confirmed for ${selectedSlot} on court ${selectedCourt}`)
      
      // Update booked slots locally
      const updatedSlots = new Map(bookedSlots)
      if (!updatedSlots.has(selectedSlot)) {
        updatedSlots.set(selectedSlot, new Set())
      }
      updatedSlots.get(selectedSlot)!.add(selectedCourt!)
      setBookedSlots(updatedSlots)
      
      // Reset selections after booking
      setSelectedSlot(null)
      setSelectedCourt(null)
    } catch (error: any) {
      console.error('Booking error:', error)
      alert(error.message || 'Failed to create booking')
    }
  }

  return (
    <div className="schedule-box">
      <h2 className="schedule-title">Tennis Court Schedule</h2>
      {loading && <p className="schedule-loading">Loading bookings...</p>}

      <div className="schedule-layout">
        <div className="calendar-wrapper">
          <CalendarPicker
            value={date}
            onChange={handleDateChange}
            minDate={new Date()}
            className="tennis-calendar"
          />
        </div>

        <TimeSlots
          slots={timeSlots}
          selected={selectedSlot}
          onSelect={handleTimeSelect}
          disabled={getDisabledSlots()}
        />

        <CourtPicker
          courts={courts}
          selected={selectedCourt}
          onSelect={handleCourtSelect}
          disabled={getDisabledCourts()}
        />
      </div>

      <BookingSummary
        date={date}
        timeSlot={selectedSlot}
        court={selectedCourt}
        onConfirm={handleConfirm}
        disabled={!canConfirm}
      />
    </div>
  )
}