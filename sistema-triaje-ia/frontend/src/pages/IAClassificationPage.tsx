import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { inferenceApi, type PredictResult } from '../api/inference'
import { NIVELES_TRIAGE, NIVELES_COLORS } from '../lib/constants'
import { LoadingSpinner } from '../components/shared'

export default function IAClassificationPage() {
  const navigate = useNavigate()
  const triageId = localStorage.getItem('active_triage_id') || ''
  const [result, setResult] = useState<PredictResult | null>(null)
  const [shapResult, setShapResult] = useState<unknown>(null)
  const [error, setError] = useState('')
  const [showShap, setShowShap] = useState(false)

  const predictMutation = useMutation({
    mutationFn: () => {
      const patient = JSON.parse(localStorage.getItem('active_patient') || '{}')
      return inferenceApi.predict({
        frecuencia_cardiaca: 80, frecuencia_respiratoria: 16,
        presion_sistolica: 120, presion_diastolica: 80,
        temperatura: 36.5, saturacion_oxigeno: 98,
        edad: patient.edad || 35, sexo: patient.sexo || 'M',
        motivo_texto: 'Evaluación clínica de urgencias',
      })
    },
    onSuccess: (res) => setResult(res.data),
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      setError(e.response?.data?.detail || 'Error en la clasificación IA')
    },
  })

  const explainMutation = useMutation({
    mutationFn: () => {
      const patient = JSON.parse(localStorage.getItem('active_patient') || '{}')
      return inferenceApi.explain({
        frecuencia_cardiaca: 80, frecuencia_respiratoria: 16,
        presion_sistolica: 120, presion_diastolica: 80,
        temperatura: 36.5, saturacion_oxigeno: 98,
        edad: patient.edad || 35, sexo: patient.sexo || 'M',
        motivo_texto: 'Evaluación clínica de urgencias',
      })
    },
    onSuccess: (res) => { setShapResult(res.data); setShowShap(true) },
  })

  if (!triageId) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">No hay un triaje activo.</p>
      </div>
    )
  }

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold text-slate-800 mb-1">🧠 Clasificación IA</h1>
      <p className="text-sm text-slate-500 mb-6">Predicción del nivel de triaje por el modelo de Machine Learning</p>

      {!result && !predictMutation.isPending && (
        <div className="bg-white border border-slate-200 rounded-lg p-8 text-center">
          <p className="text-slate-500 mb-4">Ejecuta la clasificación automática con IA</p>
          <button
            onClick={() => predictMutation.mutate()}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-purple-700 transition-colors"
          >
            🧠 Clasificar con IA
          </button>
        </div>
      )}

      {predictMutation.isPending && <LoadingSpinner message="Analizando datos clínicos con IA..." />}

      {result && (
        <div className="space-y-5">
          {/* Resultado */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white border border-slate-200 rounded-lg p-6 text-center">
              <p className="text-sm text-slate-500 mb-2">Nivel Predicho</p>
              <div
                className="text-5xl font-bold inline-block px-6 py-3 rounded-xl"
                style={{ backgroundColor: NIVELES_COLORS[result.nivel_predicho] + '20', color: NIVELES_COLORS[result.nivel_predicho] }}
              >
                {result.nivel_predicho}
              </div>
            </div>
            <div className="bg-white border border-slate-200 rounded-lg p-6 md:col-span-2">
              <p className="text-sm text-slate-500 mb-3">Probabilidades por Nivel</p>
              {NIVELES_TRIAGE.map((nivel) => {
                const prob = result.probabilidades[nivel] || 0
                return (
                  <div key={nivel} className="flex items-center gap-2 mb-2">
                    <span className="w-6 text-xs font-bold" style={{ color: NIVELES_COLORS[nivel] }}>{nivel}</span>
                    <div className="flex-1 bg-slate-100 rounded-full h-4 overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{ width: `${(prob * 100).toFixed(0)}%`, backgroundColor: NIVELES_COLORS[nivel] }}
                      />
                    </div>
                    <span className="text-xs text-slate-500 w-12 text-right">{(prob * 100).toFixed(0)}%</span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* SHAP */}
          <div className="bg-white border border-slate-200 rounded-lg p-5">
            <button
              onClick={() => showShap ? setShowShap(false) : explainMutation.mutate()}
              disabled={explainMutation.isPending}
              className="text-sm text-purple-600 hover:text-purple-800 font-medium"
            >
              {showShap ? '🔽 Ocultar Explicación' : '🔍 Ver Explicación SHAP'}
            </button>
            {showShap && shapResult && (
              <div className="mt-4 space-y-2">
                {(shapResult as { top_features: { feature: string; importancia: number; direccion: string }[] }).top_features?.slice(0, 10).map((f, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="w-4 text-xs">{f.direccion === '+' ? '🔴' : '🟢'}</span>
                    <span className="flex-1 text-slate-700">{f.feature}</span>
                    <span className="text-slate-400">{f.importancia.toFixed(4)}</span>
                  </div>
                ))}
                {(shapResult as { fallback: boolean }).fallback && (
                  <p className="text-xs text-amber-600 mt-2">⚠️ Usando importancia de features (SHAP no disponible)</p>
                )}
              </div>
            )}
          </div>

          {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-600 text-sm">{error}</div>}

          <button
            onClick={() => navigate('/validacion')}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Continuar a Validación y Cierre
          </button>
        </div>
      )}
    </div>
  )
}
