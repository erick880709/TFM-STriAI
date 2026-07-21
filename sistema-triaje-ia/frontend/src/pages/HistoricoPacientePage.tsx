import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { patientsApi } from '../api/patients'
import { LoadingSpinner, ErrorAlert, EmptyState } from '../components/shared'
import type { Patient } from '../types/patient'

export default function HistoricoPacientePage() {
  const [doc, setDoc] = useState('')
  const [searchedDoc, setSearchedDoc] = useState('')

  const patientQuery = useQuery({
    queryKey: ['patient', searchedDoc],
    queryFn: () => patientsApi.getByDocument(searchedDoc).then(r => r.data.data as Patient),
    enabled: !!searchedDoc,
  })

  const triagesQuery = useQuery({
    queryKey: ['patient-triages', patientQuery.data?.id_paciente],
    queryFn: () => patientsApi.getTriages(Number(patientQuery.data!.id_paciente)).then(r => r.data.data as unknown[]),
    enabled: !!patientQuery.data?.id_paciente,
  })

  const handleSearch = () => { if (doc.trim()) setSearchedDoc(doc.trim()) }

  return (
    <div>
      <h1 className="text-2xl font-bold text-[#164E63] mb-1">📜 Histórico del Paciente</h1>
      <p className="text-sm text-[#64748B] mb-6">Consulta del historial de triajes por documento</p>

      <div className="flex gap-3 mb-6 max-w-md">
        <input type="text" placeholder="Número de documento" value={doc} aria-label="Buscar paciente por documento"
          onChange={e => setDoc(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSearch()}
          className="flex-1 px-3 py-2 border border-[#A5F3FC] rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500" />
        <button onClick={handleSearch} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">Buscar</button>
      </div>

      {patientQuery.isLoading && <LoadingSpinner message="Buscando paciente..." />}
      {patientQuery.isError && <ErrorAlert error="No se encontró el paciente. Verifica el número de documento." />}

      {patientQuery.data && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <p className="font-medium text-green-800">{(patientQuery.data as Patient).nombre} {(patientQuery.data as Patient).apellido}</p>
          <p className="text-sm text-green-600">Doc: {(patientQuery.data as Patient).numero_documento} · EPS: {(patientQuery.data as Patient).eps} · Episodios: {(patientQuery.data as Patient).episodios_previos ?? 0}</p>
        </div>
      )}

      {triagesQuery.isLoading && <LoadingSpinner message="Cargando historial de triajes..." />}
      {triagesQuery.isError && <ErrorAlert error="Error al cargar el historial de triajes." onRetry={() => triagesQuery.refetch()} />}

      {triagesQuery.data && triagesQuery.data.length === 0 && <EmptyState message="El paciente no tiene triajes registrados." />}

      {triagesQuery.data && triagesQuery.data.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full bg-white border border-[#A5F3FC] rounded-lg text-sm">
            <caption className="sr-only">Historial de triajes del paciente</caption>
            <thead>
              <tr className="border-b border-[#A5F3FC] bg-[#ECFEFF] text-left text-xs font-medium text-[#64748B] uppercase">
                <th scope="col" className="px-4 py-3">Fecha</th><th scope="col" className="px-4 py-3">Nivel IA</th><th scope="col" className="px-4 py-3">Nivel Prof.</th><th scope="col" className="px-4 py-3">Concordancia</th><th scope="col" className="px-4 py-3">Estado</th>
              </tr>
            </thead>
            <tbody>
              {(triagesQuery.data as unknown[]).map((t: unknown, i: number) => {
                const triage = t as Record<string, unknown>
                const concordancia = triage.Concordancia || triage.concordancia
                return (
                  <tr key={i} className="border-b border-[#A5F3FC] hover:bg-[#ECFEFF]">
                    <td className="px-4 py-3 text-[#64748B] text-xs">{String(triage.FechaHoraIngreso || triage.fecha_inicio || '').slice(0, 16)}</td>
                    <td className="px-4 py-3">{String(triage.NivelSugeridoIA || triage.nivel_sugerido_ia || '—')}</td>
                    <td className="px-4 py-3">{String(triage.NivelProfesional || triage.nivel_profesional || '—')}</td>
                    <td className="px-4 py-3">{concordancia ? 'Coincide ✅' : 'Difiere ⚠️'}</td>
                    <td className="px-4 py-3">{String(triage.Estado || triage.estado || '—')}</td>
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
