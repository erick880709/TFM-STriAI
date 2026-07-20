"""
Decorador de auditoría (TT-E5-01).
Se implementará completamente en Épica 5.
Por ahora, stub que permite que el resto del código compile.
"""
import functools
import logging

logger = logging.getLogger(__name__)


def auditar(accion: str):
    """
    Decorador que registra automáticamente una acción en la tabla de auditoría.
    En Épica 5 se conectará a AuditService para persistencia real.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"[AUDIT] {accion}")
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
