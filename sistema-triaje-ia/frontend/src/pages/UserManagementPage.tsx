import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi, type UserInfo } from '../api/users'
import { LoadingSpinner, ErrorAlert, EmptyState } from '../components/shared'

export default function UserManagementPage() {
  const qc = useQueryClient()
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.list().then(r => r.data.data),
  })
  const [modal, setModal] = useState<'create' | null>(null)
  const [form, setForm] = useState({ username: '', password: '', email: '', rol: 'Enfermera' })
  const [msg, setMsg] = useState('')
  const [msgType, setMsgType] = useState<'success' | 'error'>('success')
  const [confirmDeactivate, setConfirmDeactivate] = useState<string | null>(null)
  const [resetPassword, setResetPassword] = useState<string | null>(null)
  const [resetCopied, setResetCopied] = useState(false)

  const showMsg = (text: string, type: 'success' | 'error' = 'success') => { setMsg(text); setMsgType(type); setTimeout(() => setMsg(''), 5000) }

  const createMut = useMutation({
    mutationFn: () => usersApi.create(form),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['users'] }); setModal(null); showMsg('Usuario creado exitosamente') },
    onError: (err: unknown) => { const e = err as { response?: { data?: { detail?: string } } }; showMsg(e.response?.data?.detail || 'Error al crear usuario', 'error') },
  })

  const deactivateMut = useMutation({
    mutationFn: (id: string) => usersApi.deactivate(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['users'] }); setConfirmDeactivate(null); showMsg('Usuario desactivado') },
    onError: () => showMsg('Error al desactivar usuario', 'error'),
  })

  const resetPwdMut = useMutation({
    mutationFn: (id: string) => usersApi.resetPassword(id),
    onSuccess: (res) => {
      const pwd = (res.data as { data: { nueva_password: string } }).data.nueva_password
      setResetPassword(pwd)
      qc.invalidateQueries({ queryKey: ['users'] })
    },
    onError: () => showMsg('Error al resetear contraseña', 'error'),
  })

  if (isLoading) return <LoadingSpinner message="Cargando usuarios..." />
  if (isError) return <ErrorAlert error={`Error al cargar usuarios: ${(error as Error)?.message || 'Error desconocido'}`} onRetry={() => refetch()} />

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">👥 Gestión de Usuarios</h1>
          <p className="text-sm text-slate-500">Administración de cuentas del sistema</p>
        </div>
        <button onClick={() => setModal('create')} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">➕ Nuevo</button>
      </div>

      {msg && (
        <div className={`border rounded-lg p-3 text-sm mb-4 ${msgType === 'success' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'}`}>
          {msg}
        </div>
      )}

      {!data?.length ? <EmptyState message="No hay usuarios registrados." /> : (
        <div className="overflow-x-auto">
          <table className="w-full bg-white border border-slate-200 rounded-lg text-sm">
            <caption className="sr-only">Lista de usuarios del sistema</caption>
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase">
                <th scope="col" className="px-4 py-3">Usuario</th><th scope="col" className="px-4 py-3">Email</th><th scope="col" className="px-4 py-3">Rol</th><th scope="col" className="px-4 py-3">Estado</th><th scope="col" className="px-4 py-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {(data || []).map((u: UserInfo) => (
                <tr key={u.IdUsuario} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">{u.NombreUsuario}</td>
                  <td className="px-4 py-3 text-slate-500">{u.Email}</td>
                  <td className="px-4 py-3">{u.Rol}</td>
                  <td className="px-4 py-3">{u.Activo ? '✅ Activo' : '❌ Inactivo'}</td>
                  <td className="px-4 py-3 flex gap-2">
                    {u.Activo && (
                      <>
                        <button onClick={() => u.IdUsuario && resetPwdMut.mutate(u.IdUsuario)} className="text-xs text-amber-600 hover:underline" title="Resetear contraseña">🔑</button>
                        <button onClick={() => u.IdUsuario && setConfirmDeactivate(u.IdUsuario)} className="text-xs text-red-600 hover:underline">Desactivar</button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal: Confirmar desactivación */}
      {confirmDeactivate && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" role="dialog" aria-modal="true" aria-label="Confirmar desactivación">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm space-y-4">
            <h2 className="text-lg font-semibold">¿Desactivar usuario?</h2>
            <p className="text-sm text-slate-500">El usuario no podrá iniciar sesión. Esta acción se puede revertir reactivando al usuario.</p>
            <div className="flex gap-3 pt-2">
              <button onClick={() => setConfirmDeactivate(null)} className="flex-1 py-2 border border-slate-300 rounded-lg text-sm">Cancelar</button>
              <button onClick={() => deactivateMut.mutate(confirmDeactivate)} disabled={deactivateMut.isPending} className="flex-1 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700">
                {deactivateMut.isPending ? 'Desactivando...' : 'Desactivar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Nueva contraseña (con copiar) */}
      {resetPassword && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" role="dialog" aria-modal="true" aria-label="Contraseña reseteada">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm space-y-4">
            <h2 className="text-lg font-semibold">🔑 Contraseña Reseteada</h2>
            <p className="text-sm text-slate-500">La nueva contraseña temporal es:</p>
            <div className="bg-slate-100 rounded-lg p-3 font-mono text-lg text-center select-all">{resetPassword}</div>
            <p className="text-xs text-amber-600">⚠️ Entrega esta contraseña al usuario. Se solicitará cambiarla en el próximo inicio de sesión.</p>
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => { navigator.clipboard.writeText(resetPassword); setResetCopied(true); setTimeout(() => setResetCopied(false), 2000) }}
                className="flex-1 py-2 border border-slate-300 rounded-lg text-sm hover:bg-slate-50"
              >
                {resetCopied ? '✅ Copiado' : '📋 Copiar'}
              </button>
              <button onClick={() => setResetPassword(null)} className="flex-1 py-2 bg-slate-800 text-white rounded-lg text-sm hover:bg-slate-700">Cerrar</button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Crear usuario */}
      {modal === 'create' && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-40" role="dialog" aria-modal="true" aria-label="Nuevo usuario">
          <div className="bg-white rounded-xl p-6 w-full max-w-md space-y-4">
            <h2 className="text-lg font-semibold">Nuevo Usuario</h2>
            {(['username', 'password', 'email'] as const).map((f) => (
              <div key={f}>
                <label className="block text-xs font-medium text-slate-500 mb-1 capitalize">{f}</label>
                <input
                  type={f === 'password' ? 'password' : 'text'}
                  value={form[f]}
                  onChange={e => setForm(p => ({ ...p, [f]: e.target.value }))}
                  className="input w-full"
                  autoComplete={f === 'password' ? 'new-password' : f === 'email' ? 'email' : 'username'}
                />
              </div>
            ))}
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Rol</label>
              <select value={form.rol} onChange={e => setForm(p => ({ ...p, rol: e.target.value }))} className="input w-full">
                {['Administrador', 'Medico', 'Enfermera', 'Investigador', 'Auditor'].map(r => <option key={r}>{r}</option>)}
              </select>
            </div>
            <div className="flex gap-3 pt-2">
              <button onClick={() => setModal(null)} className="flex-1 py-2 border border-slate-300 rounded-lg text-sm">Cancelar</button>
              <button onClick={() => createMut.mutate()} disabled={createMut.isPending} className="flex-1 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
                {createMut.isPending ? 'Creando...' : 'Crear'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
