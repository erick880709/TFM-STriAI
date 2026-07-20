# Manual de Instalación — STriAI (Sistema de Triaje Multimodal IA)

**TFM UNIR — Máster en Inteligencia Artificial**
**Versión:** 1.0 — Julio 2026

---

## Tabla de Contenido

1. [Requisitos del Sistema](#1-requisitos-del-sistema)
2. [Estructura del Proyecto](#2-estructura-del-proyecto)
3. [Instalación Paso a Paso](#3-instalación-paso-a-paso)
4. [Configuración del Entorno](#4-configuración-del-entorno)
5. [Base de Datos](#5-base-de-datos)
6. [Modelos de Machine Learning](#6-modelos-de-machine-learning)
7. [Ejecución de la Aplicación](#7-ejecución-de-la-aplicación)
8. [Verificación de la Instalación](#8-verificación-de-la-instalación)
9. [Instalación en Producción](#9-instalación-en-producción)
10. [Solución de Problemas](#10-solución-de-problemas)

---

## 1. Requisitos del Sistema

### 1.1 Hardware

| Componente | Mínimo | Recomendado |
|---|---|---|
| **RAM** | 4 GB | 8 GB o más |
| **Disco** | 1 GB libre | 3 GB libre (incluye modelo NLP ~420 MB) |
| **CPU** | 2 núcleos | 4+ núcleos (Intel i5/AMD Ryzen 5 o superior) |
| **GPU** | No requerida | NVIDIA con CUDA (opcional, acelera NLP) |

### 1.2 Software

| Componente | Versión Mínima | Notas |
|---|---|---|
| **Sistema Operativo** | Windows 10/11, macOS 12+, Ubuntu 20.04+ | Compatible con cualquier SO que soporte Python |
| **Python** | 3.11+ | 3.11.7 usado en desarrollo |
| **pip** | 23.0+ | Gestor de paquetes de Python |
| **Git** | 2.30+ | Solo si se clona el repositorio |
| **Navegador Web** | Chrome 90+, Firefox 90+, Edge 90+ | Para acceder a la interfaz Streamlit |

### 1.3 Dependencias Clave

| Librería | Versión | Propósito |
|---|---|---|
| Streamlit | ≥1.31.0 | Framework de interfaz web |
| pandas | ≥2.2.0 | Manipulación de datos |
| scikit-learn | ≥1.4.0 | Preprocesamiento y modelos ML |
| XGBoost | ≥2.0.0 | Modelo de gradient boosting |
| PyTorch | ≥2.2.0 | Backend para transformers |
| Transformers | ≥4.38.0 | Modelos NLP (BERT) |
| SHAP | ≥0.44.0 | Explicabilidad de modelos |
| bcrypt | ≥4.1.0 | Hashing de contraseñas |
| SQLite3 | Incluido en Python | Base de datos local |

---

## 2. Estructura del Proyecto

```
TFM-FINAL/
├── app.py                          ← Punto de entrada principal
├── run_pipeline.py                 ← Pipeline de entrenamiento ML
├── sistema-triaje-ia/              ← Código fuente de la aplicación
│   ├── .env.example                ← Plantilla de configuración
│   ├── requirements.txt            ← Dependencias Python
│   ├── app.py                      ← Entry point Streamlit
│   ├── app/
│   │   ├── config/settings.py      ← Carga de configuración
│   │   ├── data/database.py        ← Inicialización SQLite (12 tablas)
│   │   ├── services/               ← Lógica de negocio
│   │   │   ├── auth_service.py     ← Autenticación y RBAC
│   │   │   ├── patient_service.py  ← Gestión de pacientes
│   │   │   ├── triage_service.py   ← Máquina de estados de triaje
│   │   │   ├── inference_service.py← Carga y predicción del modelo
│   │   │   └── audit_service.py    ← Auditoría
│   │   └── ui/                     ← Páginas de la interfaz (14 pantallas)
│   ├── data/                       ← Base de datos SQLite (auto-generada)
│   └── models/                     ← Modelos serializados (ver §6)
├── src/                            ← Código del pipeline ML
│   ├── data/                       ← Ingesta, limpieza, anonimización
│   ├── features/                   ← Embeddings NLP
│   ├── models/                     ← Entrenamiento (LR, RF, XGBoost, Fusion)
│   ├── evaluation/                 ← Métricas, SHAP, benchmarks
│   └── serving/                    ← Serialización de modelos
├── datasets/                       ← Datos de entrenamiento (CSV)
├── models/                         ← Modelos entrenados (generado por pipeline)
├── notebooks/                      ← Jupyter notebooks (exploración)
└── resources/
    └── manuales/                   ← Documentación del proyecto
```

---

## 3. Instalación Paso a Paso

### 3.1 Obtener el Código Fuente

**Opción A — Carpeta existente (recomendado para el tribunal):**

El proyecto ya se encuentra en la carpeta `TFM-FINAL/`. Navegue a ella:

```powershell
cd "C:\Users\ELITEBOOK\OneDrive\Documentos\Repositorio\Trabajo\TFM-FINAL"
```

**Opción B — Clonar desde Git (si está disponible):**

```bash
git clone <url-del-repositorio> TFM-FINAL
cd TFM-FINAL
```

### 3.2 Crear Entorno Virtual

**Windows (PowerShell):**

```powershell
python -m venv .venv
```

**macOS / Linux:**

```bash
python3 -m venv .venv
```

### 3.3 Activar el Entorno Virtual

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

> ⚠️ Si aparece error de política de ejecución:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

**Windows (CMD):**

```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 3.4 Instalar Dependencias

```bash
pip install -r sistema-triaje-ia/requirements.txt
```

> ⏱️ **Tiempo estimado:** 5-15 minutos (depende de la velocidad de internet). El paquete más pesado es PyTorch (~122 MB).

**Verificar instalación:**

```bash
python -c "import streamlit; import pandas; import sklearn; import xgboost; import torch; import transformers; print('✓ Todas las dependencias OK')"
```

### 3.5 Configurar Variables de Entorno

```powershell
# Windows PowerShell
Copy-Item sistema-triaje-ia\.env.example sistema-triaje-ia\.env
```

```bash
# macOS / Linux
cp sistema-triaje-ia/.env.example sistema-triaje-ia/.env
```

El archivo `.env` contiene:

```ini
DB_PATH=data/triaje.db
SESSION_TIMEOUT_MINUTES=15
BCRYPT_ROUNDS=12
```

> 💡 No es necesario modificar estos valores para desarrollo local.

### 3.6 Verificar Datasets (solo si se va a re-entrenar)

Los datasets de entrenamiento deben estar en `datasets/`:

```
datasets/
├── Clasificación_en_Triage_Urgencias_20260713.csv
├── dataset_urgencias_san_juan_de_dios_custom.csv
├── MORBILIDAD_EN_EL_SERVICIO_DE_URGENCIAS_20260713.csv
└── Morbilidad_Urgencias_2019_…_Pitalito_…csv
```

> ⚠️ Los datasets no son necesarios para ejecutar la aplicación demo. Solo se requieren para re-entrenar los modelos con `run_pipeline.py`.

---

## 4. Configuración del Entorno

### 4.1 Archivo `.env`

| Variable | Valor por Defecto | Descripción |
|---|---|---|
| `DB_PATH` | `data/triaje.db` | Ruta a la base de datos SQLite |
| `SESSION_TIMEOUT_MINUTES` | `15` | Tiempo de inactividad antes de cerrar sesión |
| `BCRYPT_ROUNDS` | `12` | Rondas de hashing para contraseñas |
| `MODEL_PATH` | `models/` | Directorio de modelos serializados |
| `ACTIVE_MODEL` | `xgboost_early_fusion_v1` | Versión del modelo activo |
| `ENV` | `development` | Entorno (`development`, `staging`, `production`) |
| `LOG_LEVEL` | `INFO` | Nivel de logging |

### 4.2 Configuración Avanzada

Para entornos de producción, se recomienda modificar:

```ini
ENV=production
SESSION_TIMEOUT_MINUTES=30
BCRYPT_ROUNDS=14
LOG_LEVEL=WARNING
```

---

## 5. Base de Datos

### 5.1 Inicialización Automática

La base de datos SQLite se **crea automáticamente** al iniciar la aplicación por primera vez. No requiere instalación ni configuración manual.

El archivo se genera en `sistema-triaje-ia/data/triaje.db`.

### 5.2 Esquema

La base de datos contiene **12 tablas**:

| # | Tabla | Descripción |
|---|---|---|
| 1 | `Paciente` | Datos demográficos y de contacto (21 columnas) |
| 2 | `EventoTriaje` | Registro de eventos de triaje con máquina de estados |
| 3 | `SignosVitales` | Tensión arterial, FC, FR, T°, SpO₂, peso, talla, IMC |
| 4 | `EvaluacionClinica` | Motivo de consulta, Glasgow, dolor, conciencia |
| 5 | `ResultadoIA` | Predicciones del modelo con probabilidades |
| 6 | `Usuario` | Cuentas de acceso con roles (5 roles) |
| 7 | `Sesion` | Registro de sesiones de usuario |
| 8 | `Auditoria` | Registro inmutable de acciones (17 tipos) |
| 9 | `Cambio` | Control de cambios en entidades |
| 10 | `ModeloIA` | Registro de versiones de modelos |
| 11 | `MetricaModelo` | Métricas de rendimiento por versión |
| 12 | `ConfiguracionSistema` | Parámetros de configuración |

### 5.3 Usuarios Demo Precargados

Al inicializar la base de datos, se crean **5 usuarios de prueba**:

| Usuario | Contraseña | Rol | Permisos |
|---|---|---|---|
| `admin` | `admin123` | Administrador | Todos los permisos |
| `medico` | `medico123` | Médico | Triaje, pacientes, validación |
| `enfermera` | `enfermera123` | Enfermera | Registro, signos vitales |
| `investigador` | `investigador123` | Investigador | Dashboard, auditoría (lectura) |
| `auditor` | `auditor123` | Auditor | Solo lectura y reportes |

> 🔒 **Cambie estas contraseñas en producción.** Use el panel de Administración → Gestión de Usuarios.

### 5.4 Restablecer la Base de Datos

Para empezar desde cero:

```powershell
# Windows PowerShell
Remove-Item sistema-triaje-ia\data\triaje.db -ErrorAction SilentlyContinue
```

La base de datos se recreará automáticamente al iniciar la app.

---

## 6. Modelos de Machine Learning

### 6.1 Modelo Pre-entrenado

Si los modelos ya fueron entrenados con `run_pipeline.py`, los artefactos se encuentran en `models/`:

```
models/
├── active_version.txt
└── early_fusion_v20260720_100649/
    ├── model.joblib
    ├── scaler.joblib
    ├── encoder.joblib
    ├── feature_names.json
    ├── thresholds.json
    └── metadata.json
```

La aplicación carga automáticamente el modelo activo (indicado en `active_version.txt`) a través del `InferenceService`.

### 6.2 Ejecutar el Pipeline de Entrenamiento (Opcional)

Si necesita **re-entrenar los modelos** desde cero:

```bash
cd TFM-FINAL
python run_pipeline.py
```

| Modo | Tiempo Estimado | Requisitos |
|---|---|---|
| CPU | ~17 minutos | 8 GB RAM |
| GPU (CUDA) | ~3 minutos | GPU NVIDIA + CUDA Toolkit |

Para usar GPU:

```bash
python run_pipeline.py --use-gpu --nlp-model biomedical_es
```

> 📘 Consulte el **Manual de Modelos** (`MANUAL_MODELOS_STriAI.md`) para detalles sobre los 5 modelos entrenados, arquitectura, resultados y limitaciones.

### 6.3 Verificar que el Modelo se Carga Correctamente

```bash
python -c "
from src.serving.serialize import ModelSerializer
s = ModelSerializer()
m, sc, enc, meta = s.load_active()
print(f'Modelo: {meta[\"model_name\"]} v{meta[\"version\"]}')
print(f'F1 Macro: {meta[\"metrics\"][\"f1_macro\"]:.4f}')
"
```

---

## 7. Ejecución de la Aplicación

### 7.1 Iniciar el Servidor

Desde la raíz del proyecto (`TFM-FINAL/`):

```bash
streamlit run app.py --server.port 8501
```

O desde dentro de `sistema-triaje-ia/`:

```bash
cd sistema-triaje-ia
streamlit run app.py --server.port 8501
```

### 7.2 Acceder a la Aplicación

Abra su navegador en:

```
http://localhost:8501
```

### 7.3 Opciones de Línea de Comandos

| Argumento | Default | Descripción |
|---|---|---|
| `--server.port` | `8501` | Puerto del servidor web |
| `--server.address` | `localhost` | Dirección de escucha |
| `--server.headless` | `false` | Modo sin navegador |
| `--server.maxUploadSize` | `200` | Tamaño máximo de upload (MB) |
| `--browser.gatherUsageStats` | `false` | Desactivar telemetría |
| `--logger.level` | `info` | Nivel de logging |

Ejemplo con opciones:

```bash
streamlit run app.py --server.port 8080 --server.headless true --logger.level warning
```

### 7.4 Acceso Remoto (Red Local)

Para permitir acceso desde otros dispositivos en la misma red:

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Luego acceda desde `http://<IP-DEL-EQUIPO>:8501`.

---

## 8. Verificación de la Instalación

### 8.1 Checklist de Verificación

| # | Paso | Comando / Acción | Resultado Esperado |
|---|---|---|---|
| 1 | Python instalado | `python --version` | Python 3.11.x |
| 2 | Entorno virtual | `.venv\Scripts\Activate.ps1` | Prompt muestra `(.venv)` |
| 3 | Dependencias | `pip list \| grep streamlit` | streamlit 1.59.x |
| 4 | Archivo .env | `cat sistema-triaje-ia\.env` | Variables de configuración |
| 5 | Modelos | `ls models/early_fusion_*/` | 6 archivos (.joblib + .json) |
| 6 | App inicia | `streamlit run app.py` | Servidor en http://localhost:8501 |
| 7 | Login | Abrir navegador, login con `admin` / `admin123` | Dashboard visible |
| 8 | Navegación | Clic en menú lateral (Pacientes, Triaje, etc.) | Páginas cargan sin errores |
| 9 | Predicción IA | Registrar paciente → Iniciar triaje → Clasificación IA | Nivel de triaje sugerido |

### 8.2 Prueba Rápida de Funcionalidad

```bash
# 1. Verificar que Python y entorno virtual funcionan
python -c "import sys; print(sys.executable); print(sys.version)"

# 2. Verificar que Streamlit se instaló correctamente
streamlit version

# 3. Verificar que el modelo se carga
python -c "
import sys; sys.path.insert(0, 'sistema-triaje-ia')
from src.serving.serialize import ModelSerializer
s = ModelSerializer()
m, sc, enc, meta = s.load_active()
print('✓ Modelo cargado:', meta['model_name'], 'v' + meta['version'])
"

# 4. Verificar que la base de datos se inicializa
python -c "
import sys; sys.path.insert(0, 'sistema-triaje-ia')
from app.data.database import init_db
init_db('data/test_check.db')
print('✓ Base de datos inicializada correctamente')
" && rm data/test_check.db 2>$null
```

---

## 9. Instalación en Producción

### 9.1 Recomendaciones de Seguridad

| Área | Recomendación |
|---|---|
| **Contraseñas** | Cambiar TODAS las contraseñas demo. Usar mínimo 12 caracteres |
| **.env** | No versionar en Git. Usar valores seguros para producción |
| **BCRYPT_ROUNDS** | Aumentar a 14-16 en producción |
| **Sesiones** | Reducir timeout a 10 minutos en entornos sensibles |
| **HTTPS** | Usar un reverse proxy (Nginx/Caddy) con SSL |
| **Firewall** | Limitar acceso al puerto 8501 solo a IPs autorizadas |
| **Backups** | Respaldar `data/triaje.db` diariamente |

### 9.2 Despliegue con Docker (Opcional)

Crear `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY sistema-triaje-ia/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Construir y ejecutar:

```bash
docker build -t striai .
docker run -p 8501:8501 -v $(pwd)/models:/app/models -v $(pwd)/data:/app/data striai
```

### 9.3 Despliegue en Cloud (Streamlit Community Cloud)

1. Subir el repositorio a GitHub
2. Conectar en [share.streamlit.io](https://share.streamlit.io)
3. Configurar `sistema-triaje-ia/requirements.txt` como archivo de dependencias
4. Configurar secrets para `DB_PATH`, `BCRYPT_ROUNDS`, etc.

> ⚠️ Streamlit Cloud tiene límites de memoria (1 GB RAM). Puede no ser suficiente para cargar el modelo NLP.

---

## 10. Solución de Problemas

### 10.1 Errores Comunes

#### ❌ `Python not found`

```powershell
# Verificar instalación
python --version

# Si no está instalado, descargar de:
# https://www.python.org/downloads/
# ✅ Marcar "Add Python to PATH" durante la instalación
```

#### ❌ `pip is not recognized`

```powershell
# Usar el módulo Python directamente:
python -m pip install -r sistema-triaje-ia/requirements.txt
```

#### ❌ `No module named 'streamlit'`

```bash
# Asegurarse de que el entorno virtual está activado
# Windows:
.\.venv\Scripts\Activate.ps1

# Luego reinstalar:
pip install -r sistema-triaje-ia/requirements.txt
```

#### ❌ `WinError 206` — Nombre de archivo demasiado largo

Este error ocurre en Windows al instalar PyTorch por una limitación de 260 caracteres en rutas.

**Solución:** Habilitar rutas largas en Windows:

```powershell
# Ejecutar como Administrador:
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

O usar un directorio de instalación más corto (ej. `C:\TFM`).

#### ❌ `Port 8501 already in use`

```bash
# Cambiar el puerto:
streamlit run app.py --server.port 8502

# O liberar el puerto 8501 (Windows):
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### ❌ `ValueError: No se pudo unificar ninguna fuente`

Este error ocurre al ejecutar `run_pipeline.py` sin los datasets correctos.

**Solución:** Verificar que los 4 archivos CSV existen en `datasets/` con los nombres exactos.

#### ❌ Error de permisos al activar el entorno virtual (Windows)

```powershell
# Si aparece:
# "No se puede cargar el archivo .\\.venv\\Scripts\\Activate.ps1 porque la ejecución de scripts está deshabilitada"

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### ❌ `OutOfMemoryError` o la app se cierra al cargar

El modelo NLP consume ~1.5 GB de RAM al cargarse. Si tiene menos de 4 GB:

**Solución temporal:** Cerrar otras aplicaciones para liberar RAM.

**Solución permanente:** La aplicación funciona sin el modelo IA (las funcionalidades de clasificación automática no estarán disponibles, pero el resto de la app funciona).

#### ❌ `bcrypt` no se instala

En algunas versiones de Windows, `bcrypt` requiere Visual C++ Build Tools:

```powershell
# Instalar Visual C++ Build Tools desde:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### 10.2 Logs y Depuración

Los logs de la aplicación se muestran en la terminal donde se ejecuta Streamlit. Para aumentar el nivel de detalle:

```bash
streamlit run app.py --logger.level debug
```

### 10.3 Restablecimiento Completo

Si necesita empezar desde cero:

```powershell
# 1. Eliminar entorno virtual
Remove-Item -Recurse -Force .venv

# 2. Eliminar base de datos
Remove-Item -Force sistema-triaje-ia\data\triaje.db -ErrorAction SilentlyContinue

# 3. Recrear entorno
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r sistema-triaje-ia/requirements.txt

# 4. Re-inicializar
cd sistema-triaje-ia
streamlit run app.py --server.port 8501
```

---

## Apéndice A: Comandos Rápidos

```bash
# === INSTALACIÓN COMPLETA (Windows PowerShell) ===

# 1. Navegar al proyecto
cd "C:\Users\ELITEBOOK\OneDrive\Documentos\Repositorio\Trabajo\TFM-FINAL"

# 2. Crear y activar entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r sistema-triaje-ia/requirements.txt

# 4. Configurar entorno
Copy-Item sistema-triaje-ia\.env.example sistema-triaje-ia\.env

# 5. Iniciar aplicación
streamlit run app.py --server.port 8501

# 6. Abrir navegador
start http://localhost:8501
```

```bash
# === INSTALACIÓN COMPLETA (macOS / Linux) ===

# 1. Navegar al proyecto
cd /ruta/a/TFM-FINAL

# 2. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r sistema-triaje-ia/requirements.txt

# 4. Configurar entorno
cp sistema-triaje-ia/.env.example sistema-triaje-ia/.env

# 5. Iniciar aplicación
streamlit run app.py --server.port 8501

# 6. Abrir navegador
open http://localhost:8501
```

## Apéndice B: Puertos y Servicios

| Servicio | Puerto | URL |
|---|---|---|
| Aplicación Streamlit | 8501 | http://localhost:8501 |
| (Opcional) Segundo puerto | 8502 | http://localhost:8502 |

## Apéndice C: Requisitos de Espacio en Disco

| Componente | Tamaño Aproximado |
|---|---|
| Entorno virtual (.venv) | ~800 MB |
| Modelo NLP (MiniLM) | ~420 MB |
| Modelos entrenados (.joblib) | ~5 MB |
| Base de datos SQLite | ~2-10 MB (crece con uso) |
| Código fuente | ~2 MB |
| Datasets CSV | ~15 MB |
| **Total** | **~1.3 GB** |

---

*Documento generado por STriAI — TFM UNIR Máster en Inteligencia Artificial — Julio 2026*
