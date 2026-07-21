"""Schemas comunes reutilizables en toda la API."""
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Envoltura genérica para respuestas exitosas."""
    success: bool = True
    data: T
    message: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada genérica."""
    items: list[T]
    total: int
    page: int
    limit: int
    pages: int


class ErrorResponse(BaseModel):
    """Estructura estándar de error."""
    success: bool = False
    error: str
    detail: Optional[str] = None
