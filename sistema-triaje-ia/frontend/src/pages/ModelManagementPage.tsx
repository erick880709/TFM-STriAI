import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { modelsApi, type ModelInfo, type DiskModel } from '../api/models'
import { inferenceApi, type InferenceStatus } from '../api/inference'
import { LoadingSpinner, ErrorAlert } from '../components/shared'

export default function ModelManagementPage() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<'disk' | 'db' | 'register'>('disk')

  const status = useQuery({ queryKey: ['inference-status'], queryFn: () => inferenceApi.status().then(r => r.data) })
  const dbModels = useQuery({ queryKey: ['models-db'], queryFn: () => modelsApi.list().then(r => r.data.data) })
  const diskModels = useQuery({ queryKey: ['models-disk'], queryFn: () => modelsApi.scanDisk().then(r => r.data.data) })
  const [regForm, setRegForm] = useState({ nombre: '', version: '', f1_score: '', auc_roc: '' })

  const activateMut = useMutation({
    mutationFn: (id: string) => modelsApi.activate(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['models-db'] }); qc.invalidateQueries({ queryKey: ['inference-status'] }) },
  })

  const registerMut = useMutation({
    mutationFn: () => modelsApi.register({ ...regForm, f1_score: regForm.f1_score ? parseFloat(regForm.f1_score) : undefined, auc_roc: regForm.auc_roc ? parseFloat(regForm.auc_roc) : undefined }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['models-db'] }); setRegForm({ nombre: '', version: '', f1_score: '', auc_roc: '' }) },
  })

  const s = status.data as InferenceStatus | undefined
  const currentActiveVersion = s?.version

  if (status.isLoading || dbModels.isLoading || diskModels.isLoading) return <LoadingSpinner message="Cargando modelos..." />

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800 mb-1">⚙️ Gestión de Modelos IA</h1>
      <p className="text-sm text-slate-500 mb-4">Registro, versionado y activación de modelos de ML</p>

      {status.isError && <ErrorAlert error="Error al obtener estado de inferencia" onRetry={() => status.refetch()} />}
      {s && (
        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm mb-6 ${s.modelo_cargado ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`} role="status" aria-live="polite">
          <span className={`w-2 h-2 rounded-full ${s.modelo_cargado ? 'bg-green-500' : 'bg-red-500'}`} />
          {s.modelo_cargado ? `Modelo Activo: ${s.version || '?'} · ${s.n_features || '?'} features` : 'Modelo no cargado'}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-slate-100 rounded-lg p-1 w-fit" role="tablist">
        {(['disk', 'db', 'register'] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)} role="tab" aria-selected={tab === t}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${tab === t ? 'bg-white shadow text-slate-800' : 'text-slate-500'}`}>
            {t === 'disk' ? '💾 Serializados' : t === 'db' ? '🗄️ Registro BD' : '➕ Registrar'}
          </button>
        ))}
      </div>

      {tab === 'disk' && (
        <div className="space-y-3">
          {diskModels.isError && <ErrorAlert error="Error al escanear modelos en disco" onRetry={() => diskModels.refetch()} />}
          {diskModels.data?.map((m: DiskModel) => {
            const isActive = m.version === currentActiveVersion
            return (
              <div key={m.version} className="bg-white border border-slate-200 rounded-lg p-4 flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-800">{m.nombre} {isActive ? <span className="text-xs text-green-600 font-medium">🟢 ACTIVO</span> : <span className="text-xs text-slate-400">⚪ Inactivo</span>}</p>
                  <p className="text-xs text-slate-400">v{m.version} · {m.n_features} features · {m.tamano_mb} MB</p>
                </div>
                <span className="text-sm text-slate-500">F1: {m.f1_macro?.toFixed(3) || '?'}</span>
              </div>
            )
          })}
          {diskModels.data?.length === 0 && <p className="text-slate-400">No se encontraron modelos en disco.</p>}
        </div>
      )}

      {tab === 'db' && (
        <div className="space-y-3">
          {dbModels.data?.map((m: ModelInfo) => (
            <div key={m.IdModelo} className="bg-white border border-slate-200 rounded-lg p-4 flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-800">{m.Nombre} <span className={`text-xs ${m.Estado === 'Activo' ? 'text-green-600' : 'text-slate-400'}`}>{m.Estado === 'Activo' ? '🟢' : '⚪'} {m.Estado}</span></p>
                <p className="text-xs text-slate-400">v{m.Version} · {m.Arquitectura} · F1: {m.F1Score || '?'}</p>
              </div>
              {m.Estado !== 'Activo' && m.IdModelo && (
                <button onClick={() => activateMut.mutate(m.IdModelo!)} className="text-sm bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700">🟢 Activar</button>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === 'register' && (
        <div className="bg-white border border-slate-200 rounded-lg p-5 max-w-md space-y-4">
          {(['nombre', 'version'] as const).map((f) => (
            <div key={f}>
              <label className="block text-xs font-medium text-slate-500 mb-1 capitalize">{f.replace('_', ' ')} *</label>
              <input value={regForm[f]} onChange={(e) => setRegForm(p => ({ ...p, [f]: e.target.value }))} className="input w-full" />
            </div>
          ))}
          <button onClick={() => registerMut.mutate()} disabled={registerMut.isPending || !regForm.nombre || !regForm.version}
            className="w-full bg-blue-600 text-white py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
            {registerMut.isPending ? 'Registrando...' : 'Registrar Modelo'}
          </button>
        </div>
      )}
    </div>
  )
}
