"""
Aplicación FastAPI — Punto de entrada del backend REST.
Sirve también el frontend React en producción.

Uso:
    uvicorn app.main:app --reload --port 8000
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import load_config, get_db_path, REPO_ROOT
from app.data.database import init_db
from app.services.auth_service import AuthService
from app.services.inference_service import get_inference_service


# Ruta al build de React
FRONTEND_DIST = REPO_ROOT / "sistema-triaje-ia" / "frontend" / "dist"


# ---------------------------------------------------------------------------
# Lifespan: inicialización y cierre del servidor
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa BD, servicios y modelo IA al arrancar el servidor."""
    cfg = load_config()
    db_path = get_db_path(cfg)

    # Base de datos
    init_db(db_path)

    # Servicios base (singletons a nivel de aplicación)
    app.state.db_path = db_path
    app.state.config = cfg
    app.state.auth_service = AuthService(db_path)

    # Cargar modelo IA — usa MODELS_DIR automático
    print("[FASTAPI] Cargando modelo IA...")
    from app.services.inference_service import MODELS_DIR
    print(f"[FASTAPI] Directorio de modelos: {MODELS_DIR}")
    inference = get_inference_service(None)
    if not inference.model:
        ok = inference.load_model()
        print(f"[FASTAPI] Modelo cargado: {ok}")
    else:
        print(f"[FASTAPI] Modelo ya cargado: {inference.get_status().get('version', '?')}")
    app.state.inference_service = inference

    print(f"[FASTAPI] Servidor listo en http://0.0.0.0:8000")
    print(f"[FASTAPI] Swagger UI: http://localhost:8000/docs")

    yield

    print("[FASTAPI] Apagando servidor...")


# ---------------------------------------------------------------------------
# App Factory
# ---------------------------------------------------------------------------
def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI."""
    app = FastAPI(
        title="STriAI — Sistema de Triaje Multimodal IA",
        description="API REST para el sistema de triaje clínico con IA. TFM UNIR.",
        version="2.0.0",
        lifespan=lifespan,
    )

    # CORS
    cfg = load_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg["cors_origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Montar routers
    from app.routers import auth, patients, control_cambios, triages, inference, dashboard, models, audit, reports, users
    app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
    app.include_router(patients.router, prefix="/api/patients", tags=["Pacientes"])
    app.include_router(triages.router, prefix="/api/triages", tags=["Triajes"])
    app.include_router(inference.router, prefix="/api/inference", tags=["Inferencia IA"])
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
    app.include_router(models.router, prefix="/api/models", tags=["Modelos IA"])
    app.include_router(audit.router, prefix="/api/audit", tags=["Auditoría"])
    app.include_router(reports.router, prefix="/api/reports", tags=["Reportes"])
    app.include_router(users.router, prefix="/api/users", tags=["Usuarios"])
    app.include_router(control_cambios.router, prefix="/api/control-cambios", tags=["Control de Cambios"])

    # Health check (debe ir antes del catch-all del SPA)
    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "2.0.0"}

    # Servir frontend React en producción
    if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
        from fastapi.responses import FileResponse

        # 1. Montar assets estáticos (JS, CSS, imágenes, fuentes)
        assets_dir = FRONTEND_DIST / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="spa_assets")

        # 2. SPA catch-all: todo → verifica archivo estático o devuelve index.html
        @app.get("/{full_path:path}")
        async def serve_react(full_path: str = ""):
            """Sirve archivos estáticos de raíz o fallback SPA index.html."""
            # Saltar rutas de API que ya manejan otros routers
            if full_path.startswith("api/") or full_path == "health":
                from fastapi.responses import JSONResponse
                return JSONResponse({"detail": "Not found"}, status_code=404)

            # Intentar servir archivo estático suelto de dist/
            file_path = FRONTEND_DIST / full_path
            if file_path.is_file():
                return FileResponse(file_path)

            # Fallback SPA: index.html para client-side routing
            index_path = FRONTEND_DIST / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            return {"message": "Frontend no disponible"}

    return app


# Instancia a nivel de módulo para uvicorn
app = create_app()
