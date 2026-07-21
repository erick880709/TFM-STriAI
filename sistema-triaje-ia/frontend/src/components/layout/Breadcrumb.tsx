import { useLocation, Link } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'

const routeLabels: Record<string, string> = {
  '/pacientes': 'Registrar Paciente',
  '/signos-vitales': 'Signos Vitales',
  '/evaluacion-clinica': 'Evaluación Clínica',
  '/clasificacion-ia': 'Clasificación IA',
  '/validacion': 'Validación y Cierre',
  '/dashboard': 'Dashboard',
  '/modelos': 'Gestión Modelos IA',
  '/comparar-modelos': 'Comparar Modelos',
  '/auditoria': 'Auditoría',
  '/usuarios': 'Gestión Usuarios',
  '/control-cambios': 'Control de Cambios',
  '/historico': 'Histórico del Paciente',
}

export default function Breadcrumb() {
  const location = useLocation()
  const pathSegments = location.pathname.split('/').filter(Boolean)
  const currentLabel = routeLabels[location.pathname] || pathSegments[pathSegments.length - 1] || 'Inicio'

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm text-[#526771]">
      <Link to="/" className="hover:text-[#0891B2] transition-colors" title="Inicio">
        <Home size={16} />
      </Link>
      <ChevronRight size={14} className="text-[#A5F3FC]" />
      <span className="text-[#0F3D47] font-medium" style={{ fontFamily: 'Lexend, system-ui, sans-serif' }}>
        {currentLabel}
      </span>
    </nav>
  )
}
