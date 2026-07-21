interface StepIndicatorProps {
  step: number
  total?: number
  label?: string
}

export default function StepIndicator({ step, total = 5, label }: StepIndicatorProps) {
  return (
    <div className="flex items-center gap-2 mb-4">
      <span className="text-xs font-medium bg-[#0891B2] text-white px-2.5 py-1 rounded-full" style={{ fontFamily: 'Lexend, system-ui, sans-serif' }}>
        Paso {step} de {total}
      </span>
      {label && <span className="text-xs text-[#64748B]">· {label}</span>}
      <div className="flex-1 h-1 bg-[#A5F3FC] rounded-full ml-2 overflow-hidden">
        <div className="h-full bg-[#0891B2] rounded-full transition-all" style={{ width: `${(step / total) * 100}%` }} />
      </div>
    </div>
  )
}
