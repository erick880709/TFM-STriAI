import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { auditApi, type AuditEntry } from '../api/audit'
import { LoadingSpinner, ErrorAlert, EmptyState } from '../components/shared'

export default function AuditPage() {
  const [filters, setFilters] = useState({ fecha_desde: '', fecha_hasta: '', accion: '', entidad: '', usuario: '', page: 1 })
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['audit', filters],
    queryFn: () => auditApi.query(filters).then(r => r.data),
  })

  const handleExport = async () => {
    const res = await auditApi.exportCsv(filters)
    const blob = new Blob([res.data as BlobPart], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'auditoria.csv'; a.click()
  }

  if (isLoading) return <LoadingSpinner message="Cargando registros de auditoría..." />
  if (isError) return <ErrorAlert error={`Error al cargar auditoría: ${(error as Error)?.message || 'Error desconocido'}`} onRetry={() => refetch()} />

  const items = (data as { items?: AuditEntry[] })?.items || []

  return (
    <div>
      <h1 className="text-2xl font-bold text-[#164E63] mb-1">🔍 Auditoría</h1>
      <p className="text-sm text-[#64748B] mb-6">Registro de acciones en el sistema</p>

      <div className="flex flex-wrap gap-3 mb-6">
        <input type="date" value={filters.fecha_desde} onChange={e => setFilters(p => ({ ...p, fecha_desde: e.target.value, page: 1 }))}
          className="px-3 py-2 border border-[#A5F3FC] rounded-lg text-sm" aria-label="Fecha desde" />
        <input type="date" value={filters.fecha_hasta} onChange={e => setFilters(p => ({ ...p, fecha_hasta: e.target.value, page: 1 }))}
          className="px-3 py-2 border border-[#A5F3FC] rounded-lg text-sm" aria-label="Fecha hasta" />
        <input type="text" placeholder="Acción" value={filters.accion} onChange={e => setFilters(p => ({ ...p, accion: e.target.value, page: 1 }))}
          className="px-3 py-2 border border-[#A5F3FC] rounded-lg text-sm w-32" aria-label="Filtrar por acción" />
        <input type="text" placeholder="Entidad" value={filters.entidad} onChange={e => setFilters(p => ({ ...p, entidad: e.target.value, page: 1 }))}
          className="px-3 py-2 border border-[#A5F3FC] rounded-lg text-sm w-32" aria-label="Filtrar por entidad" />
        <button onClick={handleExport} className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700">📥 CSV</button>
      </div>

      {items.length === 0 ? <EmptyState message="No se encontraron registros de auditoría con los filtros seleccionados." /> : (
        <div className="overflow-x-auto">
          <table className="w-full bg-white border border-[#A5F3FC] rounded-lg text-sm">
            <caption className="sr-only">Registros de auditoría del sistema</caption>
            <thead>
              <tr className="border-b border-[#A5F3FC] bg-[#ECFEFF] text-left text-xs font-medium text-[#64748B] uppercase">
                <th scope="col" className="px-4 py-3">Fecha</th><th scope="col" className="px-4 py-3">Usuario</th><th scope="col" className="px-4 py-3">Acción</th><th scope="col" className="px-4 py-3">Entidad</th><th scope="col" className="px-4 py-3">Detalle</th>
              </tr>
            </thead>
            <tbody>
              {items.map((e, i) => (
                <tr key={i} className="border-b border-[#A5F3FC] hover:bg-[#ECFEFF]">
                  <td className="px-4 py-3 text-[#64748B] text-xs">{e.FechaHora?.slice(0, 16)}</td>
                  <td className="px-4 py-3 font-medium">{e.Usuario}</td>
                  <td className="px-4 py-3">{e.Accion}</td>
                  <td className="px-4 py-3">{e.EntidadAfectada}</td>
                  <td className="px-4 py-3 text-[#64748B] text-xs max-w-xs truncate">{e.Observaciones}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {(data as { pages?: number })?.pages && (data as { pages: number }).pages > 1 && (
            <div className="flex justify-center gap-2 mt-4">
              {Array.from({ length: (data as { pages: number }).pages }, (_, i) => (
                <button key={i} onClick={() => setFilters(p => ({ ...p, page: i + 1 }))}
                  className={`px-3 py-1 rounded text-sm ${filters.page === i + 1 ? 'bg-blue-600 text-white' : 'bg-[#ECFEFF] text-[#64748B] hover:bg-[#A5F3FC]'}`}>
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
