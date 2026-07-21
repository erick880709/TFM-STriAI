import { Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import PatientRegistrationPage from '../../pages/PatientRegistrationPage'
import VitalSignsPage from '../../pages/VitalSignsPage'
import ClinicalEvaluationPage from '../../pages/ClinicalEvaluationPage'
import IAClassificationPage from '../../pages/IAClassificationPage'
import TriageValidationPage from '../../pages/TriageValidationPage'

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/pacientes" replace />} />
            <Route path="/pacientes" element={<PatientRegistrationPage />} />
            <Route path="/signos-vitales" element={<VitalSignsPage />} />
            <Route path="/evaluacion-clinica" element={<ClinicalEvaluationPage />} />
            <Route path="/clasificacion-ia" element={<IAClassificationPage />} />
            <Route path="/validacion" element={<TriageValidationPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
