import api from './client'
import type { ApiResponse } from '../types/api'

export interface ModelInfo {
  IdModelo?: string; Nombre?: string; Version?: string; Estado?: string
  Arquitectura?: string; F1Score?: number; AUCROC?: number
  FechaRegistro?: string
}

export interface DiskModel {
  nombre: string; version: string; directorio: string
  f1_macro?: number; auc_roc?: number; n_features?: number
  shap_disponible?: boolean; tamano_mb?: number; metadata?: Record<string, unknown>
}

export const modelsApi = {
  list: () => api.get<ApiResponse<ModelInfo[]>>('/models'),
  register: (data: Record<string, unknown>) =>
    api.post<ApiResponse<ModelInfo>>('/models', null, { params: data }),
  activate: (id: string) => api.patch<ApiResponse<ModelInfo>>(`/models/${id}`),
  scanDisk: () => api.get<ApiResponse<DiskModel[]>>('/models/scan'),
}
