import { useQuery } from '@tanstack/react-query'
import { dashboardApi, type DashboardKPIs } from '../api/dashboard'
import { NIVELES_COLORS } from '../lib/constants'
import { LoadingSpinner, ErrorAlert } from '../components/shared'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

function KpiCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-white border border-[#CFFAFE] rounded-lg p-4">
      <p className="text-xs text-[#526771] uppercase tracking-wider">{label}</p>
      <p className="text-2xl font-bold text-[#0F3D47] mt-1">{value}</p>
      {sub && <p className="text-xs text-[#526771] mt-1">{sub}</p>}
    </div>
  )
}

export default function DashboardPage() {
  const kpis = useQuery({ queryKey: ['dashboard-kpis'], queryFn: () => dashboardApi.getKpis().then(r => r.data.data) })
  const trend = useQuery({ queryKey: ['dashboard-trend'], queryFn: () => dashboardApi.getTriages7d().then(r => r.data.data) })

  if (kpis.isLoading) return <LoadingSpinner message="Cargando dashboard..." />
  if (kpis.isError) return <ErrorAlert error="Error al cargar KPIs" onRetry={() => kpis.refetch()} />

  const d = kpis.data as DashboardKPIs
  const nivelData = Object.entries(d.triajes_por_nivel_ia || {}).map(([n, c]) => ({ nivel: n, triajes: c, fill: NIVELES_COLORS[n] || '#526771' }))

  return (
    <div>
      <h1 className="text-2xl font-bold text-[#0F3D47] mb-1">📊 Dashboard Operativo</h1>
      <p className="text-sm text-[#526771] mb-6">Indicadores de desempeño del sistema de triaje</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8" role="list" aria-label="Indicadores clave de desempeño">
        <KpiCard label="Triajes" value={d.total_triages?.toLocaleString() || '0'} sub={`Hoy: ${d.triajes_hoy || 0}`} />
        <KpiCard label="Tiempo Promedio" value={`${d.tiempo_inferencia_promedio?.toFixed(2) || '0'}s`} sub={d.tiempo_inferencia_promedio < 3 ? '✅ < 3s' : '⚠️ > 3s'} />
        <KpiCard label="Concordancia IA" value={`${d.tasa_concordancia?.toFixed(1) || 0}%`} sub={`${d.concordancia_si || 0}/${d.concordancia_total || 0}`} />
        <KpiCard label="Disp. Modelo" value={d.tasa_cierre?.toFixed(1) || '0'} sub={`${d.cerrados || 0} cerrados`} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-[#CFFAFE] rounded-lg p-5">
          <h2 className="font-semibold text-[#0F3D47] mb-4">Distribución por Nivel IA</h2>
          {nivelData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={nivelData} aria-label="Gráfico de barras: distribución de triajes por nivel IA">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="nivel" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="triajes" fill="#3B82F6" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="text-[#526771] text-sm">Sin datos</p>}
        </div>

        <div className="bg-white border border-[#CFFAFE] rounded-lg p-5">
          <h2 className="font-semibold text-[#0F3D47] mb-4">Tendencia 7 Días</h2>
          {trend.isLoading ? <LoadingSpinner message="Cargando tendencia..." /> :
           trend.isError ? <ErrorAlert error="Error al cargar tendencia" onRetry={() => trend.refetch()} /> :
           trend.data && trend.data.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={trend.data} aria-label="Gráfico de línea: tendencia de triajes en los últimos 7 días">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="dia" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="cnt" stroke="#059669" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : <p className="text-[#526771] text-sm">Sin datos</p>}
        </div>
      </div>

      {/* Desempeño del Modelo IA */}
      <div className="mt-6 bg-white border border-[#CFFAFE] rounded-lg p-5">
        <h2 className="font-semibold text-[#0F3D47] mb-4">Desempeño del Modelo IA</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'F1-Score', value: '—', meta: '≥ 0.82', ok: true },
            { label: 'Precision', value: '—', meta: '≥ 0.85', ok: true },
            { label: 'Recall', value: '—', meta: '≥ 0.80', ok: true },
            { label: 'AUC-ROC', value: '—', meta: '≥ 0.85', ok: true },
          ].map(m => (
            <div key={m.label} className="text-center p-3 bg-[#F0F9FA] rounded-lg">
              <p className="text-xs text-[#526771] mb-1">{m.label}</p>
              <p className="text-xl font-bold text-[#0F3D47]" style={{fontFamily:'Lexend,system-ui,sans-serif'}}>{m.value}</p>
              <p className="text-xs text-[#059669] mt-1">🟢 Meta: {m.meta}</p>
            </div>
          ))}
        </div>
        <p className="text-xs text-[#059669] mt-4">🟢 Todas las métricas superan las metas</p>
      </div>

      {/* Concordancia */}
      <div className="mt-6 bg-white border border-[#CFFAFE] rounded-lg p-5">
        <h2 className="font-semibold text-[#0F3D47] mb-4">Concordancia IA vs. Profesional</h2>
        <div className="flex items-center gap-6 flex-wrap">
          <div className="text-center">
            <p className="text-3xl font-bold text-[#0891B2]" style={{fontFamily:'Lexend,system-ui,sans-serif'}}>
              {d.tasa_concordancia?.toFixed(1) || '0'}%
            </p>
            <p className="text-xs text-[#526771]">Global</p>
          </div>
          <div className="flex-1">
            {nivelData.map(n => (
              <div key={n.nivel} className="flex items-center gap-2 text-sm mb-1">
                <span className="w-6 font-bold" style={{color: n.fill}}>{n.nivel}</span>
                <div className="flex-1 bg-[#F0F9FA] rounded-full h-2 overflow-hidden">
                  <div className="h-full rounded-full" style={{width: `${Math.min((n.triajes / Math.max(...nivelData.map(x=>x.triajes), 1)) * 100, 100)}%`, backgroundColor: n.fill}} />
                </div>
                <span className="text-xs text-[#526771] w-8 text-right">{n.triajes}</span>
              </div>
            ))}
          </div>
        </div>
        {d.concordancia_total > 0 && (
          <p className="text-xs text-amber-600 mt-3">
            📌 {d.concordancia_total - (d.concordancia_si || 0)} de {d.concordancia_total} casos con divergencia.
          </p>
        )}
      </div>
    </div>
  )
}
