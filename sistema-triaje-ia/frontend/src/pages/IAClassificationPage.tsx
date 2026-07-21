import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { inferenceApi, type PredictResult } from '../api/inference'
import { triagesApi } from '../api/triages'
import type { VitalSigns } from '../types/triage'
import { NIVELES_TRIAGE, NIVELES_COLORS } from '../lib/constants'
import { LoadingSpinner, ErrorAlert } from '../components/shared'
import StepIndicator from '../components/clinical/StepIndicator'

function ShapDisplay({ data }: { data: { top_features?: { feature: string; importancia: number; direccion: string }[]; fallback?: boolean } }) {
  return (
    <div className="mt-4 space-y-2">
      {data.top_features?.slice(0, 10).map((f, i) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          <span className="w-4 text-xs" aria-label={f.direccion === '+' ? 'Aumenta riesgo' : 'Reduce riesgo'}>{f.direccion === '+' ? '🔴' : '🟢'}</span>
          <span className="flex-1 text-[#0F3D47]">{f.feature}</span>
          <span className="text-[#526771]">{f.importancia.toFixed(4)}</span>
        </div>
      ))}
      {data.fallback && (
        <p className="text-xs text-amber-600 mt-2">⚠️ Usando importancia de features (SHAP no disponible)</p>
      )}
    </div>
  )
}

function buildClinicalData(vs: VitalSigns | undefined, evalData: Record<string, unknown> | undefined) {
  const patient = JSON.parse(localStorage.getItem('active_patient') || '{}')
  return {
    frecuencia_cardiaca: vs?.frecuencia_cardiaca ?? 0,
    frecuencia_respiratoria: vs?.frecuencia_respiratoria ?? 0,
    presion_sistolica: vs?.presion_sistolica ?? 0,
    presion_diastolica: vs?.presion_diastolica ?? 0,
    temperatura: vs?.temperatura ?? 0,
    saturacion_oxigeno: vs?.saturacion_oxigeno ?? 0,
    edad: patient.edad || 35,
    sexo: patient.sexo || 'M',
    motivo_texto: (evalData?.motivo_consulta as string) || '',
  }
}

export default function IAClassificationPage() {
  const navigate = useNavigate()
  const triageId = localStorage.getItem('active_triage_id') || ''
  const [result, setResult] = useState<PredictResult | null>(null)
  const [shapResult, setShapResult] = useState<unknown>(null)
  const [error, setError] = useState('')
  const [showShap, setShowShap] = useState(false)

  // Cargar signos vitales reales del triaje
  const vitalSignsQuery = useQuery({
    queryKey: ['vital-signs', triageId],
    queryFn: () => triagesApi.getVitalSigns(triageId).then(r => r.data.data as VitalSigns),
    enabled: !!triageId,
  })

  // Cargar evaluación clínica real del triaje
  const clinicalEvalQuery = useQuery({
    queryKey: ['clinical-eval', triageId],
    queryFn: () => triagesApi.getClinicalEval(triageId).then(r => r.data.data as Record<string, unknown>),
    enabled: !!triageId,
  })

  const predictMutation = useMutation({
    mutationFn: () => {
      return inferenceApi.predict(buildClinicalData(vitalSignsQuery.data, clinicalEvalQuery.data))
    },
    onSuccess: (res) => setResult(res.data),
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      setError(e.response?.data?.detail || 'Error en la clasificación IA')
    },
  })

  const explainMutation = useMutation({
    mutationFn: () => {
      return inferenceApi.explain(buildClinicalData(vitalSignsQuery.data, clinicalEvalQuery.data))
    },
    onSuccess: (res) => { setShapResult(res.data); setShowShap(true) },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      setError(e.response?.data?.detail || 'Error al generar explicación')
    },
  })

  if (!triageId) {
    return (
      <div className="text-center py-12">
        <p className="text-[#526771]">No hay un triaje activo. Inicia desde el registro de paciente.</p>
        <button onClick={() => navigate('/pacientes')} className="mt-3 text-sm text-purple-600 underline">
          Ir a Registro de Paciente
        </button>
      </div>
    )
  }

  if (vitalSignsQuery.isLoading || clinicalEvalQuery.isLoading) {
    return <LoadingSpinner message="Cargando datos clínicos del paciente..." />
  }

  if (vitalSignsQuery.isError || clinicalEvalQuery.isError) {
    return <ErrorAlert error="No se pudieron cargar los datos clínicos del paciente. Verifica que los signos vitales y la evaluación clínica estén completos." />
  }

  return (
    <div className="max-w-3xl">
      <StepIndicator step={4} label="Flujo Triaje" />
      <h1 className="text-2xl font-bold text-[#0F3D47] mb-1">🧠 Clasificación IA</h1>
      <p className="text-sm text-[#526771] mb-6">Predicción del nivel de triaje por el modelo de Machine Learning</p>

      {!result && !predictMutation.isPending && (
        <div className="bg-white border border-[#CFFAFE] rounded-lg p-8 text-center">
          <p className="text-[#526771] mb-4">Ejecuta la clasificación automática con IA usando los datos clínicos del paciente</p>
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
            <div className="bg-white border border-[#CFFAFE] rounded-lg p-6 text-center">
              <p className="text-sm text-[#526771] mb-2">Nivel Predicho</p>
              <div
                className="text-5xl font-bold inline-block px-6 py-3 rounded-xl"
                style={{ backgroundColor: NIVELES_COLORS[result.nivel_predicho] + '20', color: NIVELES_COLORS[result.nivel_predicho] }}
              >
                {result.nivel_predicho}
              </div>
            </div>
            <div className="bg-white border border-[#CFFAFE] rounded-lg p-6 md:col-span-2">
              <p className="text-sm text-[#526771] mb-3">Probabilidades por Nivel</p>
              {NIVELES_TRIAGE.map((nivel) => {
                const prob = result.probabilidades[nivel] || 0
                return (
                  <div key={nivel} className="flex items-center gap-2 mb-2">
                    <span className="w-6 text-xs font-bold" style={{ color: NIVELES_COLORS[nivel] }}>{nivel}</span>
                    <div className="flex-1 bg-[#F0F9FA] rounded-full h-4 overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{ width: `${(prob * 100).toFixed(0)}%`, backgroundColor: NIVELES_COLORS[nivel] }}
                      />
                    </div>
                    <span className="text-xs text-[#526771] w-12 text-right">{(prob * 100).toFixed(0)}%</span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* SHAP */}
          <div className="bg-white border border-[#CFFAFE] rounded-lg p-5">
            <button
              onClick={() => showShap ? setShowShap(false) : explainMutation.mutate()}
              disabled={explainMutation.isPending}
              className="text-sm text-purple-600 hover:text-purple-800 font-medium"
            >
              {showShap ? '🔽 Ocultar Explicación' : '🔍 Ver Explicación SHAP'}
            </button>
            {showShap && shapResult != null && (
              <ShapDisplay data={shapResult as { top_features?: { feature: string; importancia: number; direccion: string }[]; fallback?: boolean }} />
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
