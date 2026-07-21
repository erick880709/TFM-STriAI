import { NavLink, useLocation } from 'react-router-dom'
import { Stethoscope, Activity, Brain, LayoutDashboard, Menu } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { useState } from 'react'

const mobileNav = [
  { to: '/pacientes', label: 'Paciente', icon: Stethoscope, step: 1 },
  { to: '/signos-vitales', label: 'Vitales', icon: Activity, step: 2 },
  { to: '/clasificacion-ia', label: 'IA', icon: Brain, step: 4 },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
]

export default function BottomNav() {
  const { permissions } = useAuth()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  const hasPermission = (perm: string) => permissions.includes(perm)
  // Clinical items need their respective permissions
  const permMap: Record<string, string> = {
    '/pacientes': 'RegistroPaciente',
    '/signos-vitales': 'SignosVitales',
    '/clasificacion-ia': 'ClasificacionIA',
    '/dashboard': 'Dashboard',
  }

  return (
    <>
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-[#0A4C5C] border-t border-[#0E6B7A] flex items-center justify-around z-40 safe-area-bottom"
           aria-label="Navegación móvil">
        {mobileNav.map((item) => {
          if (!hasPermission(permMap[item.to])) return null
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 py-2 px-3 text-xs transition-colors min-w-[64px] ${
                  isActive ? 'text-[#22D3EE]' : 'text-[#CFFAFE]/70'
                }`
              }
              style={{ minHeight: '56px', justifyContent: 'center' }}
            >
              {item.step ? (
                <span className={`flex items-center justify-center rounded-full text-xs font-bold w-6 h-6 ${
                  location.pathname === item.to ? 'bg-[#22D3EE] text-[#0A4C5C]' : 'bg-white/20 text-white'
                }`}>
                  {item.step}
                </span>
              ) : (
                <item.icon size={20} />
              )}
              <span>{item.label}</span>
            </NavLink>
          )
        })}
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="flex flex-col items-center gap-0.5 py-2 px-3 text-xs text-[#CFFAFE]/70 min-w-[64px]"
          style={{ minHeight: '56px', justifyContent: 'center' }}
          aria-label="Menú"
        >
          <Menu size={20} />
          <span>Más</span>
        </button>
      </nav>

      {/* Mobile overflow menu */}
      {menuOpen && (
        <div className="md:hidden fixed inset-0 bg-black/40 z-50 flex items-end" onClick={() => setMenuOpen(false)}>
          <div className="bg-[#0A4C5C] rounded-t-2xl w-full p-5 space-y-2 animate-slide-up" onClick={e => e.stopPropagation()}>
            <div className="w-10 h-1 bg-white/30 rounded-full mx-auto mb-3" />
            <div className="grid grid-cols-3 gap-3">
              {[
                { to: '/evaluacion-clinica', label: 'Eval. Clínica', step: 3, perm: 'EvaluacionClinica' },
                { to: '/validacion', label: 'Validación', step: 5, perm: 'ClasificacionIA' },
                { to: '/modelos', label: 'Modelos', perm: 'GestionModelos' },
                { to: '/comparar-modelos', label: 'Comparar', perm: 'ComparacionModelos' },
                { to: '/auditoria', label: 'Auditoría', perm: 'Auditoria' },
                { to: '/usuarios', label: 'Usuarios', perm: 'GestionUsuarios' },
                { to: '/control-cambios', label: 'Cambios', perm: 'Auditoria' },
                { to: '/historico', label: 'Histórico', perm: 'RegistroPaciente' },
              ].filter(i => hasPermission(i.perm)).map(item => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setMenuOpen(false)}
                  className={({ isActive }) =>
                    `flex flex-col items-center gap-1 p-3 rounded-lg text-xs transition-colors ${
                      isActive ? 'bg-[#0891B2] text-white' : 'text-[#CFFAFE] hover:bg-white/10'
                    }`
                  }
                >
                  {item.step ? (
                    <span className="flex items-center justify-center rounded-full text-xs font-bold w-7 h-7 bg-white/20">
                      {item.step}
                    </span>
                  ) : (
                    <span className="text-lg">📋</span>
                  )}
                  <span className="text-center leading-tight">{item.label}</span>
                </NavLink>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
