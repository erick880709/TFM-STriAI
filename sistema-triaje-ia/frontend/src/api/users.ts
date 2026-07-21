import api from './client'
import type { ApiResponse } from '../types/api'

export interface UserInfo {
  IdUsuario?: string; NombreUsuario?: string; Email?: string
  Rol?: string; Activo?: boolean; UltimoAcceso?: string
}

export const usersApi = {
  list: () => api.get<ApiResponse<UserInfo[]>>('/users'),
  create: (params: Record<string, unknown>) =>
    api.post<ApiResponse<{ id: string }>>('/users', null, { params }),
  update: (id: string, params: Record<string, unknown>) =>
    api.patch<ApiResponse<unknown>>(`/users/${id}`, null, { params }),
  deactivate: (id: string) => api.delete<ApiResponse<unknown>>(`/users/${id}`),
  resetPassword: (id: string) =>
    api.post<ApiResponse<{ nueva_password: string }>>(`/users/${id}/reset-password`),
}
