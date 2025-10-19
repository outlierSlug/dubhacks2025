import Calendar, { type CalendarProps } from 'react-calendar'
import 'react-calendar/dist/Calendar.css'

type Props = {
  value: Date
  onChange: (d: Date) => void
  minDate?: Date
  className?: string
}

export default function CalendarPicker({ value, onChange, minDate, className }: Props) {
  const handleChange: CalendarProps['onChange'] = (v) => {
    if (!v) return
    if (v instanceof Date) onChange(v)
    else if (Array.isArray(v) && v[0] instanceof Date) onChange(v[0])
  }

  return (
    <Calendar
      onChange={handleChange}
      value={value}
      minDate={minDate}
      className={className}
      calendarType="gregory"   // Sunday-first
      locale="en-US"
      selectRange={false}
    />
  )
}