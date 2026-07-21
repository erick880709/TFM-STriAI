import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi, type UserInfo } from '../api/users'
import { LoadingSpinner } from '../components/shared'

export default function UserManagementPage() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({ queryKey: ['users'], queryFn: () => usersApi.list().then(r => r.data.data) })
  const [modal, setModal] = useState<'create' | null>(null)
  const [form, setForm] = useState({ username: '', password: '', email: '', rol: 'Enfermera' })
  const [msg, setMsg] = useState('')

  const createMut = useMutation({
    mutationFn: () => usersApi.create(form),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['users'] }); setModal(null); setMsg('Usuario creado') },
  })

  const deactivateMut = useMutation({
    mutationFn: (id: string) => usersApi.deactivate(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['users'] }); setMsg('Usuario desactivado') },
  })

  const resetPwdMut = useMutation({
    mutationFn: (id: string) => usersApi.resetPassword(id),
    onSuccess: (res) => setMsg(`Nueva contraseña: ${(res.data as { data: { nueva_password: string } }).data.nueva_password}`),
  })

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">👥 Gestión de Usuarios</h1>
          <p className="text-sm text-slate-500">Administración de cuentas del sistema</p>
        </div>
        <button onClick={() => setModal('create')} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">➕ Nuevo</button>
      </div>

      {msg && <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-green-700 text-sm mb-4">{msg}</div>}

      {isLoading ? <LoadingSpinner /> : (
        <div className="overflow-x-auto">
          <table className="w-full bg-white border border-slate-200 rounded-lg text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase">
                <th className="px-4 py-3">Usuario</th><th className="px-4 py-3">Email</th><th className="px-4 py-3">Rol</th><th className="px-4 py-3">Estado</th><th className="px-4 py-3">Acciones</th>
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
                        <button onClick={() => u.IdUsuario && resetPwdMut.mutate(u.IdUsuario)} className="text-xs text-amber-600 hover:underline">🔑</button>
                        <button onClick={() => u.IdUsuario && deactivateMut.mutate(u.IdUsuario)} className="text-xs text-red-600 hover:underline">Desactivar</button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal === 'create' && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md space-y-4">
            <h2 className="text-lg font-semibold">Nuevo Usuario</h2>
            {(['username', 'password', 'email'] as const).map((f) => (
              <div key={f}>
                <label className="block text-xs font-medium text-slate-500 mb-1 capitalize">{f}</label>
                <input type={f === 'password' ? 'password' : 'text'} value={form[f]} onChange={e => setForm(p => ({ ...p, [f]: e.target.value }))} className="input w-full" />
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
              <button onClick={() => createMut.mutate()} disabled={createMut.isPending} className="flex-1 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">Crear</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
