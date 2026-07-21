import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import type { ApiResponse } from '../types/api'
import { LoadingSpinner, ErrorAlert, EmptyState } from '../components/shared'

export default function ControlCambiosPage() {
  const [doc, setDoc] = useState('')
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['control-cambios', doc],
    queryFn: () => api.get<ApiResponse<unknown[]>>('/control-cambios', { params: { documento: doc || undefined } }).then(r => r.data.data),
  })

  if (isLoading) return <LoadingSpinner message="Cargando control de cambios..." />
  if (isError) return <ErrorAlert error={`Error al cargar datos: ${(error as Error)?.message || 'Error desconocido'}`} onRetry={() => refetch()} />

  return (
    <div>
      <h1 className="text-2xl font-bold text-[#0F3D47] mb-1">📝 Control de Cambios</h1>
      <p className="text-sm text-[#526771] mb-6">Registro de modificaciones sobre datos de pacientes</p>

      <div className="flex gap-3 mb-6 max-w-md">
        <input type="text" placeholder="Filtrar por documento" value={doc} aria-label="Número de documento"
          onChange={e => setDoc(e.target.value)}
          className="flex-1 px-3 py-2 border border-[#A5F3FC] rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      {!data || data.length === 0 ? <EmptyState message="No se encontraron cambios registrados." /> : (
        <div className="overflow-x-auto">
          <table className="w-full bg-white border border-[#CFFAFE] rounded-lg text-sm">
            <caption className="sr-only">Historial de modificaciones sobre datos</caption>
            <thead>
              <tr className="border-b border-[#CFFAFE] bg-[#F0F9FA] text-left text-xs font-medium text-[#526771] uppercase">
                <th scope="col" className="px-4 py-3">Fecha</th><th scope="col" className="px-4 py-3">Usuario</th><th scope="col" className="px-4 py-3">Campo</th><th scope="col" className="px-4 py-3">Anterior</th><th scope="col" className="px-4 py-3">Nuevo</th>
              </tr>
            </thead>
            <tbody>
              {(data || []).map((c: unknown, i: number) => {
                const cambio = c as Record<string, unknown>
                return (
                  <tr key={i} className="border-b border-[#CFFAFE] hover:bg-[#F0F9FA]">
                    <td className="px-4 py-3 text-[#526771] text-xs">{String(cambio.Fecha || cambio.fecha || '').slice(0, 16)}</td>
                    <td className="px-4 py-3 font-medium">{String(cambio.Usuario || cambio.usuario || '')}</td>
                    <td className="px-4 py-3">{String(cambio.Campo || cambio.campo || '')}</td>
                    <td className="px-4 py-3 text-[#526771]">{String(cambio.ValorAnterior || cambio.valor_anterior || '')}</td>
                    <td className="px-4 py-3">{String(cambio.ValorNuevo || cambio.valor_nuevo || '')}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
