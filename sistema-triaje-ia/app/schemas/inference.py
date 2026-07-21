"""Schemas de inferencia IA."""
from typing import Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    frecuencia_cardiaca: float
    frecuencia_respiratoria: float
    presion_sistolica: float
    presion_diastolica: float
    temperatura: float
    saturacion_oxigeno: float
    edad: int
    sexo: str
    motivo_texto: str = Field(..., min_length=3, description="Texto libre del motivo de consulta")


class PredictResponse(BaseModel):
    nivel_predicho: str
    nivel_codigo: int
    probabilidades: dict
    tiempo_inferencia_ms: float
    modelo_version: str
    shap_disponible: bool


class ExplainResponse(BaseModel):
    nivel_predicho: str
    top_features: list[dict]
    shap_disponible: bool
    fallback: bool = False


class InferenceStatus(BaseModel):
    modelo_cargado: bool
    version: Optional[str] = None
    nombre: Optional[str] = None
    n_features: Optional[int] = None
    shap_disponible: Optional[bool] = None
    thresholds: Optional[dict] = None
