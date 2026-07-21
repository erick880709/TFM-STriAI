"""
Router de dashboard — /api/dashboard/*
Endpoints: KPIs operacionales y tendencia de triajes.
"""
from fastapi import APIRouter, Depends, Request

from app.schemas.common import ApiResponse
from app.middleware.auth import get_current_user, TokenData
from app.services.dashboard_service import DashboardService

router = APIRouter()


def _get_dashboard_service(request: Request) -> DashboardService:
    if not hasattr(request.app.state, "dashboard_service"):
        request.app.state.dashboard_service = DashboardService(request.app.state.db_path)
    return request.app.state.dashboard_service


@router.get("/kpis")
async def get_kpis(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Retorna todos los KPIs operacionales del dashboard."""
    svc = _get_dashboard_service(request)
    kpis = svc.get_kpis()
    return ApiResponse(data=kpis)


@router.get("/triages-7d")
async def get_triages_7d(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Retorna el conteo de triajes por día en los últimos 7 días."""
    svc = _get_dashboard_service(request)
    data = svc.get_triages_7d()
    return ApiResponse(data=data)
