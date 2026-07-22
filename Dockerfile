# =============================================================================
# STriAI — Sistema de Triaje Multimodal IA
# Dockerfile para despliegue local del monolito Streamlit (AS-IS)
# =============================================================================
# Build:  docker build -t striai:latest .
# Run:    docker run -p 8501:8501 --env-file .env striai:latest
# =============================================================================

FROM python:3.10-slim AS base

# --- Metadatos -----------------------------------------------------------------
LABEL maintainer="TFM UNIR — STriAI"
LABEL description="Sistema de Triaje Multimodal IA — Aplicación Streamlit"
LABEL version="1.0"

# --- Variables de build -------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# --- Sistema: librerías necesarias para compilar dependencias ------------------
RUN apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        libopenblas-dev \
        libomp-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- Directorio de trabajo -----------------------------------------------------
# REPO_ROOT esperado por settings.py e inference_service.py = /app
WORKDIR /app

# --- Instalación de dependencias Python (capa cacheable) -----------------------
# Primero copiamos solo requirements para aprovechar caché de Docker
COPY sistema-triaje-ia/requirements.txt /app/sistema-triaje-ia/requirements.txt

RUN pip install --no-cache-dir -r /app/sistema-triaje-ia/requirements.txt

# --- Copia del código fuente ---------------------------------------------------
# Estructura esperada dentro del contenedor:
#   /app/
#     sistema-triaje-ia/       ← app Streamlit (app.py, app/, data/, models/)
#     src/                     ← pipeline ML compartido (data, features, models, serving, evaluation)
#     models/                  ← artefactos de modelo serializados

COPY sistema-triaje-ia/ /app/sistema-triaje-ia/
COPY src/             /app/src/
COPY models/          /app/models/

# --- Configuración de entorno --------------------------------------------------
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_THEME_BASE="light" \
    STREAMLIT_SERVER_MAX_UPLOAD_SIZE=50 \
    # App config — sobreescribibles en docker-compose / docker run -e
    DB_PATH=data/triaje.db \
    SESSION_TIMEOUT_MINUTES=15 \
    BCRYPT_ROUNDS=12 \
    MODEL_PATH=/app/models/ \
    ACTIVE_MODEL=early_fusion_v20260720_224350 \
    ENV=production \
    LOG_LEVEL=INFO

# --- Healthcheck ---------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" \
    || exit 1

# --- Puerto --------------------------------------------------------------------
EXPOSE 8501

# --- Entrypoint ----------------------------------------------------------------
# Ejecutar desde sistema-triaje-ia/ (app.py espera rutas relativas a este dir)
WORKDIR /app/sistema-triaje-ia

# Usuario no-root por seguridad
RUN useradd --create-home --shell /bin/bash striai \
    && chown -R striai:striai /app
USER striai

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
