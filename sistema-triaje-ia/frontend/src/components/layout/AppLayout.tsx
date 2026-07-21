import { Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import { ErrorBoundary } from '../shared/ErrorBoundary'
import PatientRegistrationPage from '../../pages/PatientRegistrationPage'
import VitalSignsPage from '../../pages/VitalSignsPage'
import ClinicalEvaluationPage from '../../pages/ClinicalEvaluationPage'
import IAClassificationPage from '../../pages/IAClassificationPage'
import TriageValidationPage from '../../pages/TriageValidationPage'
import DashboardPage from '../../pages/DashboardPage'
import ModelManagementPage from '../../pages/ModelManagementPage'
import ModelComparisonPage from '../../pages/ModelComparisonPage'
import AuditPage from '../../pages/AuditPage'
import UserManagementPage from '../../pages/UserManagementPage'
import HistoricoPacientePage from '../../pages/HistoricoPacientePage'
import ControlCambiosPage from '../../pages/ControlCambiosPage'

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Navigate to="/pacientes" replace />} />
              <Route path="/pacientes" element={<PatientRegistrationPage />} />
              <Route path="/signos-vitales" element={<VitalSignsPage />} />
              <Route path="/evaluacion-clinica" element={<ClinicalEvaluationPage />} />
              <Route path="/clasificacion-ia" element={<IAClassificationPage />} />
              <Route path="/validacion" element={<TriageValidationPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/modelos" element={<ModelManagementPage />} />
              <Route path="/comparar-modelos" element={<ModelComparisonPage />} />
              <Route path="/auditoria" element={<AuditPage />} />
              <Route path="/usuarios" element={<UserManagementPage />} />
              <Route path="/historico" element={<HistoricoPacientePage />} />
              <Route path="/control-cambios" element={<ControlCambiosPage />} />
            </Routes>
          </ErrorBoundary>
        </main>
      </div>
    </div>
  )
}
