"""
Router de pacientes — /api/patients/*
Endpoints: CRUD pacientes, búsqueda, histórico, triajes activos.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.schemas.patient import PatientCreate, PatientResponse
from app.schemas.common import ApiResponse
from app.middleware.auth import get_current_user, TokenData
from app.services.patient_service import PatientService, DuplicatePatientError

router = APIRouter()


def _get_patient_service(request: Request) -> PatientService:
    """Obtiene o crea el PatientService desde el estado de la app."""
    if not hasattr(request.app.state, "patient_service"):
        request.app.state.patient_service = PatientService(request.app.state.db_path)
    return request.app.state.patient_service


# ---------------------------------------------------------------------------
# POST /api/patients — Registrar nuevo paciente
# ---------------------------------------------------------------------------
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_patient(
    body: PatientCreate,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Registra un nuevo paciente en el sistema."""
    svc = _get_patient_service(request)
    try:
        paciente = svc.register_patient(
            tipo_documento=body.tipo_documento,
            numero_documento=body.numero_documento,
            nombres=body.nombre,
            apellidos=body.apellido,
            fecha_nacimiento=body.fecha_nacimiento,
            sexo=body.sexo,
            grupo_sanguineo=body.grupo_sanguineo,
            alergias=body.alergias or "",
            eps=body.eps or "",
            via_llegada=body.via_llegada or "Caminando",
            departamento=body.departamento or "",
            ciudad=body.municipio or "",
            telefono=body.telefono or "",
            correo=body.correo,
        )
        return ApiResponse(data=paciente, message="Paciente registrado exitosamente")
    except DuplicatePatientError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


# ---------------------------------------------------------------------------
# GET /api/patients/{documento} — Buscar por número de documento
# ---------------------------------------------------------------------------
@router.get("/{documento}")
async def get_patient_by_document(
    documento: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Obtiene un paciente por su número de documento."""
    svc = _get_patient_service(request)
    paciente = svc.get_patient_by_document(documento)
    if paciente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    return ApiResponse(data=paciente)


# ---------------------------------------------------------------------------
# GET /api/patients/id/{id} — Buscar por ID interno
# ---------------------------------------------------------------------------
@router.get("/id/{id_paciente}")
async def get_patient_by_id(
    id_paciente: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Obtiene un paciente por su ID interno."""
    svc = _get_patient_service(request)
    paciente = svc.get_patient_by_id(id_paciente)
    if paciente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    return ApiResponse(data=paciente)


# ---------------------------------------------------------------------------
# GET /api/patients — Búsqueda textual con filtros
# ---------------------------------------------------------------------------
@router.get("")
async def search_patients(
    q: str = Query("", description="Texto de búsqueda (nombre, apellido o documento)"),
    tipo_doc: str = Query("", description="Filtrar por tipo de documento"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados"),
    request: Request = None,
    current_user: TokenData = Depends(get_current_user),
):
    """Busca pacientes por texto con filtros opcionales."""
    svc = _get_patient_service(request)
    # Si no hay query, retornar lista vacía
    if not q.strip():
        return ApiResponse(data=[])
    resultados = svc.search_patients(query=q.strip(), tipo_documento=tipo_doc if tipo_doc else None, limit=limit)
    return ApiResponse(data=resultados)


# ---------------------------------------------------------------------------
# GET /api/patients/{id}/triages — Histórico de triajes
# ---------------------------------------------------------------------------
@router.get("/{id_paciente}/triages")
async def get_patient_triages(
    id_paciente: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Obtiene el historial completo de triajes de un paciente."""
    svc = _get_patient_service(request)
    triages = svc.get_patient_triage_history(id_paciente)
    return ApiResponse(data=triages)


# ---------------------------------------------------------------------------
# GET /api/patients/{id}/active-triage — Triaje activo
# ---------------------------------------------------------------------------
@router.get("/{id_paciente}/active-triage")
async def get_active_triage(
    id_paciente: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Obtiene el triaje activo de un paciente, si existe."""
    svc = _get_patient_service(request)
    triaje = svc.get_active_triages_by_documento("")
    # Filtrar por id_paciente
    triaje_paciente = [t for t in triaje if t.get("id_paciente") == id_paciente]
    return ApiResponse(data=triaje_paciente[0] if triaje_paciente else None)


# ---------------------------------------------------------------------------
# POST /api/patients/{id}/recount — Recalcular episodios previos
# ---------------------------------------------------------------------------
@router.post("/{id_paciente}/recount")
async def recount_episodes(
    id_paciente: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Recalcula el contador de episodios previos del paciente."""
    svc = _get_patient_service(request)
    total = svc.update_episodios_previos(id_paciente)
    return ApiResponse(data={"episodios_previos": total}, message="Episodios actualizados")
