import React, { useState } from 'react'
import '../styles/BookingList.css'

type Booking = {
  id: number
  dateISO: string
  timeSlot: string
  court: number
  status: string
}

interface BookingListProps {
  booking: Booking
  onCancel: (id: number) => void
}

export default function BookingList({ booking, onCancel }: BookingListProps) {
  const [isCanceling, setIsCanceling] = useState(false)

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel this booking?')) return
    
    setIsCanceling(true)
    try {
      await onCancel(booking.id)
    } catch (error) {
      console.error('Cancel failed:', error)
      alert('Failed to cancel booking')
      setIsCanceling(false)
    }
  }

  const dateObj = new Date(booking.dateISO)
  const formattedDate = dateObj.toLocaleDateString('en-US', { 
    weekday: 'short', 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })

  return (
    <div className={`booking-card ${booking.status === 'canceled' ? 'booking-card--canceled' : ''}`}>
      <div className="booking-card__content">
        <div className="booking-card__header">
          <div className="booking-card__date">
            <span className="booking-card__day">{dateObj.getDate()}</span>
            <span className="booking-card__month">
              {dateObj.toLocaleDateString('en-US', { month: 'short' })}
            </span>
          </div>
          <div className="booking-card__details">
            <h4 className="booking-card__title">Court {booking.court}</h4>
            <p className="booking-card__time">{booking.timeSlot}</p>
            <p className="booking-card__full-date">{formattedDate}</p>
          </div>
        </div>
        
        <div className="booking-card__footer">
          <span className={`booking-card__status booking-card__status--${booking.status}`}>
            {booking.status}
          </span>
          {booking.status !== 'canceled' && (
            <button
              onClick={handleCancel}
              disabled={isCanceling}
              className="booking-card__cancel-btn"
            >
              {isCanceling ? 'Canceling...' : 'Cancel'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}