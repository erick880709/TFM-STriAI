"""
Router de usuarios — /api/users/*
Endpoints: CRUD de usuarios (admin).
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.schemas.common import ApiResponse
from app.middleware.auth import get_current_user, TokenData

router = APIRouter()


def _get_auth_service(request: Request):
    return request.app.state.auth_service


@router.get("")
async def list_users(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Lista todos los usuarios (admin)."""
    if current_user.rol != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores")
    auth_svc = _get_auth_service(request)
    users = auth_svc.list_users()
    return ApiResponse(data=users)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    username: str = None,
    password: str = None,
    email: str = None,
    rol: str = "Enfermera",
):
    """Crea un nuevo usuario (admin)."""
    if current_user.rol != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores")
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username y password son obligatorios")
    auth_svc = _get_auth_service(request)
    id_usuario = auth_svc.create_user(
        admin_id=current_user.username,
        username=username,
        password=password,
        email=email or "",
        rol=rol,
    )
    return ApiResponse(data={"id": id_usuario}, message="Usuario creado")


@router.patch("/{target_id}")
async def update_user(
    target_id: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    email: str = None,
    rol: str = None,
    activo: bool = None,
):
    """Actualiza un usuario (admin)."""
    if current_user.rol != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores")
    auth_svc = _get_auth_service(request)
    ok = auth_svc.update_user(
        admin_id=current_user.username,
        target_id=target_id,
        email=email,
        rol=rol,
        activo=activo,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return ApiResponse(message="Usuario actualizado")


@router.delete("/{target_id}")
async def deactivate_user(
    target_id: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Desactiva un usuario — soft delete (admin)."""
    if current_user.rol != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores")
    auth_svc = _get_auth_service(request)
    ok = auth_svc.deactivate_user(admin_id=current_user.username, target_id=target_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return ApiResponse(message="Usuario desactivado")


@router.post("/{target_id}/reset-password")
async def reset_password(
    target_id: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Resetea la contraseña de un usuario (admin)."""
    if current_user.rol != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores")
    auth_svc = _get_auth_service(request)
    new_pwd = auth_svc.reset_password(admin_id=current_user.username, target_id=target_id)
    if new_pwd is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return ApiResponse(data={"nueva_password": new_pwd}, message="Contraseña reseteada")
