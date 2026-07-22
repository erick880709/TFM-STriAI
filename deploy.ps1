# =============================================================================
# deploy.ps1 — Script de despliegue rápido de STriAI con Docker
# =============================================================================
# Uso:
#   .\deploy.ps1              → Build + run en producción
#   .\deploy.ps1 -Dev         → Modo desarrollo (hot-reload)
#   .\deploy.ps1 -BuildOnly   → Solo construir la imagen
#   .\deploy.ps1 -Down        → Detener y limpiar
#   .\deploy.ps1 -Logs        → Ver logs
# =============================================================================

param(
    [switch]$Dev,
    [switch]$BuildOnly,
    [switch]$Down,
    [switch]$Logs
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# ---------------------------------------------------------------------------
# Colores para salida
# ---------------------------------------------------------------------------
function Write-Step { param($Text) Write-Host "`n>>> $Text" -ForegroundColor Cyan }
function Write-OK   { param($Text) Write-Host "  ✓ $Text" -ForegroundColor Green }
function Write-Warn { param($Text) Write-Host "  ⚠ $Text" -ForegroundColor Yellow }

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
Write-Host @"

  ╔══════════════════════════════════════════════════╗
  ║   🏥  STriAI — Sistema de Triaje Multimodal IA  ║
  ║   TFM — Máster en Inteligencia Artificial UNIR   ║
  ╚══════════════════════════════════════════════════╝

"@ -ForegroundColor Blue

# ---------------------------------------------------------------------------
# Verificar prerequisitos
# ---------------------------------------------------------------------------
Write-Step "Verificando prerequisitos..."

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "  ✗ Docker no está instalado. Instálalo desde https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}
Write-OK "Docker detectado: $(docker --version)"

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue) -and -not (docker compose version 2>$null)) {
    Write-Host "  ✗ Docker Compose no está disponible." -ForegroundColor Red
    exit 1
}
Write-OK "Docker Compose detectado"

# Verificar archivo .env
if (-not (Test-Path ".env")) {
    Write-Warn ".env no encontrado. Creando desde .env.docker..."
    Copy-Item ".env.docker" ".env"
    Write-OK ".env creado (revisa y ajusta las variables si es necesario)"
}

# ---------------------------------------------------------------------------
# Detener
# ---------------------------------------------------------------------------
if ($Down) {
    Write-Step "Deteniendo contenedores..."
    docker compose down --remove-orphans
    Write-OK "Contenedores detenidos y limpiados"
    exit 0
}

# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------
if ($Logs) {
    Write-Step "Mostrando logs (Ctrl+C para salir)..."
    docker compose logs -f --tail=100
    exit 0
}

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
Write-Step "Construyendo imagen Docker..."
docker compose build --no-cache
Write-OK "Imagen construida: striai:latest"

if ($BuildOnly) {
    Write-OK "Build completado. La imagen striai:latest está lista."
    Write-Host "`n  Para ejecutar: docker compose up -d" -ForegroundColor Gray
    exit 0
}

# ---------------------------------------------------------------------------
# Ejecutar
# ---------------------------------------------------------------------------
if ($Dev) {
    Write-Step "Iniciando en modo DESARROLLO (hot-reload)..."
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    Write-OK "Contenedor iniciado en modo desarrollo"
    Write-Host "`n  🌐 Abre http://localhost:8501 en tu navegador" -ForegroundColor Green
    Write-Host "  📝 Los cambios en código se reflejan automáticamente" -ForegroundColor Gray
    Write-Host "  📋 Para ver logs: .\deploy.ps1 -Logs" -ForegroundColor Gray
    Write-Host "  🛑 Para detener: .\deploy.ps1 -Down`n" -ForegroundColor Gray
} else {
    Write-Step "Iniciando en modo PRODUCCIÓN..."
    docker compose up -d
    Write-OK "Contenedor iniciado en modo producción"
    Write-Host "`n  🌐 Abre http://localhost:8501 en tu navegador" -ForegroundColor Green
    Write-Host "  📋 Para ver logs: .\deploy.ps1 -Logs" -ForegroundColor Gray
    Write-Host "  🛑 Para detener: .\deploy.ps1 -Down`n" -ForegroundColor Gray
}

# ---------------------------------------------------------------------------
# Resumen de acceso
# ---------------------------------------------------------------------------
Write-Step "Usuarios de prueba"
Write-Host @"

  ┌─────────────────────┬─────────────┬──────────────────┐
  │ Usuario             │ Contraseña  │ Rol              │
  ├─────────────────────┼─────────────┼──────────────────┤
  │ admin               │ admin123    │ Administrador    │
  │ enfermera_01        │ admin123    │ Enfermera        │
  │ medico_01           │ admin123    │ Médico           │
  │ investigador_01     │ admin123    │ Investigador     │
  │ auditor_01          │ admin123    │ Auditor          │
  └─────────────────────┴─────────────┴──────────────────┘

"@
