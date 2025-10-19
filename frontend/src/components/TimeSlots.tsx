type Props = {
  slots: string[]
  selected: string | null
  onSelect: (slot: string | null) => void
  disabled?: string[]
}

export default function TimeSlots({ slots, selected, onSelect, disabled = [] }: Props) {
  const handleClick = (slot: string) => {
    onSelect(selected === slot ? null : slot) // toggle
  }

  return (
    <div className="panel panel-times">
      <h3 className="panel-title">Select Time</h3>
      <div className="times-grid">
        {slots.map((slot) => {
          const isDisabled = disabled.includes(slot)
          const isSelected = selected === slot
          return (
            <button
              key={slot}
              type="button"
              className={`times-item ${isSelected ? 'times-item--selected' : ''} ${isDisabled ? 'times-item--disabled' : ''}`}
              onClick={() => !isDisabled && handleClick(slot)}
              aria-pressed={isSelected}
              disabled={isDisabled}
            >
              {slot}
            </button>
          )
        })}
      </div>
    </div>
  )
}