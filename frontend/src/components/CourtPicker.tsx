type Props = {
  courts: number[]
  selected: number | null
  onSelect: (court: number | null) => void
}

export default function CourtPicker({ courts, selected, onSelect }: Props) {
  const handleClick = (court: number) => {
    onSelect(selected === court ? null : court) // toggle
  }

  return (
    <aside className="panel panel-courts">
      <h3 className="panel-title">Courts</h3>
      <div className="courts-grid">
        {courts.map((n) => {
          const isSelected = selected === n
          return (
            <button
              key={n}
              type="button"
              onClick={() => handleClick(n)}
              className={`court ${isSelected ? 'court--selected' : 'court--idle'}`}
              aria-pressed={isSelected}
              aria-label={`Court ${n}`}
            >
              <svg viewBox="0 0 100 60" width="100" height="60" role="img" aria-hidden="true">
                <rect x="2" y="2" width="96" height="56" rx="6" ry="6" className="court-rect" />
                <line x1="50" y1="6" x2="50" y2="54" stroke="#ffffff66" strokeWidth="1" />
                <text x="50" y="36" textAnchor="middle" fontSize="20" fill="#fff" fontFamily="Arial, Helvetica, sans-serif">
                  {n}
                </text>
              </svg>
            </button>
          )
        })}
      </div>
    </aside>
  )
}