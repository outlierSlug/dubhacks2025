type Props = {
  date: Date
  timeSlot: string | null
  court: number | null
  onConfirm: () => void
  disabled?: boolean
}

export default function BookingSummary({ date, timeSlot, court, onConfirm, disabled }: Props) {
  return (
    <div className="selection-summary">
      <p>Selected date: {date.toLocaleDateString()}</p>
      <p>Selected time: {timeSlot ?? '—'}</p>
      <p>Selected court: {court ?? '—'}</p>
      <button
        type="button"
        onClick={onConfirm}
        disabled={disabled}
        className="confirm-btn"
      >
        Confirm Booking
      </button>
    </div>
  )
}