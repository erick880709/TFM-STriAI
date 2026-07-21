"""
Router de autenticación — /api/auth/*
Endpoints: login, logout, permisos, reset password.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.schemas.auth import (
    LoginRequest, LoginResponse, ResetTokenRequest, ResetPasswordRequest,
)
from app.schemas.common import ApiResponse
from app.middleware.auth import create_access_token, get_current_user, TokenData

router = APIRouter()


def _get_auth_service(request: Request):
    return request.app.state.auth_service


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------
@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, request: Request):
    """Autentica al usuario y retorna un JWT."""
    auth_svc = _get_auth_service(request)
    user = auth_svc.authenticate(body.username, body.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña inválidos",
        )

    # Generar JWT
    token = create_access_token(
        data={"sub": user["nombre_usuario"], "rol": user["rol"]}
    )

    # Permisos según rol
    permissions = auth_svc.get_allowed_pages(user["rol"])

    return LoginResponse(
        access_token=token,
        user={
            "username": user["nombre_usuario"],
            "rol": user["rol"],
            "email": user.get("email"),
        },
        permissions=permissions,
    )


# ---------------------------------------------------------------------------
# POST /api/auth/logout
# ---------------------------------------------------------------------------
@router.post("/logout")
async def logout(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Cierra la sesión. El frontend debe descartar el token."""
    auth_svc = _get_auth_service(request)
    auth_svc.logout()
    return ApiResponse(data={}, message="Sesión cerrada")


# ---------------------------------------------------------------------------
# GET /api/auth/permissions
# ---------------------------------------------------------------------------
@router.get("/permissions")
async def get_permissions(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Retorna las páginas permitidas para el rol del usuario autenticado."""
    auth_svc = _get_auth_service(request)
    pages = auth_svc.get_allowed_pages(current_user.rol)
    return ApiResponse(data={"pages": pages})


# ---------------------------------------------------------------------------
# POST /api/auth/reset-token
# ---------------------------------------------------------------------------
@router.post("/reset-token")
async def request_reset_token(body: ResetTokenRequest, request: Request):
    """Solicita un token de recuperación de contraseña."""
    auth_svc = _get_auth_service(request)
    result = auth_svc.generate_reset_token(body.username_or_email)
    # Siempre retornar éxito para no revelar si el usuario existe
    return ApiResponse(message="Si el usuario existe, recibirás instrucciones por correo.")


# ---------------------------------------------------------------------------
# POST /api/auth/reset-password
# ---------------------------------------------------------------------------
@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, request: Request):
    """Restablece la contraseña usando un token de recuperación."""
    auth_svc = _get_auth_service(request)
    ok = auth_svc.reset_password(body.token, body.new_password)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado",
        )
    return ApiResponse(message="Contraseña actualizada exitosamente")
