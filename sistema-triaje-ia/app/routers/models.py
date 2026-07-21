"""
Router de modelos IA — /api/models/*
Endpoints: CRUD de modelos registrados y escaneo de disco.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.schemas.common import ApiResponse
from app.middleware.auth import get_current_user, TokenData
from app.services.model_management_service import ModelManagementService

router = APIRouter()


def _get_model_service(request: Request) -> ModelManagementService:
    if not hasattr(request.app.state, "model_mgmt_service"):
        request.app.state.model_mgmt_service = ModelManagementService(request.app.state.db_path)
    return request.app.state.model_mgmt_service


@router.get("")
async def list_models(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Lista todos los modelos registrados en la base de datos."""
    svc = _get_model_service(request)
    modelos = svc.list_models()
    return ApiResponse(data=modelos)


@router.post("", status_code=status.HTTP_201_CREATED)
async def register_model(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    nombre: str = None,
    version: str = None,
    arquitectura: str = "XGBoost",
    algoritmo: str = "Gradient Boosting",
    f1_score: float = None,
    auc_roc: float = None,
):
    """Registra un nuevo modelo en la base de datos (admin)."""
    if current_user.rol != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores")
    if not nombre or not version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="nombre y version son obligatorios")
    svc = _get_model_service(request)
    modelo = svc.register_model(
        nombre=nombre, version=version,
        arquitectura=arquitectura, algoritmo=algoritmo,
        f1_score=f1_score, auc_roc=auc_roc,
    )
    return ApiResponse(data=modelo, message="Modelo registrado")


@router.patch("/{id_modelo}")
async def activate_model(
    id_modelo: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Activa un modelo (admin). Solo uno puede estar activo a la vez."""
    if current_user.rol != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores")
    svc = _get_model_service(request)
    try:
        modelo = svc.activate_model(id_modelo)
        return ApiResponse(data=modelo, message="Modelo activado")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/scan")
async def scan_disk_models(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Escanea el disco en busca de modelos serializados."""
    svc = _get_model_service(request)
    modelos = svc.scan_disk_models()
    return ApiResponse(data=modelos)
