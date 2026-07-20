# Manual Técnico — STriAI (Sistema de Triaje Multimodal IA)

**Versión:** 1.0 Demo  
**TFM — Máster en Inteligencia Artificial — UNIR**  
**Stack:** Python 3.11 · Streamlit 1.59+ · SQLite 3 · XGBoost 2.0+ · scikit-learn 1.4+ · SHAP 0.44+ · BERT-es · bcrypt 5.0

---

## 1. Arquitectura General

### 1.1 Diagrama de Capas

```
┌─────────────────────────────────────────────────┐
│                  app.py (Entry Point)            │
│    Router · Sidebar · Session State · Auth       │
├──────────────┬──────────────────────────────────┤
│   app/ui/    │         app/services/             │
│  (Streamlit) │  (Business Logic + ML Inference)  │
│              │                                   │
│  P01-P14     │  auth_service  triage_service     │
│  login       │  patient_service                  │
│  patient     │  inference_service                │
│  vital_signs │  audit_service                    │
│  clinical    │  report_service                   │
│  ia_classif  │                                   │
│  dashboard   ├──────────────────────────────────┤
│  models      │        app/data/                  │
│  audit       │     database.py (SQLite)          │
│  users       │  12 tablas · Índices · Migración   │
│  control_cb  │  SEED SQL · row_to_dict()         │
│  historico   │                                   │
├──────────────┴──────────────────────────────────┤
│              app/config/settings.py              │
│         .env · YAML · Variables de entorno       │
└─────────────────────────────────────────────────┘

Pipeline ML (externo):
  src/               → Código reutilizable del pipeline
  notebooks/         → Exploración y experimentos
  models/            → Artefactos serializados (.pkl)
  run_pipeline.py    → Pipeline 14 pasos ejecutable
```

### 1.2 Patrón Arquitectónico

**Layered Monolith** con separación modular:

- **UI Layer** (`app/ui/`): Componentes Streamlit sin estado. Cada pantalla es una función `render_*()` independiente.
- **Service Layer** (`app/services/`): Lógica de negocio pura. Clases con inyección de `db_path`. Sin dependencia de Streamlit (salvo `auth_service` para `st.session_state`).
- **Data Layer** (`app/data/`): Acceso a SQLite. Schema DDL, helpers `row_to_dict()`/`rows_to_dicts()`, migraciones incrementales, datos semilla.
- **Config Layer** (`app/config/`): Carga de `.env` y variables de entorno.

**Principio clave:** Las páginas UI nunca acceden directamente a la BD; siempre pasan por los servicios.

---

## 2. Stack Tecnológico

| Componente | Tecnología | Versión | Notas |
|---|---|---|---|
| Lenguaje | Python | 3.11 | |
| Framework Web/UI | Streamlit | ≥1.31 (actual 1.59) | Single-page app con `st.session_state` como router |
| Base de Datos | SQLite 3 | Built-in | WAL mode, FK enabled |
| ORM / Acceso a Datos | `sqlite3` (stdlib) | — | Sin ORM. `row_factory = sqlite3.Row` + conversión manual |
| Autenticación | bcrypt | 5.0 | 12 rounds, bloqueo tras 5 intentos |
| ML — Clasificación | XGBoost | ≥2.0 | Early Fusion y Late Fusion |
| ML — NLP | BERT-es (beto) | — | Embeddings 768-dim vía `transformers` |
| ML — Preprocesamiento | scikit-learn | ≥1.4 | StandardScaler, OneHotEncoder, ColumnTransformer |
| ML — Explicabilidad | SHAP | ≥0.44 | TreeExplainer + waterfall plots |
| ML — Serialización | joblib | ≥1.3 | `.pkl` para modelo, scaler, encoder |
| Gráficos | matplotlib | ≥3.8 | SHAP plots |
| Datos | pandas, numpy | ≥2.1, ≥1.26 | Procesamiento de features |

### 2.1 Dependencias Completas (`requirements.txt`)

```
streamlit>=1.31
pandas>=2.1
numpy>=1.26
scikit-learn>=1.4
xgboost>=2.0
shap>=0.44
joblib>=1.3
matplotlib>=3.8
bcrypt>=4.1
python-dotenv>=1.0
```

---

## 3. Base de Datos

### 3.1 Motor y Configuración

```python
# app/data/database.py
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA journal_mode=WAL")    # Write-Ahead Logging
conn.execute("PRAGMA foreign_keys=ON")     # Integridad referencial
conn.row_factory = sqlite3.Row              # Acceso por nombre de columna
```

**Decisiones:**
- **WAL mode:** Permite lecturas concurrentes mientras se escribe.
- **Foreign keys ON:** Evita huérfanos entre Paciente → EventoTriaje → SignosVitales/EvaluacionClinica.
- **Sin ORM:** Control total del SQL. La conversión PascalCase↔snake_case se hace con `_pascal_to_snake()`.

### 3.2 Conversión de Nombres (PascalCase ↔ snake_case)

El schema SQL usa **PascalCase** (`IdPaciente`, `NivelSugeridoIA`). El código Python usa **snake_case** (`id_paciente`, `nivel_sugerido_ia`). La conversión la hacen:

```python
def _pascal_to_snake(name: str) -> str:
    s1 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)   # "IdPaciente" → "Id_Paciente"
    s2 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s1)   # "IMC" → "IMC"
    return s2.lower()                                      # → "id_paciente"

def row_to_dict(row: sqlite3.Row) -> dict:
    return {_pascal_to_snake(k): row[k] for k in row.keys()} if row else None
```

**IMPORTANTE para desarrolladores:** Al añadir nuevas columnas al schema, usar PascalCase en el SQL. La conversión a snake_case es automática al leer.

### 3.3 Migraciones Incrementales

El sistema soporta migraciones no destructivas. Se ejecutan en `init_db()` después del schema:

```python
def _apply_migrations(conn):
    migraciones = [
        "ALTER TABLE Paciente ADD COLUMN Nombres TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE Paciente ADD COLUMN Apellidos TEXT NOT NULL DEFAULT ''",
        # ... 7 más para Épica 7
    ]
    for sql in migraciones:
        try:
            conn.execute(sql)
        except sqlite3.OperationalError:
            pass  # Columna ya existe
```

**Para añadir una nueva columna:** Agregarla al `CREATE TABLE` Y también a la lista de migraciones.

### 3.4 Índices

```sql
CREATE INDEX idx_paciente_documento ON Paciente(NumeroDocumento);
CREATE INDEX idx_triaje_paciente ON EventoTriaje(IdPaciente);
CREATE INDEX idx_triaje_estado ON EventoTriaje(Estado);
CREATE INDEX idx_auditoria_fecha ON Auditoria(FechaHora);
CREATE INDEX idx_auditoria_usuario ON Auditoria(Usuario);
CREATE INDEX idx_auditoria_accion ON Auditoria(Accion);
CREATE INDEX idx_prediccion_triaje ON PrediccionIA(IdTriaje);
CREATE INDEX idx_modelo_estado ON Modelo(Estado);
CREATE INDEX idx_usuario_nombre ON Usuario(NombreUsuario);
CREATE INDEX idx_control_cambios_entidad ON ControlCambios(Entidad, IdEntidad);
CREATE INDEX idx_control_cambios_documento ON ControlCambios(NumeroDocumento);
CREATE INDEX idx_control_cambios_fecha ON ControlCambios(FechaHora);
```

### 3.5 Datos Semilla

5 usuarios demo + 5 configuraciones del sistema. Todos usan contraseña `admin123` con bcrypt $2b$12$.

---

## 4. Servicios (Business Logic)

### 4.1 AuthService (`app/services/auth_service.py`)

**Propósito:** Autenticación, autorización RBAC, gestión de sesiones, recuperación de contraseña.

| Método | Firma | Retorno | Descripción |
|---|---|---|---|
| `login` | `(username, password)` | `Optional[Dict]` | Autentica. Bloquea tras 5 intentos. Retorna dict con `id_usuario, nombre_usuario, rol, email`. |
| `logout` | `()` | `None` | Limpia `st.session_state.user`. |
| `get_allowed_pages` | `(rol)` | `List[str]` | Páginas permitidas para un rol. |
| `check_permission` | `(rol, page)` | `bool` | ¿Tiene acceso a esta página? |
| `create_user` | `(admin_id, username, password, email, rol)` | `Optional[str]` | Crea usuario (solo Admin). Retorna ID. |
| `update_user` | `(admin_id, target_id, email, rol, activo)` | `bool` | Actualiza campos editables. |
| `update_user_role` | `(admin_id, target_id, new_rol)` | `bool` | Wrapper de `update_user()`. |
| `reset_password` | `(admin_id, target_id)` | `Optional[str]` | Genera contraseña aleatoria 8 chars. Retorna en texto plano. |
| `deactivate_user` | `(admin_id, target_id)` | `bool` | Soft delete (Activo=0). |
| `list_users` | `()` | `List[Dict]` | Todos los usuarios con datos. |
| `generate_reset_token` | `(username_or_email)` | `Optional[str]` | Token de 32 bytes URL-safe. |
| `check_session_timeout` | `()` | `bool` | ¿Sesión expirada? (>15 min). |
| `get_timeout_minutes` | `()` | `int` | Minutos de timeout configurados. |

**Permisos RBAC:**

```python
ROLE_PERMISSIONS = {
    "Administrador": ["RegistroPaciente", "SignosVitales", "EvaluacionClinica",
        "ClasificacionIA", "Dashboard", "GestionModelos",
        "ComparacionModelos", "Auditoria", "GestionUsuarios"],
    "Medico": ["RegistroPaciente", "SignosVitales", "EvaluacionClinica",
        "ClasificacionIA", "Dashboard"],
    "Enfermera": ["RegistroPaciente", "SignosVitales", "EvaluacionClinica",
        "ClasificacionIA"],
    "Investigador": ["Dashboard", "ComparacionModelos"],
    "Auditor": ["Auditoria", "Dashboard"],
}
```

### 4.2 PatientService (`app/services/patient_service.py`)

**Propósito:** CRUD de pacientes, búsqueda, historial de triajes, control de cambios.

| Método | Descripción |
|---|---|
| `register_patient(...)` | Registra nuevo paciente con 20 campos. Lanza `DuplicatePatientError` si el documento ya existe. |
| `search_patients(query, tipo_doc, limit)` | Búsqueda por documento, nombres o apellidos (LIKE). |
| `get_patient_by_document(num_doc)` | Búsqueda exacta por documento. |
| `get_patient_by_id(id)` | Búsqueda por ID interno. |
| `get_patient_triage_history(id)` | Historial de triajes con signos vitales y evaluación clínica. |
| `update_episodios_previos(id)` | Recalcula contador de episodios desde EventoTriaje. |
| `search_triages_by_documento(doc, limit)` | Triajes por documento (JOIN Paciente). |
| `get_active_triages_by_documento(doc)` | Triajes activos (≠ Cerrado/Cancelado). |
| `registrar_cambio(entidad, id, campo, val_ant, val_nuevo, ...)` | Inserta en ControlCambios con versionado. |
| `get_historial_cambios(entidad, id, doc, limit)` | Consulta historial con filtros. |

**Catálogos exportados:** `TIPOS_DOCUMENTO`, `VIAS_LLEGADA`, `REGIMENES_SALUD`, `SEXOS`, `DEPARTAMENTOS_COLOMBIA` (32), `CIUDADES_POR_DEPARTAMENTO` (108).

### 4.3 TriageService (`app/services/triage_service.py`)

**Propósito:** Máquina de estados del triaje, signos vitales, evaluación clínica, reclasificación, cierre.

| Método | Descripción |
|---|---|
| `create_triage_event(id_paciente, profesional)` | Crea triaje en estado "Registrado". |
| `get_triage_event(id)` | Obtiene triaje con JOIN de Paciente + SignosVitales + EvaluacionClinica. |
| `get_active_triage_for_patient(id)` | Busca triaje activo (≠ Cerrado/Cancelado). |
| `transition_state(id, nuevo_estado, usuario)` | Valida y ejecuta transición de estado. |
| `save_vital_signs(id, datos)` | Guarda/actualiza signos vitales. Calcula IMC. |
| `get_vital_signs(id)` | Obtiene signos vitales de un triaje. |
| `save_clinical_evaluation(id, datos)` | Guarda evaluación clínica. |
| `get_clinical_evaluation(id)` | Obtiene evaluación clínica. |
| `reclassify(id, nuevo_nivel, usuario, motivo)` | Reclasifica un triaje ya clasificado. |
| `close_event(id, usuario, motivo)` | Cierra triaje (estado terminal). |

**Máquina de Estados:**

```
Registrado → EnEvaluacion → PendienteIA → Clasificado → Validado → Cerrado
    ↓             ↓              ↓             ↓            ↓
Cancelado    Cancelado      Cancelado     Cancelado    Cancelado
    ↓ (reactivable)
Registrado
```

**Transiciones válidas:** Definidas en `TRANSICIONES_VALIDAS: Dict[str, List[str]]`.

**Catálogos exportados:** `RANGOS_VITALES`, `ALERTAS_VITALES`, `NIVELES_TRIAGE`, `NIVELES_LABELS`, `NIVELES_CONCIENCIA`, `MOTIVOS_CATEGORIA`.

### 4.4 InferenceService (`app/services/inference_service.py`)

**Propósito:** Carga del modelo ML, construcción del vector de features, predicción multimodal, explicación SHAP.

| Método | Descripción |
|---|---|
| `load_model(model_dir)` | Carga modelo XGBoost + transformadores + metadata. |
| `predict(triage_data)` | Predicción completa: features → inferencia → SHAP. |
| `explain(features, model)` | Genera explicación SHAP con waterfall plot. |
| `_build_feature_vector(data)` | Construye vector 768-dim + variables estructuradas. |
| `_preprocess(data)` | Limpieza, imputación, encoding, escalado. |
| `_apply_thresholds(probas)` | Aplica umbrales calibrados por clase. |
| `_enrich_explanation(shap_values)` | Traduce nombres de variables a etiquetas clínicas en español. |

**Singleton:** `get_inference_service()` retorna la instancia única (carga lazy del modelo).

**Modo Degradado:** Si el modelo no está disponible, `predict()` retorna `None` y el sistema continúa solo con clasificación manual del profesional.

### 4.5 AuditService (`app/services/audit_service.py`)

**Propósito:** Registro de auditoría append-only, consulta con filtros, exportación.

| Método | Descripción |
|---|---|
| `register(usuario, accion, entidad, id_entidad, ...)` | Inserta registro de auditoría. |
| `query(filtros)` | Consulta con 6 filtros + paginación. |
| `export_csv(filtros)` | Exporta resultados a CSV. |
| `export_excel_dataframe(filtros)` | Exporta a Excel (DataFrame). |
| `generate_triage_report(id_triaje)` | Genera reporte completo de un triaje. |

**Acciones auditables:** `LOGIN`, `LOGOUT`, `CREAR_PACIENTE`, `ACTUALIZAR_PACIENTE`, `SIGNOS_VITALES`, `EVALUACION_CLINICA`, `CLASIFICACION_IA`, `VALIDAR_TRIAJE`, `CERRAR_TRIAJE`, `RECLASIFICAR`, `CREAR_USUARIO`, `ACTUALIZAR_USUARIO`, `DESACTIVAR_USUARIO`, `ACTIVAR_MODELO`, `EXPORTAR_DATOS`, `CONSULTAR_AUDITORIA`, `RESET_PASSWORD`.

---

## 5. Páginas UI (app/ui/)

| Archivo | Función | Página | Roles |
|---|---|---|---|
| `login_page.py` | `render_login(auth)` | P01 — Login | Todos (pública) |
| `patient_page.py` | `render_patient_registration()` | P02 — Registro/Búsqueda de Paciente | Admin, Médico, Enfermera |
| `vital_signs_page.py` | `render_vital_signs()` | P03 — Signos Vitales | Admin, Médico, Enfermera |
| `clinical_eval_page.py` | `render_clinical_evaluation()` | P04 — Evaluación Clínica | Admin, Médico, Enfermera |
| `ia_classification_page.py` | `render_ia_classification()` | P05/P06 — Clasificación IA + SHAP | Admin, Médico, Enfermera |
| `triage_validation_page.py` | `render_triage_validation()` | P07 — Validación y Cierre | Admin, Médico, Enfermera |
| `dashboard_page.py` | `render_dashboard()` | P10 — Dashboard Operativo | Admin, Médico, Investigador, Auditor |
| `model_management_page.py` | `render_model_management()` | P09 — Gestión Modelos | Admin |
| `model_comparison_page.py` | `render_model_comparison()` | P08 — Comparar Modelos | Admin, Investigador |
| `audit_page.py` | `render_audit()` | P11 — Auditoría | Admin, Auditor |
| `user_management_page.py` | `render_user_management(auth)` | P12 — Gestión Usuarios | Admin |
| `control_cambios_page.py` | `render_control_cambios()` | P13 — Control de Cambios | Admin |
| `historico_paciente_page.py` | `render_historico_paciente()` | P14 — Histórico del Paciente | Todos |

### 5.1 Convenciones de UI

- Cada página es una **función** `render_*()` que recibe servicios como parámetros o los instancia desde `st.session_state`.
- El **estado global** está en `st.session_state`: `user`, `page`, `db_path`, `triaje_activo`, `paciente_activo`, `app_config`, `app_initialized`.
- La **navegación** es por `st.session_state.page` (string). El router en `app.py` hace `if/elif` para renderizar la página correspondiente.
- El **sidebar** se renderiza en `app.py` con `st.sidebar` y muestra botones según `roles_permitidos`.
- **Indicador de flujo:** `_render_flow_indicator(paso)` muestra los 6 pasos del triaje con el paso actual resaltado.

---

## 6. Flujo de Datos

### 6.1 Ciclo de Vida de un Triaje

```
1. POST paciente    → INSERT Paciente
2. POST triaje      → INSERT EventoTriaje (Estado=Registrado)
3. PUT signos       → INSERT/UPDATE SignosVitales → Estado: EnEvaluacion
4. PUT evaluación   → INSERT/UPDATE EvaluacionClinica → Estado: PendienteIA
5. POST inferencia  → INSERT PrediccionIA + ExplicacionSHAP → Estado: Clasificado
6. PUT validación   → UPDATE EventoTriaje (NivelAsignado, Concordancia) → Estado: Validado
7. PUT cierre       → UPDATE EventoTriaje (FechaHoraCierre) → Estado: Cerrado
```

### 6.2 Flujo de Inferencia IA

```
Datos clínicos (SignosVitales + EvaluacionClinica)
    │
    ▼
_build_feature_vector()
    ├── Variables estructuradas (numéricas + categóricas)
    │   └── Scaler + Encoder (cargados del modelo)
    ├── Embeddings NLP (MotivoTextoLibre)
    │   └── Tokenizer BERT-es (cargado del modelo)
    └── Vector combinado (Early Fusion = concatenación)
    │
    ▼
model.predict_proba() → 5 probabilidades [I, II, III, IV, V]
    │
    ▼
_apply_thresholds() → Nivel sugerido (argmax calibrado)
    │
    ▼
SHAP TreeExplainer → Valores SHAP por variable → Waterfall plot
    │
    ▼
_enrich_explanation() → Etiquetas clínicas en español
```

---

## 7. Router y Navegación (`app.py`)

### 7.1 Estructura del Router

```python
page = st.session_state.get("page", "login")

if page == "login" or "user" not in st.session_state or st.session_state.user is None:
    render_login(auth)
elif page == "registro_paciente":
    render_patient_registration()
elif page == "signos_vitales":
    render_vital_signs()
# ... 11 páginas más
```

### 7.2 Inicialización (una sola vez por sesión)

```python
if "app_initialized" not in st.session_state:
    cfg = load_config()
    st.session_state.db_path = get_db_path(cfg)
    init_db(st.session_state.db_path)
    st.session_state.auth_service = AuthService(st.session_state.db_path)
    st.session_state.app_initialized = True
```

### 7.3 Recarga Forzada de Módulos

Para evitar el caché stale de Streamlit, `app.py` elimina módulos de `sys.modules` y usa `importlib.reload()` al inicio:

```python
for prefix in ("app.services.auth", "app.ui.login_page", "app.ui.patient_page", ...):
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith(prefix):
            del sys.modules[mod_name]
import app.services.auth_service as auth_mod
importlib.reload(auth_mod)
```

**Al añadir una nueva página UI, agregar su prefijo a esta lista.**

---

## 8. Configuración (`app/config/settings.py`)

### 8.1 Variables de Entorno (.env)

```bash
DB_PATH=data/triaje.db
SESSION_TIMEOUT_MINUTES=15
BCRYPT_ROUNDS=12
MODEL_PATH=models
ACTIVE_MODEL=xgboost_early_fusion_v1
ENV=development
LOG_LEVEL=INFO
```

### 8.2 Funciones

```python
def load_config() -> dict:
    # Carga .env con python-dotenv, retorna dict con defaults.

def get_db_path(cfg: dict) -> str:
    # Resuelve ruta absoluta, crea directorio data/ si no existe.
```

---

## 9. Pipeline ML (src/)

### 9.1 Estructura

```
src/
├── __init__.py
├── data/
│   ├── ingesta.py          # Carga de datasets
│   ├── limpieza.py         # Validación, imputación, encoding
│   └── anonimizacion.py    # Eliminación de datos sensibles
├── features/
│   └── nlp_embeddings.py   # Generación de embeddings BERT-es
├── models/
│   └── train_models.py     # Entrenamiento XGBoost (Early/Late Fusion)
├── evaluation/
│   ├── metrics.py          # F1, AUC-ROC, AUPRC, matriz de confusión
│   └── shap_benchmarks.py  # Explicabilidad SHAP + benchmarks literatura
└── serving/
    └── serialize.py        # Serialización/deserialización de artefactos
```

### 9.2 Serialización de Modelos

```python
# src/serving/serialize.py
class ModelSerializer:
    @staticmethod
    def save(output_dir, model, scaler, encoder, tokenizer, metrics, thresholds, ...):
        # Guarda model.pkl, scaler.pkl, encoder.pkl, tokenizer/, metadata.json

    @staticmethod
    def load(model_dir) -> Dict[str, Any]:
        # Carga todos los artefactos y retorna dict con modelo + transformadores

    @staticmethod
    def load_active_model(models_dir=None) -> Dict[str, Any]:
        # Busca el modelo activo en BD y lo carga
```

---

## 10. Guía para Desarrolladores

### 10.1 Cómo Añadir una Nueva Página

1. Crear `app/ui/nueva_pagina.py` con función `render_nueva_pagina()`.
2. Agregar ruta en `app.py`:
   ```python
   elif page == "nueva_pagina":
       from app.ui.nueva_pagina import render_nueva_pagina
       render_nueva_pagina()
   ```
3. Agregar botón en el sidebar (sección correspondiente).
4. Si requiere permisos, agregar a `ROLE_PERMISSIONS` en `auth_service.py`.
5. Agregar `"app.ui.nueva_pagina"` a la lista de prefijos en `app.py` (recarga de módulos).

### 10.2 Cómo Añadir una Nueva Columna a la BD

1. Agregar la columna al `CREATE TABLE` en `SCHEMA_SQL` (`database.py`).
2. Agregar `ALTER TABLE ADD COLUMN ...` a la lista `migraciones` en `_apply_migrations()`.
3. Usar **PascalCase** en el SQL. La conversión a snake_case es automática.
4. Actualizar los métodos del servicio que usan esa tabla (INSERT, SELECT).
5. Si la columna se expone en UI, actualizar la página correspondiente.

### 10.3 Cómo Añadir un Nuevo Rol

1. Agregar a `CHECK(Rol IN (...))` en `CREATE TABLE Usuario`.
2. Agregar entrada en `ROLE_PERMISSIONS`.
3. Agregar a `ROLES_LABELS` en los archivos UI que muestren roles.
4. Si aplica, agregar a la lista de roles permitidos en `user_management_page.py` (`ROLES_DISPONIBLES`).

### 10.4 Cómo Añadir un Nuevo Estado al Triaje

1. Agregar a `CHECK(Estado IN (...))` en `CREATE TABLE EventoTriaje`.
2. Definir transiciones válidas en `TRANSICIONES_VALIDAS`.
3. Agregar lógica de transición en `TriageService.transition_state()`.
4. Actualizar UI en las páginas que muestran/validan estados.

### 10.5 Cómo Registrar un Nuevo Modelo ML

1. Entrenar el modelo con `run_pipeline.py` o manualmente.
2. El artefacto se guarda en `models/nombre_modelo/` con `ModelSerializer.save()`.
3. En la app: ⚙️ Gestión Modelos → Pestaña Disco → Seleccionar carpeta → Registrar en BD.
4. En la BD: El modelo aparece con Estado "EnValidacion".
5. Revisar métricas en 🔬 Comparar Modelos.
6. Activar desde ⚙️ Gestión Modelos → Pestaña BD → Activar.

### 10.6 Debugging

- **Logs de Streamlit:** Aparecen en la terminal donde se ejecuta `streamlit run`.
- **Errores de importación:** Verificar que el módulo esté en la lista de recarga de `app.py`.
- **Errores de BD:** El archivo `data/triaje.db` se recrea automáticamente al borrarlo. Los datos semilla se insertan con `INSERT OR IGNORE`.
- **Caché stale:** Si los cambios no se reflejan, matar Streamlit, borrar `__pycache__/` y reiniciar con `PYTHONDONTWRITEBYTECODE=1`.

### 10.7 Variables de Sesión (st.session_state)

| Variable | Tipo | Descripción |
|---|---|---|
| `user` | `dict` | Datos del usuario logueado (`id_usuario`, `nombre_usuario`, `rol`, `email`) |
| `page` | `str` | Página activa (`"login"`, `"registro_paciente"`, etc.) |
| `db_path` | `str` | Ruta absoluta al archivo SQLite |
| `triaje_activo` | `str` | `IdTriaje` del triaje en curso |
| `paciente_activo` | `str` | `IdPaciente` del paciente en curso |
| `app_config` | `dict` | Configuración cargada de `.env` |
| `app_initialized` | `bool` | `True` después de la primera inicialización |
| `login_time` | `datetime` | Momento del último login |
| `patient_service` | `PatientService` | Instancia cacheada del servicio |
| `triage_service` | `TriageService` | Instancia cacheada del servicio |

---

## 11. Endpoints y Puertos

| Servicio | Puerto | URL |
|---|---|---|
| Streamlit App | 8501 | `http://localhost:8501` |

**La app es standalone — no expone API REST. Toda la lógica se ejecuta en el mismo proceso Python de Streamlit.**

---

## 12. Instalación y Ejecución

### 12.1 Requisitos Previos

- Python 3.11+
- pip 23+
- Git (opcional)

### 12.2 Instalación

```bash
cd sistema-triaje-ia
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Linux/Mac
pip install -r requirements.txt
```

### 12.3 Ejecución

```bash
streamlit run app.py --server.port 8501
```

### 12.4 Variables de Entorno

Copiar `.env.example` a `.env` y ajustar según el entorno.

---

## 13. Estándares de Código

- **Idioma:** Código en español (variables, funciones, comentarios). Nombres de columnas SQL en PascalCase.
- **Formato:** snake_case para funciones, variables y archivos Python.
- **Tipado:** Type hints en todas las firmas de servicios (`Optional`, `Dict`, `List`).
- **Docstrings:** Cada método público debe tener docstring descriptivo.
- **Errores:** Excepciones específicas (`DuplicatePatientError`, `ValueError`) con mensajes en español.
- **UI:** Cada pantalla tiene un `st.title()` y `st.caption()` con el número de paso y descripción.

---

**TFM · UNIR · Máster en Inteligencia Artificial · v1.0 Demo**
