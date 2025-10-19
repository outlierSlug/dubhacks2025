import React, { useState } from 'react'
import '../styles/Schedule.css'
import CalendarPicker from '../components/CalendarPicker'
import TimeSlots from '../components/TimeSlots'
import CourtPicker from '../components/CourtPicker'
import BookingSummary from '../components/BookingSummary'
import useBookings from '../context/BookingsContext'
import useUser from '../context/UserContext'

// Helper function to convert "6:00 AM" to ISO datetime string
function toStartISO(date: Date, timeSlot: string): string {
  const [time, meridiem] = timeSlot.split(' ')
  const [hours, minutes] = time.split(':').map(Number)
  
  // Convert to 24-hour format
  let hour24 = hours === 12 ? 0 : hours
  if (meridiem === 'PM' && hours !== 12) {
    hour24 += 12
  }
  
  const dt = new Date(date)
  dt.setHours(hour24, minutes || 0, 0, 0)
  return dt.toISOString()
}

export default function Schedule() {
  const [date, setDate] = useState(new Date())
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null)
  const [selectedCourt, setSelectedCourt] = useState<number | null>(null)
  const { createBooking } = useBookings()
  const { user } = useUser()

  const timeSlots = [
    '6:00 AM', '7:00 AM', '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM',
    '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM',
    '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM', '8:00 PM', '9:00 PM'
  ]

  const courts = [1, 2, 3, 4, 5, 6]

  const handleDateChange = (d: Date) => {
    setDate(d)
    setSelectedSlot(null)
    setSelectedCourt(null)
  }

  const handleTimeSelect = (slot: string | null) => {
    setSelectedSlot((prev) => (prev === slot ? null : slot))
  }

  const handleCourtSelect = (court: number | null) => {
    setSelectedCourt((prev) => (prev === court ? null : court))
  }

  const canConfirm = Boolean(user && selectedSlot && selectedCourt)

  const handleConfirm = async () => {
    if (!canConfirm || !user || !selectedSlot) return
    
    try {
      const startISO = toStartISO(date, selectedSlot)
      const created = await createBooking({
        startISO,
        timeSlot: selectedSlot,
        court: selectedCourt!,
      })
      console.log('Booking created:', created)
      alert(`Booking confirmed for ${selectedSlot} on court ${selectedCourt}`)
      
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
        />

        <CourtPicker
          courts={courts}
          selected={selectedCourt}
          onSelect={handleCourtSelect}
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