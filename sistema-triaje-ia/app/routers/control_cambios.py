"""
Router de control de cambios — /api/control-cambios/*
Endpoints: consulta y registro de cambios sobre datos de pacientes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.schemas.common import ApiResponse
from app.middleware.auth import get_current_user, TokenData
from app.services.patient_service import PatientService

router = APIRouter()


def _get_patient_service(request: Request) -> PatientService:
    if not hasattr(request.app.state, "patient_service"):
        request.app.state.patient_service = PatientService(request.app.state.db_path)
    return request.app.state.patient_service


# ---------------------------------------------------------------------------
# GET /api/control-cambios — Historial de cambios
# ---------------------------------------------------------------------------
@router.get("")
async def get_control_cambios(
    documento: str = Query("", description="Filtrar por documento de paciente"),
    request: Request = None,
    current_user: TokenData = Depends(get_current_user),
):
    """Obtiene el historial de cambios, opcionalmente filtrado por paciente."""
    svc = _get_patient_service(request)
    cambios = svc.get_historial_cambios(documento=documento if documento else None)
    return ApiResponse(data=cambios)


# ---------------------------------------------------------------------------
# POST /api/control-cambios — Registrar cambio
# ---------------------------------------------------------------------------
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_control_cambio(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    id_paciente: int = None,
    campo: str = None,
    valor_anterior: str = None,
    valor_nuevo: str = None,
):
    """
    Registra un cambio en los datos de un paciente.
    Los parámetros se pasan como query parameters para simplificar.
    """
    if not id_paciente or not campo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="id_paciente y campo son obligatorios",
        )
    svc = _get_patient_service(request)
    id_cambio = svc.registrar_cambio(
        id_paciente=str(id_paciente),
        usuario=current_user.username,
        campo=campo,
        valor_anterior=valor_anterior or "",
        valor_nuevo=valor_nuevo or "",
    )
    return ApiResponse(data={"id_cambio": id_cambio}, message="Cambio registrado")
