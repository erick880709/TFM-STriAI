"""
Router de inferencia IA — /api/inference/*
Endpoints: predicción, explicabilidad SHAP, estado del servicio.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.schemas.inference import PredictRequest, PredictResponse, ExplainResponse, InferenceStatus
from app.schemas.common import ApiResponse
from app.middleware.auth import get_current_user, TokenData

router = APIRouter()


def _get_inference(request: Request):
    return request.app.state.inference_service


# ---------------------------------------------------------------------------
# POST /api/inference/predict — Clasificar nivel de triaje
# ---------------------------------------------------------------------------
@router.post("/predict", response_model=PredictResponse)
async def predict(
    body: PredictRequest,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Predice el nivel de triaje usando el modelo IA cargado."""
    inf = _get_inference(request)
    if not inf.model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo IA no cargado",
        )

    clinical_data = {
        "frecuencia_cardiaca": body.frecuencia_cardiaca,
        "frecuencia_respiratoria": body.frecuencia_respiratoria,
        "presion_sistolica": body.presion_sistolica,
        "presion_diastolica": body.presion_diastolica,
        "temperatura": body.temperatura,
        "saturacion_oxigeno": body.saturacion_oxigeno,
        "edad": body.edad,
        "sexo": body.sexo,
    }

    result = inf.predict(clinical_data, body.motivo_texto)
    return PredictResponse(
        nivel_predicho=result["nivel_predicho"],
        nivel_codigo=result["nivel_codigo"],
        probabilidades=result["probabilidades"],
        tiempo_inferencia_ms=result["tiempo_inferencia_ms"],
        modelo_version=result.get("modelo_version", "?"),
        shap_disponible=result.get("shap_disponible", False),
    )


# ---------------------------------------------------------------------------
# POST /api/inference/explain — Explicación SHAP
# ---------------------------------------------------------------------------
@router.post("/explain", response_model=ExplainResponse)
async def explain(
    body: PredictRequest,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Genera explicación SHAP (o feature_importances_) para una predicción."""
    inf = _get_inference(request)
    if not inf.model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo IA no cargado",
        )

    clinical_data = {
        "frecuencia_cardiaca": body.frecuencia_cardiaca,
        "frecuencia_respiratoria": body.frecuencia_respiratoria,
        "presion_sistolica": body.presion_sistolica,
        "presion_diastolica": body.presion_diastolica,
        "temperatura": body.temperatura,
        "saturacion_oxigeno": body.saturacion_oxigeno,
        "edad": body.edad,
        "sexo": body.sexo,
    }

    result = inf.explain(clinical_data, body.motivo_texto)
    return ExplainResponse(
        nivel_predicho=result["nivel_predicho"],
        top_features=result.get("top_features", []),
        shap_disponible=result.get("shap_disponible", False),
        fallback=result.get("fallback", False),
    )


# ---------------------------------------------------------------------------
# GET /api/inference/status — Estado del servicio
# ---------------------------------------------------------------------------
@router.get("/status", response_model=InferenceStatus)
async def inference_status(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Retorna el estado actual del servicio de inferencia."""
    inf = _get_inference(request)
    status_data = inf.get_status()
    return InferenceStatus(
        modelo_cargado=inf.model is not None,
        version=status_data.get("version"),
        nombre=status_data.get("nombre"),
        n_features=status_data.get("n_features"),
        shap_disponible=status_data.get("shap_disponible"),
        thresholds=status_data.get("thresholds"),
    )


# ---------------------------------------------------------------------------
# POST /api/inference/reload — Recargar modelo (admin)
# ---------------------------------------------------------------------------
@router.post("/reload")
async def reload_model(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Recarga el modelo IA desde disco. Requiere rol Administrador."""
    if current_user.rol != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores")
    inf = _get_inference(request)
    ok = inf.load_model()
    return ApiResponse(data={"cargado": ok}, message="Modelo recargado" if ok else "Error al recargar")
