import api from './client'
import type { ApiResponse, PaginatedResponse } from '../types/api'

export interface AuditEntry {
  IdAuditoria?: string; Usuario?: string; FechaHora?: string
  Accion?: string; EntidadAfectada?: string; Observaciones?: string
}

export const auditApi = {
  query: (params: Record<string, unknown>) =>
    api.get<PaginatedResponse<AuditEntry>>('/audit', { params }),
  getActions: () => api.get<ApiResponse<string[]>>('/audit/actions'),
  getUsers: () => api.get<ApiResponse<string[]>>('/audit/users'),
  exportCsv: (params: Record<string, unknown>) =>
    api.get('/audit/export/csv', { params, responseType: 'blob' }),
}
