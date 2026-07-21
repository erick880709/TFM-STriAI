import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { triagesApi } from '../api/triages'
import { useAuth } from '../hooks/useAuth'
import PatientSearch from '../components/clinical/PatientSearch'
import type { Patient } from '../types/patient'

const RANGOS: Record<string, { min: number; max: number; unit: string; normal: [number, number]; label: string; help: string }> = {
  frecuencia_cardiaca: { min: 30, max: 250, unit: 'lpm', normal: [60, 100], label: 'Frecuencia Cardíaca', help: 'Latidos del corazón por minuto. Normal: 60-100 lpm.' },
  frecuencia_respiratoria: { min: 5, max: 60, unit: 'rpm', normal: [12, 20], label: 'Frecuencia Respiratoria', help: 'Respiraciones por minuto. Normal: 12-20 rpm.' },
  presion_sistolica: { min: 40, max: 280, unit: 'mmHg', normal: [90, 140], label: 'Presión Sistólica', help: 'Presión arterial al contraer el corazón. Normal: 90-140 mmHg.' },
  presion_diastolica: { min: 20, max: 180, unit: 'mmHg', normal: [60, 90], label: 'Presión Diastólica', help: 'Presión arterial al relajar el corazón. Normal: 60-90 mmHg.' },
  temperatura: { min: 30, max: 45, unit: '°C', normal: [36, 37.5], label: 'Temperatura', help: 'Temperatura corporal. Normal: 36-37.5 °C.' },
  saturacion_oxigeno: { min: 30, max: 100, unit: '%', normal: [95, 100], label: 'Saturación de Oxígeno', help: 'Porcentaje de oxígeno en sangre. Normal: ≥ 95%.' },
}

function alertClass(value: number, normal: [number, number]) {
  if (value >= normal[0] && value <= normal[1]) return 'normal'
  if (value >= normal[0] * 0.9 && value <= normal[1] * 1.1) return 'warning'
  return 'danger'
}

function inputBorderClass(status: string) {
  switch (status) {
    case 'normal': return 'border-green-400 ring-green-300'
    case 'warning': return 'border-amber-400 ring-amber-300'
    case 'danger': return 'border-red-400 ring-red-300'
    default: return 'border-slate-300 ring-blue-300'
  }
}

function statusLabelClass(status: string) {
  switch (status) {
    case 'normal': return 'text-green-600'
    case 'warning': return 'text-amber-600'
    case 'danger': return 'text-red-600'
    default: return ''
  }
}

export default function VitalSignsPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [patient, setPatient] = useState<Patient | null>(() => {
    const stored = localStorage.getItem('active_patient')
    return stored ? JSON.parse(stored) : null
  })
  const [signs, setSigns] = useState({
    frecuencia_cardiaca: '', frecuencia_respiratoria: '', presion_sistolica: '',
    presion_diastolica: '', temperatura: '36.5', saturacion_oxigeno: '98',
  })
  const [error, setError] = useState('')

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!patient) throw new Error('No hay paciente activo')
      // Crear triaje primero
      const triageRes = await triagesApi.create(Number(patient.id_paciente), user?.username || 'sistema')
      const triageId = (triageRes.data.data as { id_triaje: string }).id_triaje
      // Guardar signos vitales
      const nums = Object.fromEntries(
        Object.entries(signs).map(([k, v]) => [k, parseFloat(v) || 0])
      )
      await triagesApi.saveVitalSigns(triageId, nums as unknown as import('../types/triage').VitalSigns)
      localStorage.setItem('active_triage_id', triageId)
      return triageId
    },
    onSuccess: () => navigate('/evaluacion-clinica'),
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      setError(e.response?.data?.detail || 'Error al guardar signos vitales')
    },
  })

  const handleChange = (field: string, value: string) => {
    setSigns((prev) => ({ ...prev, [field]: value }))
  }

  if (!patient) {
    return (
      <div className="max-w-lg mx-auto mt-12 text-center">
        <p className="text-[#475569] mb-4">No hay un paciente activo. Busca uno para continuar.</p>
        <PatientSearch onSelect={(p) => { localStorage.setItem('active_patient', JSON.stringify(p)); setPatient(p) }} />
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-[#164E63] mb-1" style={{fontFamily:'Lexend,system-ui,sans-serif'}}>💓 Signos Vitales</h1>
      <p className="text-sm text-[#475569] mb-2">
        Paciente: {patient.nombre} {patient.apellido} · {patient.numero_documento}
      </p>

      <PatientSearch onSelect={(p) => { localStorage.setItem('active_patient', JSON.stringify(p)); setPatient(p) }} />

      <div className="mt-6 bg-white border border-[#CFFAFE] rounded-lg p-5 max-w-xl">
        <div className="space-y-4">
          {Object.entries(RANGOS).map(([key, cfg]) => {
            const val = parseFloat(signs[key as keyof typeof signs]) || 0
            const status = val ? alertClass(val, cfg.normal) : ''
            return (
              <div key={key}>
                <div className="flex items-center gap-2 mb-1">
                  <label className="text-sm font-medium text-[#164E63]">
                    {cfg.label}
                  </label>
                  <span className="text-xs text-[#475569]" title={cfg.help}>ℹ️</span>
                </div>
                <div className="flex items-center gap-3">
                  <input
                    type="number" step="0.1" min={cfg.min} max={cfg.max}
                    value={signs[key as keyof typeof signs]}
                    onChange={(e) => handleChange(key, e.target.value)}
                    className={`flex-1 px-3 py-2 border rounded-lg text-sm outline-none focus:ring-2 ${inputBorderClass(status)}`}
                    style={{minHeight:'44px'}}
                    aria-valuemin={cfg.min} aria-valuemax={cfg.max}
                    aria-label={cfg.label}
                    required
                  />
                  {val > 0 && (
                    <span className={`text-xs font-medium w-20 ${statusLabelClass(status)}`}>
                      {val < cfg.normal[0] ? '↓ Bajo' : val > cfg.normal[1] ? '↑ Alto' : '✓ Normal'}
                    </span>
                  )}
                </div>
                <p className="text-xs text-[#475569] mt-1 ml-1">Normal: {cfg.normal[0]}-{cfg.normal[1]} {cfg.unit}</p>
              </div>
            )
          })}
        </div>

        {error && <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-600 text-sm">{error}</div>}

        <button
          onClick={() => saveMutation.mutate()}
          disabled={saveMutation.isPending}
          className="w-full mt-6 bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {saveMutation.isPending ? 'Guardando...' : 'Guardar Signos Vitales y Continuar'}
        </button>
      </div>
    </div>
  )
}
