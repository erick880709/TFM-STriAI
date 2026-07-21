import { useState } from 'react'
import { patientsApi } from '../api/patients'
import type { Patient } from '../types/patient'

interface PatientSearchProps {
  onSelect: (patient: Patient) => void
}

export default function PatientSearch({ onSelect }: PatientSearchProps) {
  const [doc, setDoc] = useState('')
  const [result, setResult] = useState<Patient | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    if (!doc.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await patientsApi.getByDocument(doc.trim())
      setResult(res.data.data)
    } catch {
      setError('Paciente no encontrado')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4">
      <div className="flex gap-3">
        <input
          type="text"
          placeholder="Número de documento"
          value={doc}
          onChange={(e) => setDoc(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
      </div>

      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}

      {result && (
        <div className="mt-3 bg-green-50 border border-green-200 rounded-lg p-3">
          <p className="font-medium text-green-800">
            {result.nombre} {result.apellido}
          </p>
          <p className="text-sm text-green-600">
            Doc: {result.numero_documento} · Edad: {result.edad} · EPS: {result.eps}
          </p>
          <button
            onClick={() => onSelect(result)}
            className="mt-2 text-sm bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
          >
            Seleccionar Paciente
          </button>
        </div>
      )}
    </div>
  )
}
