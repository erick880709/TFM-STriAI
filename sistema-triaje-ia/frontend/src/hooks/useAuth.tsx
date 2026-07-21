import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import { authApi } from '../api/auth'
import type { AuthState, User } from '../types/user'

const AuthContext = createContext<AuthState & {
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
} | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    const permissionsStr = localStorage.getItem('permissions')
    const user = userStr ? JSON.parse(userStr) : null
    const permissions = permissionsStr ? JSON.parse(permissionsStr) : []
    return {
      user,
      token,
      permissions,
      isAuthenticated: !!token && !!user,
      isAdmin: user?.rol === 'Administrador',
    }
  })

  const login = useCallback(async (username: string, password: string): Promise<boolean> => {
    try {
      const res = await authApi.login(username, password)
      const { access_token, user: apiUser, permissions } = res.data
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(apiUser))
      localStorage.setItem('permissions', JSON.stringify(permissions))
      setState({
        user: { username: apiUser.username, rol: apiUser.rol as User['rol'], email: apiUser.email },
        token: access_token,
        permissions,
        isAuthenticated: true,
        isAdmin: apiUser.rol === 'Administrador',
      })
      return true
    } catch {
      return false
    }
  }, [])

  const logout = useCallback(() => {
    authApi.logout().catch(() => {})
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('permissions')
    setState({
      user: null, token: null, permissions: [],
      isAuthenticated: false, isAdmin: false,
    })
  }, [])

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
