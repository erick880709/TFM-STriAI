import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import type { ApiResponse } from '../types/api'
import { LoadingSpinner } from '../components/shared'

export default function ControlCambiosPage() {
  const [doc, setDoc] = useState('')
  const { data, isLoading } = useQuery({
    queryKey: ['control-cambios', doc],
    queryFn: () => api.get<ApiResponse<unknown[]>>('/control-cambios', { params: { documento: doc || undefined } }).then(r => r.data.data),
  })

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800 mb-1">📝 Control de Cambios</h1>
      <p className="text-sm text-slate-500 mb-6">Registro de modificaciones sobre datos de pacientes</p>

      <div className="flex gap-3 mb-6 max-w-md">
        <input type="text" placeholder="Filtrar por documento" value={doc}
          onChange={e => setDoc(e.target.value)}
          className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      {isLoading ? <LoadingSpinner /> : (
        <div className="overflow-x-auto">
          <table className="w-full bg-white border border-slate-200 rounded-lg text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase">
                <th className="px-4 py-3">Fecha</th><th className="px-4 py-3">Usuario</th><th className="px-4 py-3">Campo</th><th className="px-4 py-3">Anterior</th><th className="px-4 py-3">Nuevo</th>
              </tr>
            </thead>
            <tbody>
              {(data || []).map((c: unknown, i: number) => {
                const cambio = c as Record<string, unknown>
                return (
                  <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="px-4 py-3 text-slate-500 text-xs">{String(cambio.Fecha || cambio.fecha || '').slice(0, 16)}</td>
                    <td className="px-4 py-3 font-medium">{String(cambio.Usuario || cambio.usuario || '')}</td>
                    <td className="px-4 py-3">{String(cambio.Campo || cambio.campo || '')}</td>
                    <td className="px-4 py-3 text-slate-500">{String(cambio.ValorAnterior || cambio.valor_anterior || '')}</td>
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
