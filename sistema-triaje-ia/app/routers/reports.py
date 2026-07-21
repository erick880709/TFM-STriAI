"""
Router de reportes — /api/reports/*
Endpoints: generación y descarga de informes HTML de triaje.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from app.schemas.common import ApiResponse
from app.middleware.auth import get_current_user, TokenData
from app.services.report_service import ReportService

router = APIRouter()


def _get_report_service(request: Request) -> ReportService:
    if not hasattr(request.app.state, "report_service"):
        request.app.state.report_service = ReportService(request.app.state.db_path)
    return request.app.state.report_service


@router.get("/triage/{id_triaje}/html", response_class=HTMLResponse)
async def get_triage_report_html(
    id_triaje: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Retorna el informe HTML de un triaje."""
    svc = _get_report_service(request)
    try:
        html = svc.generate_triage_html(id_triaje)
        return html
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/triage/{id_triaje}/download")
async def download_triage_report(
    id_triaje: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Descarga el informe de triaje como archivo HTML."""
    svc = _get_report_service(request)
    try:
        html_bytes = svc.get_triage_html_bytes(id_triaje)
        from fastapi.responses import Response
        return Response(
            content=html_bytes,
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename=triaje_{id_triaje}.html"},
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
