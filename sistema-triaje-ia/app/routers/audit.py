"""
Router de auditoría — /api/audit/*
Endpoints: consulta paginada, filtros, exportación CSV.
"""
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
import io

from app.schemas.common import ApiResponse, PaginatedResponse
from app.middleware.auth import get_current_user, TokenData
from app.services.audit_service import AuditService

router = APIRouter()


def _get_audit_service(request: Request) -> AuditService:
    if not hasattr(request.app.state, "audit_service"):
        request.app.state.audit_service = AuditService(request.app.state.db_path)
    return request.app.state.audit_service


@router.get("")
async def query_audit(
    fecha_desde: str = Query("", description="YYYY-MM-DD"),
    fecha_hasta: str = Query("", description="YYYY-MM-DD"),
    accion: str = Query("", description="Acción a filtrar"),
    entidad: str = Query("", description="Entidad afectada"),
    usuario: str = Query("", description="Usuario que ejecutó la acción"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    request: Request = None,
    current_user: TokenData = Depends(get_current_user),
):
    """Consulta paginada del registro de auditoría con filtros."""
    svc = _get_audit_service(request)
    resultados, total = svc.query(
        fecha_desde=fecha_desde if fecha_desde else None,
        fecha_hasta=fecha_hasta if fecha_hasta else None,
        accion=accion if accion else None,
        entidad=entidad if entidad else None,
        usuario=usuario if usuario else None,
        page=page,
        limit=limit,
    )
    pages = (total + limit - 1) // limit if total > 0 else 1
    return PaginatedResponse(
        items=resultados, total=total, page=page, limit=limit, pages=pages
    )


@router.get("/actions")
async def get_actions(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Lista las acciones auditables disponibles."""
    svc = _get_audit_service(request)
    acciones = svc.get_acciones_disponibles()
    return ApiResponse(data=acciones)


@router.get("/users")
async def get_audited_users(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Lista los usuarios que han generado registros de auditoría."""
    svc = _get_audit_service(request)
    users = svc.get_usuarios_auditados()
    return ApiResponse(data=users)


@router.get("/export/csv")
async def export_csv(
    fecha_desde: str = Query(""),
    fecha_hasta: str = Query(""),
    accion: str = Query(""),
    entidad: str = Query(""),
    usuario: str = Query(""),
    request: Request = None,
    current_user: TokenData = Depends(get_current_user),
):
    """Exporta los resultados de auditoría como archivo CSV."""
    svc = _get_audit_service(request)
    resultados, _ = svc.query(
        fecha_desde=fecha_desde if fecha_desde else None,
        fecha_hasta=fecha_hasta if fecha_hasta else None,
        accion=accion if accion else None,
        entidad=entidad if entidad else None,
        usuario=usuario if usuario else None,
        page=1,
        limit=10000,
    )
    csv_content = svc.export_csv(resultados)
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=auditoria.csv"},
    )
