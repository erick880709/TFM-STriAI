import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useNavigate, Link } from 'react-router-dom'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPwd, setShowPwd] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    const ok = await login(username, password)
    setLoading(false)
    if (ok) {
      navigate('/')
    } else {
      setError('Usuario o contraseña inválidos')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#ECFEFF]">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-md border border-[#CFFAFE]">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-[#164E63]" style={{fontFamily:'Lexend,system-ui,sans-serif'}}>🏥 Triaje IA</h1>
          <p className="text-sm text-[#64748B] mt-1">Servicio de Urgencias · Colombia</p>
        </div>

        <h2 className="text-lg font-semibold text-[#164E63] mb-4 text-center" style={{fontFamily:'Lexend,system-ui,sans-serif'}}>
          Sistema de Triaje IA
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[#164E63] mb-1">Usuario</label>
            <input
              type="text"
              placeholder="usuario@hospital.gov.co"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-[#A5F3FC] rounded-lg focus:ring-2 focus:ring-[#0891B2] focus:border-[#0891B2] outline-none"
              autoComplete="username"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#164E63] mb-1">Contraseña</label>
            <div className="relative">
              <input
                type={showPwd ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-[#A5F3FC] rounded-lg focus:ring-2 focus:ring-[#0891B2] focus:border-[#0891B2] outline-none pr-10"
                autoComplete="current-password"
                onKeyDown={(e) => { if (e.key === 'Enter') handleSubmit(e) }}
                required
              />
              <button
                type="button"
                onClick={() => setShowPwd(!showPwd)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-[#475569] hover:text-[#164E63]"
                aria-label={showPwd ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {showPwd ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-600 text-sm text-center">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#0891B2] text-white py-2.5 rounded-lg font-medium hover:bg-[#0E7490] transition-colors disabled:opacity-50"
            style={{minHeight:'44px'}}
          >
            {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </button>
        </form>

        <p className="text-center mt-4">
          <Link to="/reset-password" className="text-sm text-[#0891B2] hover:underline">
            ¿Olvidaste tu contraseña?
          </Link>
        </p>

        <p className="text-center text-xs text-[#475569] mt-6">
          Hospital Universitario · Colombia
        </p>
      </div>
    </div>
  )
}
