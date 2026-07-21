import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { LogOut, Stethoscope, Activity, ClipboardCheck, Brain, CheckCircle, LayoutDashboard, Cpu, GitCompare, Shield, Users, FileText, Clock } from 'lucide-react'

const menuItems = [
  { group: '📋 Flujo Clínico', items: [
    { to: '/pacientes', label: 'Registrar Paciente', icon: Stethoscope, perm: 'RegistroPaciente' },
    { to: '/signos-vitales', label: 'Signos Vitales', icon: Activity, perm: 'SignosVitales' },
    { to: '/evaluacion-clinica', label: 'Evaluación Clínica', icon: ClipboardCheck, perm: 'EvaluacionClinica' },
    { to: '/clasificacion-ia', label: 'Clasificación IA', icon: Brain, perm: 'ClasificacionIA' },
    { to: '/validacion', label: 'Validación y Cierre', icon: CheckCircle, perm: 'ClasificacionIA' },
  ]},
  { group: '📊 Soporte', items: [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, perm: 'Dashboard' },
    { to: '/modelos', label: 'Gestión Modelos', icon: Cpu, perm: 'GestionModelos' },
    { to: '/comparar-modelos', label: 'Comparar Modelos', icon: GitCompare, perm: 'ComparacionModelos' },
    { to: '/auditoria', label: 'Auditoría', icon: Shield, perm: 'Auditoria' },
    { to: '/usuarios', label: 'Gestión Usuarios', icon: Users, perm: 'GestionUsuarios' },
    { to: '/control-cambios', label: 'Control de Cambios', icon: FileText, perm: 'Auditoria' },
    { to: '/historico', label: 'Histórico del Paciente', icon: Clock, perm: 'RegistroPaciente' },
  ]},
]

export default function Sidebar() {
  const { user, permissions, logout } = useAuth()

  const hasPermission = (perm: string) => permissions.includes(perm)

  return (
    <aside className="w-64 bg-[#164E63] text-white flex flex-col shrink-0" aria-label="Navegación principal">
      <div className="p-4 border-b border-[#0E7490]">
        <h1 className="text-lg font-bold" style={{fontFamily:'Lexend,system-ui,sans-serif'}}>🏥 Triaje IA</h1>
        <p className="text-xs text-[#22D3EE]">Servicio de Urgencias · Colombia</p>
      </div>

      <nav className="flex-1 overflow-y-auto p-3 space-y-4">
        {menuItems.map((group) => (
          <div key={group.group}>
            <p className="text-xs font-semibold text-[#22D3EE] uppercase tracking-wider mb-2 px-2">
              {group.group}
            </p>
            {group.items.map((item) =>
              hasPermission(item.perm) ? (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                      isActive
                        ? 'bg-[#0891B2] text-white shadow-sm'
                        : 'text-[#CFFAFE] hover:bg-[#0E7490] hover:text-white'
                    }`
                  }
                >
                  <item.icon size={18} />
                  {item.label}
                </NavLink>
              ) : null
            )}
          </div>
        ))}
      </nav>

      <div className="p-3 border-t border-[#0E7490]">
        <div className="flex items-center gap-3 px-3 py-2 text-sm text-[#CFFAFE]">
          <div className="w-8 h-8 rounded-full bg-[#0891B2] flex items-center justify-center text-xs font-bold">
            {user?.username?.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="truncate font-medium">{user?.username}</p>
            <p className="text-xs text-[#22D3EE]">{user?.rol}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-2 w-full mt-2 px-3 py-2 text-sm text-red-300 hover:bg-red-900/30 rounded-lg transition-colors"
        >
          <LogOut size={16} /> Cerrar Sesión
        </button>
      </div>
    </aside>
  )
}
