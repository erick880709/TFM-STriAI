"""
Configuración del sistema.
Carga variables desde .env y archivo YAML.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # sistema-triaje-ia/app/
REPO_ROOT = BASE_DIR.parent.parent  # TFM-FINAL/
MODELS_DEFAULT = REPO_ROOT / "models"  # TFM-FINAL/models/

def load_config() -> dict:
    """Carga la configuración desde .env con valores por defecto."""
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    return {
        "db_path": os.getenv("DB_PATH", str(BASE_DIR / "data" / "triaje.db")),
        "session_timeout_minutes": int(os.getenv("SESSION_TIMEOUT_MINUTES", "15")),
        "bcrypt_rounds": int(os.getenv("BCRYPT_ROUNDS", "12")),
        "model_path": os.getenv("MODEL_PATH", str(MODELS_DEFAULT)),
        "active_model": os.getenv("ACTIVE_MODEL", "xgboost_early_fusion_v1"),
        "env": os.getenv("ENV", "development"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        # FastAPI / JWT
        "jwt_secret": os.getenv("JWT_SECRET", "cambiar-por-secreto-seguro-en-produccion"),
        "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
        "jwt_expiration_minutes": int(os.getenv("JWT_EXPIRATION_MINUTES", "15")),
        # CORS
        "cors_origins": os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:8501"
        ).split(","),
    }


def get_db_path(cfg: dict) -> str:
    """Retorna la ruta completa a la base de datos."""
    path = cfg["db_path"]
    if not os.path.isabs(path):
        path = str(BASE_DIR / path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path
