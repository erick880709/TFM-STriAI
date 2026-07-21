import api from './client'
import type { ApiResponse } from '../types/api'
import type { Patient } from '../types/patient'

export const patientsApi = {
  create: (data: Record<string, unknown>) =>
    api.post<ApiResponse<Patient>>('/patients', data),

  getByDocument: (documento: string) =>
    api.get<ApiResponse<Patient>>(`/patients/${documento}`),

  getById: (id: number) =>
    api.get<ApiResponse<Patient>>(`/patients/id/${id}`),

  search: (q: string, tipo_doc = '', limit = 20) =>
    api.get<ApiResponse<Patient[]>>('/patients', { params: { q, tipo_doc, limit } }),

  getTriages: (id: number) =>
    api.get<ApiResponse<unknown[]>>(`/patients/${id}/triages`),

  getActiveTriage: (id: number) =>
    api.get<ApiResponse<unknown>>(`/patients/${id}/active-triage`),

  recountEpisodes: (id: number) =>
    api.post<ApiResponse<{ episodios_previos: number }>>(`/patients/${id}/recount`),
}
