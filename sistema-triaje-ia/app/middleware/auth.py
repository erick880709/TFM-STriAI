"""
Middleware de autenticación JWT para FastAPI.
Provee la dependencia get_current_user y require_role.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config.settings import load_config
from app.schemas.auth import TokenData

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un JWT con claims {sub, rol, exp}."""
    cfg = load_config()
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=cfg["jwt_expiration_minutes"])
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, cfg["jwt_secret"], algorithm=cfg["jwt_algorithm"])


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decodifica y valida un JWT. Retorna None si es inválido o expirado."""
    cfg = load_config()
    try:
        payload = jwt.decode(token, cfg["jwt_secret"], algorithms=[cfg["jwt_algorithm"]])
        username: str = payload.get("sub")
        rol: str = payload.get("rol")
        exp: int = payload.get("exp")
        if username is None or rol is None:
            return None
        return TokenData(username=username, rol=rol, exp=exp)
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Dependencia de FastAPI que extrae y valida el JWT del header Authorization.
    Lanza HTTPException(401) si el token es inválido o expirado.
    """
    token_data = decode_access_token(credentials.credentials)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


def require_role(rol_requerido: str):
    """
    Factory de dependencia que verifica que el usuario tenga un rol específico.
    Usar como: Depends(require_role("Administrador"))
    """
    async def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.rol != rol_requerido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere rol '{rol_requerido}'",
            )
        return current_user
    return role_checker
