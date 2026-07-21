export interface User { username: string; rol: 'Administrador' | 'Medico' | 'Enfermera' | 'Investigador' | 'Auditor'; email?: string }
export interface AuthState { user: User | null; token: string | null; permissions: string[]; isAuthenticated: boolean; isAdmin: boolean }
