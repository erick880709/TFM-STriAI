import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { triagesApi } from '../api/triages'
import { useAuth } from '../hooks/useAuth'
import { NIVELES_TRIAGE, NIVELES_COLORS, ESTADOS_TRIAGE } from '../lib/constants'

const PASOS = ['Registro', 'Signos Vitales', 'Evaluación', 'Clasificación IA', 'Validación']

export default function TriageValidationPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const triageId = localStorage.getItem('active_triage_id') || ''
  const [nivelProf, setNivelProf] = useState('III')
  const [motivoCierre, setMotivoCierre] = useState('')
  const [closed, setClosed] = useState(false)
  const [error, setError] = useState('')

  const closeMutation = useMutation({
    mutationFn: () =>
      triagesApi.close(triageId, nivelProf, user?.username || 'sistema', motivoCierre || undefined),
    onSuccess: () => {
      setClosed(true)
      localStorage.removeItem('active_triage_id')
      localStorage.removeItem('active_patient')
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      setError(e.response?.data?.detail || 'Error al cerrar triaje')
    },
  })

  if (!triageId && !closed) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">No hay un triaje activo para validar.</p>
      </div>
    )
  }

  if (closed) {
    return (
      <div className="max-w-lg mx-auto mt-12 text-center">
        <div className="text-6xl mb-4">🎉</div>
        <h1 className="text-2xl font-bold text-green-700 mb-2">¡Triaje Completado!</h1>
        <p className="text-slate-500 mb-6">El evento de triaje ha sido cerrado exitosamente.</p>
        <button
          onClick={() => navigate('/pacientes')}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700"
        >
          Iniciar Nuevo Triaje
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-slate-800 mb-1">✅ Validación y Cierre</h1>
      <p className="text-sm text-slate-500 mb-6">Confirmación profesional del nivel de triaje y cierre del episodio</p>

      {/* Progreso */}
      <div className="flex items-center gap-1 mb-8 flex-wrap">
        {PASOS.map((p, i) => (
          <div key={p} className="flex items-center gap-1">
            <span className={`text-xs px-2 py-1 rounded-full ${
              i < 4 ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
            }`}>
              {i < 4 ? '✅' : '📍'} {p}
            </span>
            {i < PASOS.length - 1 && <span className="text-slate-300">→</span>}
          </div>
        ))}
      </div>

      <div className="space-y-5">
        {/* Clasificación profesional */}
        <div className="bg-white border border-slate-200 rounded-lg p-6">
          <h2 className="font-semibold text-slate-700 mb-4">🏷️ Clasificación del Profesional</h2>
          <p className="text-sm text-slate-500 mb-3">Selecciona el nivel de triaje según tu criterio clínico:</p>
          <div className="flex gap-3 flex-wrap">
            {NIVELES_TRIAGE.map((nivel) => (
              <button
                key={nivel}
                onClick={() => setNivelProf(nivel)}
                className={`px-6 py-3 rounded-lg text-lg font-bold border-2 transition-all ${
                  nivelProf === nivel
                    ? 'border-slate-800 scale-105'
                    : 'border-transparent opacity-60 hover:opacity-100'
                }`}
                style={{ backgroundColor: NIVELES_COLORS[nivel] + '20', color: NIVELES_COLORS[nivel] }}
              >
                Nivel {nivel}
              </button>
            ))}
          </div>
        </div>

        {/* Cierre */}
        <div className="bg-white border border-slate-200 rounded-lg p-6">
          <h2 className="font-semibold text-slate-700 mb-4">🔒 Cierre del Triaje</h2>
          <textarea
            value={motivoCierre}
            onChange={(e) => setMotivoCierre(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
            placeholder="Motivo de cierre (opcional)..."
          />
        </div>

        {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-600 text-sm">{error}</div>}

        <button
          onClick={() => closeMutation.mutate()}
          disabled={closeMutation.isPending}
          className="w-full bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          {closeMutation.isPending ? 'Cerrando triaje...' : '✅ Cerrar Triaje'}
        </button>
      </div>
    </div>
  )
}
