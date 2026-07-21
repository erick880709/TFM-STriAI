"""Fixtures compartidos para tests de API."""
import os
import sys
import tempfile
import pytest
from pathlib import Path

# Asegurar que app/ está en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["JWT_SECRET"] = "test-secret-key-for-pytest"
os.environ["ENV"] = "testing"

from fastapi.testclient import TestClient
from app.main import create_app
from app.data.database import init_db
from app.services.auth_service import AuthService
from app.middleware.auth import create_access_token


@pytest.fixture
def app():
    """FastAPI app con BD temporal y datos de prueba."""
    # Usar archivo temporal (no :memory:) para que múltiples conexiones
    # compartan la misma BD
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    os.environ["DB_PATH"] = db_path
    app = create_app()

    # Inicializar manualmente el estado (el lifespan no corre en tests)
    app.state.db_path = db_path
    init_db(db_path)
    app.state.auth_service = AuthService(db_path)

    yield app

    # Limpiar
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def client(app):
    """TestClient de FastAPI."""
    return TestClient(app)


@pytest.fixture
def admin_token():
    """Token JWT de administrador para tests."""
    return create_access_token(data={"sub": "admin", "rol": "Administrador"})


@pytest.fixture
def auth_headers(admin_token):
    """Headers con token JWT de admin."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def enfermera_token():
    """Token JWT de enfermera."""
    return create_access_token(data={"sub": "enfermera_01", "rol": "Enfermera"})


@pytest.fixture
def enfermera_headers(enfermera_token):
    return {"Authorization": f"Bearer {enfermera_token}"}
