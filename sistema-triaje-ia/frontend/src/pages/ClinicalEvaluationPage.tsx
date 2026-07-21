import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { triagesApi } from '../api/triages'
import { NIVELES_CONCIENCIA, COMORBILIDADES } from '../lib/constants'

export default function ClinicalEvaluationPage() {
  const navigate = useNavigate()
  const triageId = localStorage.getItem('active_triage_id') || ''
  const [form, setForm] = useState({
    motivo_consulta: '',
    categoria_motivo: 'Dolor torácico',
    glasgow_ocular: 4,
    glasgow_verbal: 5,
    glasgow_motora: 6,
    escala_dolor: 0,
    nivel_conciencia: 'Alerta',
    comorbilidades: [] as string[],
  })
  const [error, setError] = useState('')

  const glasgowTotal = form.glasgow_ocular + form.glasgow_verbal + form.glasgow_motora
  const glasgowSeverity = glasgowTotal <= 8 ? 'Grave' : glasgowTotal <= 12 ? 'Moderado' : 'Leve'
  const glasgowColor = glasgowTotal <= 8 ? 'text-red-600' : glasgowTotal <= 12 ? 'text-amber-600' : 'text-green-600'

  const saveMutation = useMutation({
    mutationFn: () => triagesApi.saveClinicalEval(triageId, {
      ...form,
      glasgow_total: glasgowTotal,
    }),
    onSuccess: () => navigate('/clasificacion-ia'),
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      setError(e.response?.data?.detail || 'Error al guardar evaluación')
    },
  })

  const toggleComorbidity = (c: string) => {
    setForm((prev) => ({
      ...prev,
      comorbilidades: prev.comorbilidades.includes(c)
        ? prev.comorbilidades.filter((x) => x !== c)
        : [...prev.comorbilidades, c],
    }))
  }

  if (!triageId) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">No hay un triaje activo. Inicia desde el registro de paciente.</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-slate-800 mb-1">🩺 Evaluación Clínica</h1>
      <p className="text-sm text-slate-500 mb-6">Motivo de consulta, Glasgow, dolor y comorbilidades</p>

      <div className="space-y-5">
        {/* Motivo */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h2 className="font-semibold text-slate-700 mb-3">Motivo de Consulta</h2>
          <textarea
            value={form.motivo_consulta}
            onChange={(e) => setForm((p) => ({ ...p, motivo_consulta: e.target.value }))}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
            placeholder="Describa el motivo de consulta del paciente..."
            required
          />
          <select
            value={form.categoria_motivo}
            onChange={(e) => setForm((p) => ({ ...p, categoria_motivo: e.target.value }))}
            className="mt-3 px-3 py-2 border border-slate-300 rounded-lg text-sm"
          >
            {['Dolor torácico', 'Dificultad respiratoria', 'Trauma', 'Dolor abdominal', 'Cefalea', 'Fiebre', 'Otro'].map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Glasgow */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h2 className="font-semibold text-slate-700 mb-3">Escala de Glasgow</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { key: 'glasgow_ocular', label: 'Apertura Ocular', min: 1, max: 4 },
              { key: 'glasgow_verbal', label: 'Respuesta Verbal', min: 1, max: 5 },
              { key: 'glasgow_motora', label: 'Respuesta Motora', min: 1, max: 6 },
            ].map((g) => (
              <div key={g.key}>
                <label className="block text-xs font-medium text-slate-500 mb-1">{g.label}</label>
                <input
                  type="number" min={g.min} max={g.max}
                  value={form[g.key as keyof typeof form] as number}
                  onChange={(e) => setForm((p) => ({ ...p, [g.key]: parseInt(e.target.value) || g.min }))}
                  className="w-20 px-3 py-2 border border-slate-300 rounded-lg text-sm text-center"
                />
              </div>
            ))}
          </div>
          <div className={`mt-3 text-lg font-bold ${glasgowColor}`}>
            Total: {glasgowTotal}/15 — {glasgowSeverity}
          </div>
        </div>

        {/* Dolor + Conciencia */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="font-semibold text-slate-700 mb-3">Escala de Dolor (0-10)</h2>
              <input
                type="range" min={0} max={10} value={form.escala_dolor}
                onChange={(e) => setForm((p) => ({ ...p, escala_dolor: parseInt(e.target.value) }))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>0 Sin dolor</span>
                <span className={`font-bold text-lg ${form.escala_dolor >= 7 ? 'text-red-600' : form.escala_dolor >= 3 ? 'text-amber-600' : 'text-green-600'}`}>
                  {form.escala_dolor}/10
                </span>
                <span>10 Máximo</span>
              </div>
            </div>
            <div>
              <h2 className="font-semibold text-slate-700 mb-3">Nivel de Conciencia</h2>
              <select value={form.nivel_conciencia}
                onChange={(e) => setForm((p) => ({ ...p, nivel_conciencia: e.target.value }))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm">
                {NIVELES_CONCIENCIA.map((n) => <option key={n}>{n}</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* Comorbilidades */}
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h2 className="font-semibold text-slate-700 mb-3">Comorbilidades</h2>
          <div className="flex flex-wrap gap-2">
            {COMORBILIDADES.map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => toggleComorbidity(c)}
                className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                  form.comorbilidades.includes(c)
                    ? 'bg-blue-100 border-blue-300 text-blue-700'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-600 text-sm">{error}</div>}

        <button
          onClick={() => saveMutation.mutate()}
          disabled={saveMutation.isPending || !form.motivo_consulta.trim()}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {saveMutation.isPending ? 'Guardando...' : 'Guardar y Continuar a Clasificación IA'}
        </button>
      </div>
    </div>
  )
}
