import api from './client'
import type { ApiResponse } from '../types/api'

export interface DashboardKPIs {
  total_triages: number; total_pacientes: number; triajes_hoy: number
  tasa_concordancia: number; concordancia_si: number; concordancia_total: number
  tiempo_inferencia_promedio: number; tasa_cierre: number; cerrados: number
  triajes_por_estado: Record<string, number>
  triajes_por_nivel_ia: Record<string, number>
  total_con_ia: number
}

export const dashboardApi = {
  getKpis: () => api.get<ApiResponse<DashboardKPIs>>('/dashboard/kpis'),
  getTriages7d: () => api.get<ApiResponse<{ dia: string; cnt: number }[]>>('/dashboard/triages-7d'),
}
