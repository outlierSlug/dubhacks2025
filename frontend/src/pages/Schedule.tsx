import React, { useState } from 'react'
import '../styles/Schedule.css'
import CalendarPicker from '../components/CalendarPicker'
import TimeSlots from '../components/TimeSlots'
import CourtPicker from '../components/CourtPicker'
import BookingSummary from '../components/BookingSummary'

export default function Schedule() {
  const [date, setDate] = useState(new Date())
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null)
  const [selectedCourt, setSelectedCourt] = useState<number | null>(null)

  const timeSlots = [
    '6:00 AM', '7:00 AM', '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM',
    '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM',
    '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM', '8:00 PM', '9:00 PM'
  ]

  const courts = [1, 2, 3, 4, 5, 6]

  // When the date changes, reset selections
  const handleDateChange = (d: Date) => {
    setDate(d)
    setSelectedSlot(null)
    setSelectedCourt(null)
  }

  // Toggle selection in parent so children stay presentational
  const handleTimeSelect = (slot: string | null) => {
    setSelectedSlot((prev) => (prev === slot ? null : slot))
  }

  const handleCourtSelect = (court: number | null) => {
    setSelectedCourt((prev) => (prev === court ? null : court))
  }

  const canConfirm = Boolean(selectedSlot && selectedCourt)

  const handleConfirm = async () => {
    if (!canConfirm) return
    const booking = {
      dateISO: date.toISOString(),
      dateLabel: date.toLocaleDateString(),
      timeSlot: selectedSlot!,
      court: selectedCourt!,
    }
    // TODO: Replace with real API call to save booking
    // await fetch('/api/bookings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(booking) })
    console.log('Booking confirmed:', booking)
    alert(`Booked court ${booking.court} at ${booking.timeSlot} on ${booking.dateLabel}`)
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