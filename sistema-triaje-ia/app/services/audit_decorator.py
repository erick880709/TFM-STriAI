"""
Decorador de auditoría (TT-E5-01).
Conectado a AuditService para persistencia real.

Uso en Streamlit (contexto actual):
    from app.services.audit_decorator import auditar
    from app.services.audit_service import AuditService

    audit_svc = AuditService(db_path)

    @auditar("crear_paciente", audit_service=audit_svc)
    def crear_paciente(datos): ...

Uso futuro en FastAPI:
    Se reemplazará por un middleware que registre automáticamente cada request.
"""
import functools
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


def auditar(
    accion: str,
    audit_service=None,
    entidad: Optional[str] = None,
    get_usuario: Optional[Callable[[], str]] = None,
):
    """
    Decorador que registra automáticamente una acción en la tabla de auditoría.

    Args:
        accion: nombre de la acción (ej. "crear_paciente", "cerrar_triaje").
        audit_service: instancia de AuditService. Si es None, solo loguea.
        entidad: nombre de la entidad afectada.
        get_usuario: callable que retorna el username del usuario actual.
                      Si es None, intenta obtenerlo de st.session_state.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Intentar resolver el usuario
            usuario = "sistema"
            if get_usuario:
                try:
                    usuario = get_usuario()
                except Exception:
                    pass
            else:
                # Fallback: intentar obtener de Streamlit
                try:
                    import streamlit as st
                    u = st.session_state.get("user")
                    if u and isinstance(u, dict):
                        usuario = u.get("nombre_usuario", "sistema")
                except Exception:
                    pass

            # Ejecutar la función original
            result = func(*args, **kwargs)

            # Registrar auditoría
            if audit_service:
                try:
                    audit_service.register(
                        usuario=usuario,
                        accion=accion,
                        entidad=entidad,
                        observaciones=f"Ejecutado: {func.__name__}",
                    )
                except Exception as e:
                    logger.warning(f"No se pudo registrar auditoría: {e}")
            else:
                logger.info(f"[AUDIT] {accion} por {usuario} — AuditService no configurado")

            return result
        return wrapper
    return decorator
