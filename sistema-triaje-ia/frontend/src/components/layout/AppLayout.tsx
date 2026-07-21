import { Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

// Lazy-loaded pages (se irán agregando)
import LoginPage from '../../pages/LoginPage'

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/pacientes" replace />} />
            {/* Las rutas se irán agregando en HU-03 a HU-14 */}
          </Routes>
        </main>
      </div>
    </div>
  )
}
