import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { auditApi, type AuditEntry } from '../api/audit'
import { LoadingSpinner } from '../components/shared'

export default function AuditPage() {
  const [filters, setFilters] = useState({ fecha_desde: '', fecha_hasta: '', accion: '', entidad: '', usuario: '', page: 1 })
  const { data, isLoading } = useQuery({
    queryKey: ['audit', filters],
    queryFn: () => auditApi.query(filters).then(r => r.data),
  })

  const handleExport = async () => {
    const res = await auditApi.exportCsv(filters)
    const blob = new Blob([res.data as BlobPart], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'auditoria.csv'; a.click()
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800 mb-1">🔍 Auditoría</h1>
      <p className="text-sm text-slate-500 mb-6">Registro de acciones en el sistema</p>

      <div className="flex flex-wrap gap-3 mb-6">
        <input type="date" value={filters.fecha_desde} onChange={e => setFilters(p => ({ ...p, fecha_desde: e.target.value, page: 1 }))}
          className="px-3 py-2 border border-slate-300 rounded-lg text-sm" />
        <input type="date" value={filters.fecha_hasta} onChange={e => setFilters(p => ({ ...p, fecha_hasta: e.target.value, page: 1 }))}
          className="px-3 py-2 border border-slate-300 rounded-lg text-sm" />
        <input type="text" placeholder="Acción" value={filters.accion} onChange={e => setFilters(p => ({ ...p, accion: e.target.value, page: 1 }))}
          className="px-3 py-2 border border-slate-300 rounded-lg text-sm w-32" />
        <input type="text" placeholder="Entidad" value={filters.entidad} onChange={e => setFilters(p => ({ ...p, entidad: e.target.value, page: 1 }))}
          className="px-3 py-2 border border-slate-300 rounded-lg text-sm w-32" />
        <button onClick={handleExport} className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700">📥 CSV</button>
      </div>

      {isLoading ? <LoadingSpinner /> : (
        <div className="overflow-x-auto">
          <table className="w-full bg-white border border-slate-200 rounded-lg text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase">
                <th className="px-4 py-3">Fecha</th><th className="px-4 py-3">Usuario</th><th className="px-4 py-3">Acción</th><th className="px-4 py-3">Entidad</th><th className="px-4 py-3">Detalle</th>
              </tr>
            </thead>
            <tbody>
              {((data as { items?: AuditEntry[] })?.items || []).map((e, i) => (
                <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-500 text-xs">{e.FechaHora?.slice(0, 16)}</td>
                  <td className="px-4 py-3 font-medium">{e.Usuario}</td>
                  <td className="px-4 py-3">{e.Accion}</td>
                  <td className="px-4 py-3">{e.EntidadAfectada}</td>
                  <td className="px-4 py-3 text-slate-500 text-xs max-w-xs truncate">{e.Observaciones}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {(data as { pages?: number })?.pages && (data as { pages: number }).pages > 1 && (
            <div className="flex justify-center gap-2 mt-4">
              {Array.from({ length: (data as { pages: number }).pages }, (_, i) => (
                <button key={i} onClick={() => setFilters(p => ({ ...p, page: i + 1 }))}
                  className={`px-3 py-1 rounded text-sm ${filters.page === i + 1 ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}>
                  {i + 1}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
