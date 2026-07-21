import { useAuth } from '../../hooks/useAuth'
import Breadcrumb from './Breadcrumb'

export default function Header() {
  const { user } = useAuth()

  return (
    <header className="h-14 bg-white border-b border-[#CFFAFE] flex items-center px-6 shrink-0 gap-4">
      <Breadcrumb />
      <div className="flex-1" />
      <div className="hidden sm:flex items-center gap-3">
        <span className="text-sm text-[#526771]">{user?.username}</span>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
          user?.rol === 'Administrador' ? 'bg-[#0891B2]/10 text-[#0891B2]' :
          user?.rol === 'Medico' ? 'bg-[#059669]/10 text-[#059669]' :
          'bg-[#526771]/10 text-[#526771]'
        }`}>
          {user?.rol}
        </span>
      </div>
    </header>
  )
}
