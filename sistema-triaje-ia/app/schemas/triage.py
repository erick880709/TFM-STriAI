"""Schemas de triajes."""
from typing import Optional
from pydantic import BaseModel, Field


class TriageCreate(BaseModel):
    id_paciente: int
    profesional: str


class VitalSignsUpdate(BaseModel):
    frecuencia_cardiaca: float = Field(..., ge=30, le=250)
    frecuencia_respiratoria: float = Field(..., ge=5, le=60)
    presion_sistolica: float = Field(..., ge=40, le=280)
    presion_diastolica: float = Field(..., ge=20, le=180)
    temperatura: float = Field(..., ge=30.0, le=45.0)
    saturacion_oxigeno: float = Field(..., ge=30, le=100)


class ClinicalEvalUpdate(BaseModel):
    motivo_consulta: str = Field(..., min_length=3)
    categoria_motivo: Optional[str] = None
    glasgow_ocular: int = Field(..., ge=1, le=4)
    glasgow_verbal: int = Field(..., ge=1, le=5)
    glasgow_motora: int = Field(..., ge=1, le=6)
    escala_dolor: int = Field(..., ge=0, le=10)
    nivel_conciencia: str
    comorbilidades: list[str] = []


class StateTransition(BaseModel):
    estado: str
    usuario: str
    motivo: Optional[str] = None


class ReclassifyRequest(BaseModel):
    nivel: str = Field(..., description="I, II, III, IV, V")
    motivo: str
    usuario: str


class CloseRequest(BaseModel):
    nivel_profesional: str = Field(..., description="I, II, III, IV, V")
    usuario: str
    motivo_cierre: Optional[str] = None
