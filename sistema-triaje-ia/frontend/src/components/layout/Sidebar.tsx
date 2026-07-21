import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { LogOut, Stethoscope, Activity, ClipboardCheck, Brain, CheckCircle, LayoutDashboard, Cpu, GitCompare, Shield, Users, FileText, Clock, ChevronLeft, ChevronRight } from 'lucide-react'
import { useState } from 'react'

const menuItems = [
  { group: '📋 Flujo Clínico', items: [
    { to: '/pacientes', label: 'Registrar Paciente', icon: Stethoscope, perm: 'RegistroPaciente', step: 1 },
    { to: '/signos-vitales', label: 'Signos Vitales', icon: Activity, perm: 'SignosVitales', step: 2 },
    { to: '/evaluacion-clinica', label: 'Evaluación Clínica', icon: ClipboardCheck, perm: 'EvaluacionClinica', step: 3 },
    { to: '/clasificacion-ia', label: 'Clasificación IA', icon: Brain, perm: 'ClasificacionIA', step: 4 },
    { to: '/validacion', label: 'Validación y Cierre', icon: CheckCircle, perm: 'ClasificacionIA', step: 5 },
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
  const [collapsed, setCollapsed] = useState(false)

  const hasPermission = (perm: string) => permissions.includes(perm)

  return (
    <aside className={`${collapsed ? 'w-14' : 'w-60'} bg-[#0A4C5C] text-white flex flex-col shrink-0 transition-all duration-200`} aria-label="Navegación principal">
      <div className={`p-4 border-b border-[#0E6B7A] flex items-center ${collapsed ? 'justify-center' : 'justify-between'}`}>
        {!collapsed && (
          <div>
            <h1 className="text-lg font-bold" style={{fontFamily:'Lexend,system-ui,sans-serif'}}>STriAI</h1>
            <p className="text-xs text-[#22D3EE]">Triaje Multimodal IA</p>
          </div>
        )}
        <button onClick={() => setCollapsed(!collapsed)} className="text-[#22D3EE] hover:text-white rounded" aria-label={collapsed ? 'Expandir menú' : 'Colapsar menú'} style={{minHeight:'44px', minWidth:'44px', display:'flex', alignItems:'center', justifyContent:'center'}}>
          {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto p-3 space-y-4">
        {menuItems.map((group) => (
          <div key={group.group}>
            {!collapsed && (
              <p className="text-xs font-semibold text-[#22D3EE] uppercase tracking-wider mb-2 px-2">
                {group.group}
              </p>
            )}
            {group.items.map((item) =>
              hasPermission(item.perm) ? (
                <NavLink
                  key={item.to}
                  to={item.to}
                  title={collapsed ? item.label : undefined}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                      isActive
                        ? 'bg-[#0891B2] text-white shadow-sm'
                        : 'text-[#CFFAFE] hover:bg-[#0E6B7A] hover:text-white'
                    } ${collapsed ? 'justify-center' : ''}`
                  }
                  style={{minHeight:'44px'}}
                >
                  {'step' in item ? (
                    <span className={`flex items-center justify-center rounded-full text-xs font-bold shrink-0 ${
                      collapsed ? 'w-7 h-7 text-sm' : 'w-6 h-6'
                    } bg-white/20`}>
                      {(item as typeof item & { step: number }).step}
                    </span>
                  ) : (
                    <item.icon size={collapsed ? 22 : 18} />
                  )}
                  {!collapsed && <span>{item.label}</span>}
                </NavLink>
              ) : null
            )}
          </div>
        ))}
      </nav>

      <div className="p-3 border-t border-[#0E6B7A]">
        <div className={`flex items-center gap-3 ${collapsed ? 'justify-center' : 'px-3'} py-2 text-sm text-[#CFFAFE]`}>
          <div className="w-8 h-8 rounded-full bg-[#0891B2] flex items-center justify-center text-xs font-bold shrink-0">
            {user?.username?.charAt(0).toUpperCase()}
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="truncate font-medium">{user?.username}</p>
              <p className="text-xs text-[#22D3EE]">{user?.rol}</p>
            </div>
          )}
        </div>
        <button
          onClick={logout}
          className={`flex items-center gap-2 w-full mt-2 px-3 py-2 text-sm text-red-300 hover:bg-red-900/30 rounded-lg transition-colors ${collapsed ? 'justify-center' : ''}`}
          style={{minHeight:'44px'}}
          title="Cerrar sesión"
        >
          <LogOut size={16} /> {!collapsed && 'Cerrar Sesión'}
        </button>
      </div>
    </aside>
  )
}
