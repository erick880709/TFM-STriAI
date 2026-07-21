import { useAuth } from '../../hooks/useAuth'

export default function Header() {
  const { user } = useAuth()

  return (
    <header className="h-14 bg-white border-b border-slate-200 flex items-center px-6 shrink-0">
      <div className="flex-1" />
      <div className="flex items-center gap-3">
        <span className="text-sm text-slate-600">{user?.username}</span>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
          user?.rol === 'Administrador' ? 'bg-purple-100 text-purple-700' :
          user?.rol === 'Medico' ? 'bg-blue-100 text-blue-700' :
          'bg-green-100 text-green-700'
        }`}>
          {user?.rol}
        </span>
      </div>
    </header>
  )
}
