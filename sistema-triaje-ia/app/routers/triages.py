"""
Router de triajes — /api/triages/*
Endpoints: flujo completo de triaje (crear, signos, evaluación, estados, cierre).
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.schemas.triage import (
    TriageCreate, VitalSignsUpdate, ClinicalEvalUpdate,
    StateTransition, ReclassifyRequest, CloseRequest,
)
from app.schemas.common import ApiResponse
from app.middleware.auth import get_current_user, TokenData
from app.services.triage_service import TriageService

router = APIRouter()


def _get_triage_service(request: Request) -> TriageService:
    if not hasattr(request.app.state, "triage_service"):
        request.app.state.triage_service = TriageService(request.app.state.db_path)
    return request.app.state.triage_service


# ---------------------------------------------------------------------------
# POST /api/triages — Crear evento de triaje
# ---------------------------------------------------------------------------
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_triage(
    body: TriageCreate,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Crea un nuevo evento de triaje para un paciente."""
    svc = _get_triage_service(request)
    triaje = svc.create_triage_event(
        id_paciente=str(body.id_paciente),
        profesional=body.profesional or current_user.username,
    )
    return ApiResponse(data=triaje, message="Triaje creado")


# ---------------------------------------------------------------------------
# GET /api/triages/{id} — Obtener triaje completo
# ---------------------------------------------------------------------------
@router.get("/{id_triaje}")
async def get_triage(
    id_triaje: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Obtiene un triaje con todos sus datos relacionados."""
    svc = _get_triage_service(request)
    triaje = svc.get_triage_event(id_triaje)
    if triaje is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Triaje no encontrado")
    return ApiResponse(data=triaje)


# ---------------------------------------------------------------------------
# GET /api/triages — Buscar triajes por documento
# ---------------------------------------------------------------------------
@router.get("")
async def search_triages(
    doc: str = Query("", description="Número de documento del paciente"),
    active_only: bool = Query(False, description="Solo triajes activos"),
    request: Request = None,
    current_user: TokenData = Depends(get_current_user),
):
    """Busca triajes por documento del paciente."""
    svc = _get_triage_service(request)
    if not doc.strip():
        return ApiResponse(data=[])
    # Usar el PatientService para buscar triajes por documento
    from app.services.patient_service import PatientService
    ps = PatientService(request.app.state.db_path)
    if active_only:
        triajes = ps.get_active_triages_by_documento(doc.strip())
    else:
        triajes = ps.search_triages_by_documento(doc.strip())
    return ApiResponse(data=triajes)


# ---------------------------------------------------------------------------
# PUT /api/triages/{id}/vital-signs — Guardar signos vitales
# ---------------------------------------------------------------------------
@router.put("/{id_triaje}/vital-signs")
async def save_vital_signs(
    id_triaje: str,
    body: VitalSignsUpdate,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Guarda o actualiza los signos vitales de un triaje."""
    svc = _get_triage_service(request)
    signos, alertas = svc.save_vital_signs(
        id_triaje=id_triaje,
        frecuencia_cardiaca=body.frecuencia_cardiaca,
        frecuencia_respiratoria=body.frecuencia_respiratoria,
        presion_sistolica=body.presion_sistolica,
        presion_diastolica=body.presion_diastolica,
        temperatura=body.temperatura,
        saturacion_oxigeno=body.saturacion_oxigeno,
    )
    return ApiResponse(data={"signos": signos, "alertas": alertas}, message="Signos vitales guardados")


# ---------------------------------------------------------------------------
# GET /api/triages/{id}/vital-signs — Obtener signos vitales
# ---------------------------------------------------------------------------
@router.get("/{id_triaje}/vital-signs")
async def get_vital_signs(
    id_triaje: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Obtiene los signos vitales registrados de un triaje."""
    svc = _get_triage_service(request)
    signos = svc.get_vital_signs(id_triaje)
    return ApiResponse(data=signos)


# ---------------------------------------------------------------------------
# PUT /api/triages/{id}/clinical-eval — Guardar evaluación clínica
# ---------------------------------------------------------------------------
@router.put("/{id_triaje}/clinical-eval")
async def save_clinical_evaluation(
    id_triaje: str,
    body: ClinicalEvalUpdate,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Guarda o actualiza la evaluación clínica de un triaje."""
    svc = _get_triage_service(request)
    # Calcular Glasgow total (ocular + verbal + motora)
    glasgow_total = body.glasgow_ocular + body.glasgow_verbal + body.glasgow_motora
    # Mapear comorbilidades de lista a booleanos individuales
    comorb = [c.lower() for c in body.comorbilidades]
    evaluacion = svc.save_clinical_evaluation(
        id_triaje=id_triaje,
        motivo_categoria=body.categoria_motivo or "Otro",
        motivo_texto_libre=body.motivo_consulta,
        escala_dolor=body.escala_dolor,
        glasgow=glasgow_total,
        nivel_conciencia=body.nivel_conciencia,
        diabetes="diabetes" in comorb,
        hipertension="hipertension" in comorb or "hta" in comorb,
        enfermedad_renal="irc" in comorb or "enfermedad renal" in comorb or "insuficiencia renal" in comorb,
        embarazo="embarazo" in comorb,
        cancer="cancer" in comorb or "cáncer" in comorb,
        cardiopatias="cardiopatia" in comorb or "cardiopatía" in comorb,
        enfermedad_pulmonar="epoc" in comorb or "enfermedad pulmonar" in comorb,
        cirugias_recientes="cirugia" in comorb or "cirugía" in comorb,
        alergias=body.alergias,
        medicacion_relevante=body.medicacion_relevante,
        observaciones=body.observaciones,
        episodios_previos=body.episodios_previos,
    )
    return ApiResponse(data=evaluacion, message="Evaluación clínica guardada")


# ---------------------------------------------------------------------------
# GET /api/triages/{id}/clinical-eval — Obtener evaluación clínica
# ---------------------------------------------------------------------------
@router.get("/{id_triaje}/clinical-eval")
async def get_clinical_evaluation(
    id_triaje: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Obtiene la evaluación clínica de un triaje."""
    svc = _get_triage_service(request)
    evaluacion = svc.get_clinical_evaluation(id_triaje)
    return ApiResponse(data=evaluacion)


# ---------------------------------------------------------------------------
# PATCH /api/triages/{id}/state — Transicionar estado
# ---------------------------------------------------------------------------
@router.patch("/{id_triaje}/state")
async def transition_state(
    id_triaje: str,
    body: StateTransition,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Transiciona el estado de un triaje (máquina de estados)."""
    svc = _get_triage_service(request)
    triaje = svc.transition_state(
        id_triaje=id_triaje,
        nuevo_estado=body.estado,
        usuario=body.usuario or current_user.username,
        motivo=body.motivo,
    )
    return ApiResponse(data=triaje, message=f"Estado cambiado a {body.estado}")


# ---------------------------------------------------------------------------
# POST /api/triages/{id}/reclassify — Reclasificar manualmente
# ---------------------------------------------------------------------------
@router.post("/{id_triaje}/reclassify")
async def reclassify_triage(
    id_triaje: str,
    body: ReclassifyRequest,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Reclasifica manualmente el nivel de triaje."""
    svc = _get_triage_service(request)
    triaje = svc.reclassify(
        id_triaje=id_triaje,
        nivel=body.nivel,
        motivo=body.motivo,
        usuario=body.usuario or current_user.username,
    )
    return ApiResponse(data=triaje, message=f"Triaje reclasificado a Nivel {body.nivel}")


# ---------------------------------------------------------------------------
# POST /api/triages/{id}/close — Cerrar triaje
# ---------------------------------------------------------------------------
@router.post("/{id_triaje}/close")
async def close_triage(
    id_triaje: str,
    body: CloseRequest,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Cierra un evento de triaje con validación profesional."""
    svc = _get_triage_service(request)
    triaje = svc.close_event(
        id_triaje=id_triaje,
        nivel_profesional=body.nivel_profesional,
        usuario=body.usuario or current_user.username,
        motivo_cierre=body.motivo_cierre,
    )
    return ApiResponse(data=triaje, message="Triaje cerrado exitosamente")
