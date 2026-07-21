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
      <h1 className="text-2xl font-bold text-[#164E63] mb-1">📝 Control de Cambios</h1>
      <p className="text-sm text-[#64748B] mb-6">Registro de modificaciones sobre datos de pacientes</p>

      <div className="flex gap-3 mb-6 max-w-md">
        <input type="text" placeholder="Filtrar por documento" value={doc} aria-label="Número de documento"
          onChange={e => setDoc(e.target.value)}
          className="flex-1 px-3 py-2 border border-[#A5F3FC] rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      {!data || data.length === 0 ? <EmptyState message="No se encontraron cambios registrados." /> : (
        <div className="overflow-x-auto">
          <table className="w-full bg-white border border-[#A5F3FC] rounded-lg text-sm">
            <caption className="sr-only">Historial de modificaciones sobre datos</caption>
            <thead>
              <tr className="border-b border-[#A5F3FC] bg-[#ECFEFF] text-left text-xs font-medium text-[#64748B] uppercase">
                <th scope="col" className="px-4 py-3">Fecha</th><th scope="col" className="px-4 py-3">Usuario</th><th scope="col" className="px-4 py-3">Campo</th><th scope="col" className="px-4 py-3">Anterior</th><th scope="col" className="px-4 py-3">Nuevo</th>
              </tr>
            </thead>
            <tbody>
              {(data || []).map((c: unknown, i: number) => {
                const cambio = c as Record<string, unknown>
                return (
                  <tr key={i} className="border-b border-[#A5F3FC] hover:bg-[#ECFEFF]">
                    <td className="px-4 py-3 text-[#64748B] text-xs">{String(cambio.Fecha || cambio.fecha || '').slice(0, 16)}</td>
                    <td className="px-4 py-3 font-medium">{String(cambio.Usuario || cambio.usuario || '')}</td>
                    <td className="px-4 py-3">{String(cambio.Campo || cambio.campo || '')}</td>
                    <td className="px-4 py-3 text-[#64748B]">{String(cambio.ValorAnterior || cambio.valor_anterior || '')}</td>
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
