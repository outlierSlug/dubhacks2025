type Props = {
  slots: string[]
  selected: string | null
  onSelect: (slot: string | null) => void
}

export default function TimeSlots({ slots, selected, onSelect }: Props) {
  const handleClick = (slot: string) => {
    onSelect(selected === slot ? null : slot) // toggle
  }

  return (
    <div className="panel panel-times">
      <h3 className="panel-title">Available Times</h3>
      <div className="times-grid">
        {slots.map((slot) => {
          const isSelected = selected === slot
          return (
            <button
              key={slot}
              type="button"
              className={`times-item ${isSelected ? 'times-item--selected' : ''}`}
              onClick={() => handleClick(slot)}
              aria-pressed={isSelected}
            >
              {slot}
            </button>
          )
        })}
      </div>
    </div>
  )
}