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
    </div>
  )
}
