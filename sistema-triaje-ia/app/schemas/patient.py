"""Schemas de pacientes."""
from typing import Optional
from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    tipo_documento: str = Field(..., description="CC, CE, TI, PA, RC")
    numero_documento: str = Field(..., min_length=3, max_length=20)
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    fecha_nacimiento: str = Field(..., description="YYYY-MM-DD")
    sexo: str = Field(..., description="M o F")
    grupo_sanguineo: str = Field(..., description="A+, A-, B+, B-, AB+, AB-, O+, O-")
    alergias: Optional[str] = None
    eps: str
    via_llegada: Optional[str] = "Caminando"
    departamento: Optional[str] = None
    municipio: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None


class PatientResponse(BaseModel):
    id_paciente: int
    tipo_documento: str
    numero_documento: str
    nombre: str
    apellido: str
    fecha_nacimiento: str
    sexo: str
    grupo_sanguineo: str
    alergias: Optional[str] = None
    eps: str
    via_llegada: Optional[str] = None
    departamento: Optional[str] = None
    municipio: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    edad: Optional[int] = None
    episodios_previos: Optional[int] = None
