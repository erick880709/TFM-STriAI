import api from './client'
import type { ApiResponse } from '../types/api'

export interface PredictResult {
  nivel_predicho: string
  nivel_codigo: number
  probabilidades: Record<string, number>
  tiempo_inferencia_ms: number
  modelo_version: string
  shap_disponible: boolean
}

export interface ExplainResult {
  nivel_predicho: string
  top_features: { feature: string; importancia: number; direccion: string; valor_paciente?: unknown }[]
  shap_disponible: boolean
  fallback: boolean
}

export interface InferenceStatus {
  modelo_cargado: boolean
  version?: string
  n_features?: number
  shap_disponible?: boolean
  thresholds?: Record<string, number>
}

export const inferenceApi = {
  predict: (data: Record<string, unknown>) =>
    api.post<PredictResult>('/inference/predict', data),

  explain: (data: Record<string, unknown>) =>
    api.post<ExplainResult>('/inference/explain', data),

  status: () =>
    api.get<InferenceStatus>('/inference/status'),

  reload: () =>
    api.post<ApiResponse<{ cargado: boolean }>>('/inference/reload'),
}
