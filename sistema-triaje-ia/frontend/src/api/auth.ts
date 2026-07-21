import api from './client'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type { User } from '../types/user'

export interface LoginResponse {
  access_token: string
  token_type: string
  user: { username: string; rol: string; email?: string }
  permissions: string[]
}

export const authApi = {
  login: (username: string, password: string) =>
    api.post<LoginResponse>('/auth/login', { username, password }),

  logout: () => api.post('/auth/logout'),

  permissions: () =>
    api.get<ApiResponse<{ pages: string[] }>>('/auth/permissions'),

  resetToken: (username_or_email: string) =>
    api.post('/auth/reset-token', { username_or_email }),

  resetPassword: (token: string, new_password: string) =>
    api.post('/auth/reset-password', { token, new_password }),
}
