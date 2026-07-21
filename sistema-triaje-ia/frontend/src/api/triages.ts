import api from './client'
import type { ApiResponse } from '../types/api'
import type { Triage, VitalSigns } from '../types/triage'

export const triagesApi = {
  create: (id_paciente: number, profesional: string) =>
    api.post<ApiResponse<Triage>>('/triages', { id_paciente, profesional }),

  getById: (id: string) =>
    api.get<ApiResponse<Triage>>(`/triages/${id}`),

  search: (doc: string, active_only = false) =>
    api.get<ApiResponse<Triage[]>>('/triages', { params: { doc, active_only } }),

  saveVitalSigns: (id: string, data: VitalSigns) =>
    api.put<ApiResponse<unknown>>(`/triages/${id}/vital-signs`, data),

  getVitalSigns: (id: string) =>
    api.get<ApiResponse<unknown>>(`/triages/${id}/vital-signs`),

  saveClinicalEval: (id: string, data: Record<string, unknown>) =>
    api.put<ApiResponse<unknown>>(`/triages/${id}/clinical-eval`, data),

  getClinicalEval: (id: string) =>
    api.get<ApiResponse<unknown>>(`/triages/${id}/clinical-eval`),

  transitionState: (id: string, estado: string, usuario: string, motivo?: string) =>
    api.patch<ApiResponse<Triage>>(`/triages/${id}/state`, { estado, usuario, motivo }),

  reclassify: (id: string, nivel: string, motivo: string, usuario: string) =>
    api.post<ApiResponse<Triage>>(`/triages/${id}/reclassify`, { nivel, motivo, usuario }),

  close: (id: string, nivel_profesional: string, usuario: string, motivo_cierre?: string) =>
    api.post<ApiResponse<Triage>>(`/triages/${id}/close`, { nivel_profesional, usuario, motivo_cierre }),
}
