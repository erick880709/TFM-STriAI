import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { patientsApi } from '../api/patients'
import PatientSearch from '../components/clinical/PatientSearch'
import StepIndicator from '../components/clinical/StepIndicator'
import {
  TIPOS_DOCUMENTO, GRUPOS_SANGUINEOS, EPS_COLOMBIA,
  VIAS_LLEGADA, DEPARTAMENTOS_COLOMBIA,
} from '../lib/constants'
import type { Patient } from '../types/patient'

export default function PatientRegistrationPage() {
  const navigate = useNavigate()
  const [tab, setTab] = useState<'new' | 'search'>('new')
  const [form, setForm] = useState({
    tipo_documento: 'CC', numero_documento: '', nombre: '', apellido: '',
    fecha_nacimiento: '', sexo: 'M', grupo_sanguineo: 'O+', alergias: '',
    eps: 'Nueva EPS', via_llegada: 'Caminando', departamento: '', municipio: '',
    telefono: '', correo: '',
  })
  const [error, setError] = useState('')
  const [duplicate, setDuplicate] = useState<Patient | null>(null)

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => patientsApi.create(data),
    onSuccess: (res) => {
      const p = res.data.data as Patient
      localStorage.setItem('active_patient', JSON.stringify(p))
      navigate('/signos-vitales')
    },
    onError: (err: unknown) => {
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } }
      if (axiosErr.response?.status === 409) {
        // Paciente duplicado — buscar y mostrar
        patientsApi.getByDocument(form.numero_documento).then((r) => {
          setDuplicate(r.data.data as Patient)
        }).catch(() => setError('Error al verificar duplicado'))
      } else {
        setError(axiosErr.response?.data?.detail || 'Error al registrar paciente')
      }
    },
  })

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    const required = ['numero_documento', 'nombre', 'apellido', 'fecha_nacimiento', 'eps']
    for (const f of required) {
      if (!form[f as keyof typeof form]) {
        setError(`El campo ${f} es obligatorio`)
        return
      }
    }
    createMutation.mutate(form)
  }

  const handlePatientFound = (patient: Patient) => {
    localStorage.setItem('active_patient', JSON.stringify(patient))
    navigate('/signos-vitales')
  }

  return (
    <div>
      <StepIndicator step={1} label="Flujo Triaje" />
      <h1 className="text-2xl font-bold text-[#164E63] mb-1">📝 Registrar Paciente</h1>
      <p className="text-sm text-[#64748B] mb-6">Registro de nuevo paciente o búsqueda de existente</p>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-[#ECFEFF] rounded-lg p-1 w-fit">
        {(['new', 'search'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              tab === t ? 'bg-white shadow text-[#164E63]' : 'text-[#64748B] hover:text-[#164E63]'
            }`}
          >
            {t === 'new' ? '🆕 Nuevo Paciente' : '🔍 Buscar Paciente'}
          </button>
        ))}
      </div>

      {tab === 'search' ? (
        <div className="max-w-lg">
          <PatientSearch onSelect={handlePatientFound} />
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="max-w-2xl space-y-5">
          {/* Datos básicos */}
          <div className="bg-white border border-[#A5F3FC] rounded-lg p-5">
            <h2 className="font-semibold text-[#164E63] mb-4">Datos Básicos</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Field label="Tipo Doc.">
                <select value={form.tipo_documento} onChange={(e) => handleChange('tipo_documento', e.target.value)}
                  className="input">
                  {TIPOS_DOCUMENTO.map((t) => <option key={t}>{t}</option>)}
                </select>
              </Field>
              <Field label="Número Documento *">
                <input type="text" value={form.numero_documento}
                  onChange={(e) => handleChange('numero_documento', e.target.value)} className="input" required />
              </Field>
              <Field label="Sexo">
                <select value={form.sexo} onChange={(e) => handleChange('sexo', e.target.value)} className="input">
                  <option value="M">Masculino</option>
                  <option value="F">Femenino</option>
                </select>
              </Field>
              <Field label="Nombre *">
                <input type="text" value={form.nombre} onChange={(e) => handleChange('nombre', e.target.value)} className="input" required />
              </Field>
              <Field label="Apellido *">
                <input type="text" value={form.apellido} onChange={(e) => handleChange('apellido', e.target.value)} className="input" required />
              </Field>
              <Field label="Fecha Nacimiento *">
                <input type="date" value={form.fecha_nacimiento} onChange={(e) => handleChange('fecha_nacimiento', e.target.value)} className="input" required />
              </Field>
            </div>
          </div>

          {/* Datos clínicos */}
          <div className="bg-white border border-[#A5F3FC] rounded-lg p-5">
            <h2 className="font-semibold text-[#164E63] mb-4">Datos Clínicos</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Field label="Grupo Sanguíneo">
                <select value={form.grupo_sanguineo} onChange={(e) => handleChange('grupo_sanguineo', e.target.value)} className="input">
                  {GRUPOS_SANGUINEOS.map((g) => <option key={g}>{g}</option>)}
                </select>
              </Field>
              <Field label="EPS *">
                <select value={form.eps} onChange={(e) => handleChange('eps', e.target.value)} className="input" required>
                  {EPS_COLOMBIA.map((e) => <option key={e}>{e}</option>)}
                </select>
              </Field>
              <Field label="Vía de Llegada">
                <select value={form.via_llegada} onChange={(e) => handleChange('via_llegada', e.target.value)} className="input">
                  {VIAS_LLEGADA.map((v) => <option key={v}>{v}</option>)}
                </select>
              </Field>
            </div>
            <div className="mt-4">
              <Field label="Alergias">
                <textarea value={form.alergias} onChange={(e) => handleChange('alergias', e.target.value)}
                  className="input" rows={2} placeholder="Alergias conocidas del paciente..." />
              </Field>
            </div>
          </div>

          {/* Contacto */}
          <div className="bg-white border border-[#A5F3FC] rounded-lg p-5">
            <h2 className="font-semibold text-[#164E63] mb-4">Contacto y Ubicación</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Field label="Departamento">
                <select value={form.departamento} onChange={(e) => handleChange('departamento', e.target.value)} className="input">
                  <option value="">--</option>
                  {DEPARTAMENTOS_COLOMBIA.map((d) => <option key={d}>{d}</option>)}
                </select>
              </Field>
              <Field label="Municipio">
                <input type="text" value={form.municipio} onChange={(e) => handleChange('municipio', e.target.value)} className="input" />
              </Field>
              <Field label="Teléfono">
                <input type="tel" value={form.telefono} onChange={(e) => handleChange('telefono', e.target.value)} className="input" />
              </Field>
              <Field label="Correo Electrónico" className="md:col-span-2">
                <input type="email" value={form.correo} onChange={(e) => handleChange('correo', e.target.value)} className="input" />
              </Field>
            </div>
          </div>

          {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-600 text-sm">{error}</div>}

          {/* Duplicado */}
          {duplicate && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <p className="font-semibold text-amber-800">⚠️ Paciente ya registrado</p>
              <p className="text-sm text-amber-700">
                {duplicate.nombre} {duplicate.apellido} · {duplicate.numero_documento} · {duplicate.episodios_previos ?? 0} episodios previos
              </p>
              <button type="button" onClick={() => handlePatientFound(duplicate)}
                className="mt-2 bg-amber-600 text-white px-4 py-1.5 rounded text-sm hover:bg-amber-700">
                Iniciar Nuevo Triaje
              </button>
            </div>
          )}

          <button type="submit" disabled={createMutation.isPending}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
            {createMutation.isPending ? 'Registrando...' : 'Registrar Paciente e Iniciar Triaje'}
          </button>
        </form>
      )}
    </div>
  )
}

function Field({ label, children, className = '' }: { label: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={className}>
      <label className="block text-xs font-medium text-[#64748B] mb-1">{label}</label>
      {children}
    </div>
  )
}
