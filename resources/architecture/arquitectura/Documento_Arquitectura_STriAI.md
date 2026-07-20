# Documento de Arquitectura — STriAI (Sistema de Triaje Multimodal IA)

**TFM UNIR — Máster en Inteligencia Artificial**
**Versión:** 1.0 — Julio 2026
**Tipo:** Documentación AS-IS (Caso B)

---

## Tabla de Contenido

1. [Introducción y Objetivos](#1-introducción-y-objetivos)
2. [Restricciones y Decisiones Arquitectónicas](#2-restricciones-y-decisiones-arquitectónicas)
3. [Contexto del Sistema (C4 Nivel 1)](#3-contexto-del-sistema-c4-nivel-1)
4. [Contenedores (C4 Nivel 2)](#4-contenedores-c4-nivel-2)
5. [Componentes (C4 Nivel 3)](#5-componentes-c4-nivel-3)
6. [Código — Nivel de Clases (C4 Nivel 4)](#6-código--nivel-de-clases-c4-nivel-4)
7. [Diagramas de Secuencia](#7-diagramas-de-secuencia)
8. [Modelo de Datos](#8-modelo-de-datos)
9. [Arquitectura de Machine Learning](#9-arquitectura-de-machine-learning)
10. [Arquitectura de Despliegue](#10-arquitectura-de-despliegue)
11. [Seguridad y Autenticación](#11-seguridad-y-autenticación)
12. [Deuda Técnica y Hallazgos](#12-deuda-técnica-y-hallazgos)
13. [ADRs (Architecture Decision Records)](#13-adrs-architecture-decision-records)
14. [Supuestos](#14-supuestos)

---

## 1. Introducción y Objetivos

### 1.1 Propósito del Sistema

STriAI (Sistema de Triaje Multimodal IA) es una aplicación diseñada como Trabajo de Fin de Máster (TFM) para la UNIR. Su objetivo es asistir a profesionales de la salud en la clasificación de pacientes en servicios de urgencias mediante niveles de triaje I-V (Resolución 5596/2015 de Colombia), combinando **datos clínicos estructurados** (signos vitales, datos demográficos) con **procesamiento de lenguaje natural** (NLP) sobre el motivo de consulta en texto libre.

### 1.2 Objetivos de Arquitectura

| Atributo | Prioridad | Meta |
|---|---|---|
| **Funcionalidad** | Crítica | Registrar pacientes, capturar signos vitales, clasificar con IA, validar por profesional |
| **Trazabilidad** | Alta | Auditoría inmutable de todas las acciones clínicas |
| **Portabilidad** | Alta | Ejecutable en una laptop sin infraestructura cloud |
| **Explicabilidad** | Alta | Cada predicción de IA debe ser explicable (SHAP) |
| **Seguridad** | Media | Autenticación con roles, contraseñas hasheadas |
| **Rendimiento** | Baja | Inferencia < 5 segundos en CPU (no es sistema de tiempo real) |
| **Escalabilidad** | Baja | Sistema demo/monousuario (no production-grade) |

### 1.3 Stakeholders

| Stakeholder | Interés |
|---|---|
| Tribunal TFM UNIR | Evaluar la integración de IA en un sistema clínico funcional |
| Director/a de TFM | Supervisar la calidad técnica y académica |
| Desarrollador/Estudiante | Implementar y demostrar competencias en ML, NLP, y desarrollo full-stack |
| Usuarios demo (médicos, enfermeras) | Probar flujo clínico con datos sintéticos/reales |

---

## 2. Restricciones y Decisiones Arquitectónicas

### 2.1 Restricciones Técnicas

| ID | Restricción | Impacto |
|---|---|---|
| RT-001 | Python 3.11 como único lenguaje | Stack uniforme pero sin tipado fuerte |
| RT-002 | Streamlit como framework UI | Single-page app, sin SPA ni SSR tradicional |
| RT-003 | SQLite como base de datos | Sin concurrencia real, sin cliente-servidor |
| RT-004 | Ejecución en CPU (sin GPU obligatoria) | Inferencia NLP lenta (~1-2s por texto) |
| RT-005 | Datasets del sistema de salud colombiano | Pocas features clínicas, datasets no balanceados |
| RT-006 | Sin ORM — SQL directo | Acoplamiento a SQLite, sin migraciones automáticas |

### 2.2 Decisiones Arquitectónicas Clave

| ID | Decisión | Justificación |
|---|---|---|
| ADR-001 | **Monolito en capas** sobre Streamlit | Adecuado para prototipo/demo; microservicios sería sobrediseño |
| ADR-002 | **SQLite con WAL + FK ON** | Portátil, cero configuración, suficiente para monousuario |
| ADR-003 | **PascalCase en BD → snake_case en Python** | Convención SQL estándar vs. PEP 8; conversión automática |
| ADR-004 | **Modelo ML serializado en joblib** | Carga rápida, sin servidor de modelos separado |
| ADR-005 | **5 roles RBAC hardcodeados** | Suficiente para demo; roles dinámicos serían sobrediseño |
| ADR-006 | **Pipeline ML como script offline** | Separación clara entrenamiento/inferencia; no requiere MLOps |
| ADR-007 | **Early Fusion como arquitectura ML** | Mejor F1 Macro en experimentos; simplicidad sobre Late Fusion |

---

## 3. Contexto del Sistema (C4 Nivel 1)

### 3.1 Diagrama de Contexto

```mermaid
C4Context
    title Diagrama de Contexto — STriAI (Nivel C1)

    Person(profesional, "Profesional de Salud", "Médico, enfermero o administrador que utiliza el sistema de triaje")
    Person(auditor, "Auditor", "Revisa registros de auditoría y genera reportes")
    
    System(striai, "STriAI — Sistema de Triaje Multimodal IA", "Permite registrar pacientes, capturar signos vitales, clasificar con IA el nivel de triaje (I-V), y validar por profesional. Incluye dashboard, auditoría y gestión de usuarios.")

    System_Ext(huggingface, "HuggingFace Hub", "Repositorio de modelos NLP pre-entrenados (BERT multilingüe)")
    System_Ext(datagov, "datos.gov.co", "Fuente de datasets abiertos del sistema de salud colombiano")
    
    Rel(profesional, striai, "Registra pacientes, captura signos vitales, clasifica y valida triaje", "HTTPS/Web (Streamlit)")
    Rel(auditor, striai, "Consulta auditoría y exporta reportes", "HTTPS/Web (Streamlit)")
    Rel(striai, huggingface, "Descarga modelo NLP para embeddings", "HTTPS (offline/entrenamiento)")
    Rel(striai, datagov, "Ingesta de datasets CSV para entrenamiento", "HTTP (offline/entrenamiento)")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### 3.2 Actores del Sistema

| Actor | Descripción | Interacciones |
|---|---|---|
| **Profesional de Salud** | Médico, enfermero o administrador | Registro de pacientes, signos vitales, clasificación IA, validación de triaje |
| **Auditor** | Personal de control y calidad | Consulta de logs de auditoría, exportación CSV/Excel, reportes |
| **HuggingFace Hub** (externo) | Repositorio de modelos NLP | Descarga de BERT multilingüe para embeddings (solo en entrenamiento) |
| **datos.gov.co** (externo) | Portal de datos abiertos Colombia | Fuente de datasets CSV para entrenamiento del modelo |

---

## 4. Contenedores (C4 Nivel 2)

### 4.1 Diagrama de Contenedores

```mermaid
C4Container
    title Diagrama de Contenedores — STriAI (Nivel C2)

    Person(profesional, "Profesional de Salud", "Médico/Enfermero/Admin")
    Person(auditor, "Auditor", "Control y calidad")

    System_Boundary(striai_boundary, "STriAI — Sistema de Triaje Multimodal IA") {
        Container(streamlit_app, "Aplicación Streamlit", "Python 3.11 + Streamlit 1.59", "Interfaz web con 14 pantallas. Router de páginas, sidebar con RBAC, gestión de sesión en st.session_state.")
        Container(sqlite_db, "Base de Datos SQLite", "SQLite 3 (WAL mode)", "12 tablas: Paciente, EventoTriaje, SignosVitales, EvaluacionClinica, PrediccionIA, Usuario, Auditoria, etc. 11 índices.")
        Container(ml_inference, "Servicio de Inferencia ML", "Python + XGBoost + SHAP", "Carga modelo serializado (joblib), preprocesa datos, ejecuta predicción y explicabilidad SHAP. Singleton en memoria.")
        Container(ml_pipeline, "Pipeline de Entrenamiento ML", "Python CLI (run_pipeline.py)", "Script offline de 14 pasos: ingesta → limpieza → NLP → entrenamiento → evaluación → serialización. No se ejecuta en la demo.")
    }

    System_Ext(huggingface, "HuggingFace Hub", "Modelos NLP pre-entrenados")
    System_Ext(datagov, "datos.gov.co", "Datasets CSV abiertos")

    Rel(profesional, streamlit_app, "Usa la aplicación web", "HTTPS :8501")
    Rel(auditor, streamlit_app, "Consulta auditoría", "HTTPS :8501")
    Rel(streamlit_app, sqlite_db, "SQL directo (lectura/escritura)", "SQLite3 API")
    Rel(streamlit_app, ml_inference, "Llama a predict() y explain()", "Python API (in-process)")
    Rel(ml_inference, sqlite_db, "Lee datos de paciente para features", "SQLite3 API")
    Rel(ml_pipeline, datagov, "Descarga datasets CSV", "HTTPS (manual)")
    Rel(ml_pipeline, huggingface, "Descarga modelo BERT", "HTTPS")
    Rel(ml_pipeline, sqlite_db, "No interactúa — datasets independientes", "")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### 4.2 Descripción de Contenedores

| Contenedor | Tecnología | Responsabilidad |
|---|---|---|
| **Aplicación Streamlit** | Python 3.11, Streamlit 1.59 | UI, ruteo, autenticación, orquestación de flujos clínicos |
| **Base de Datos SQLite** | SQLite 3 (WAL, FK ON) | Persistencia de pacientes, triajes, usuarios, auditoría |
| **Servicio de Inferencia ML** | Python, XGBoost, SHAP, joblib | Carga de modelo, predicción de nivel de triaje, explicabilidad |
| **Pipeline de Entrenamiento** | Python CLI, scikit-learn, XGBoost, PyTorch, Transformers | Entrenamiento offline de modelos (no parte de la demo) |

---

## 5. Componentes (C4 Nivel 3)

### 5.1 Diagrama de Componentes — Aplicación Streamlit

```mermaid
C4Component
    title Diagrama de Componentes — Aplicación Streamlit (Nivel C3)

    Container_Boundary(app_boundary, "Aplicación Streamlit") {
        Component(router, "Router de Páginas", "app.py", "Gestiona navegación entre 14 pantallas vía st.session_state.page. Importlib.reload() para evitar caché stale.")
        Component(auth_svc, "AuthService", "app/services/auth_service.py", "Login/logout, RBAC (5 roles, 14 permisos), gestión de usuarios, reset password, timeout de sesión.")
        Component(patient_svc, "PatientService", "app/services/patient_service.py", "Registro de pacientes (21 campos), búsqueda por documento/nombre, histórico de triajes, catálogos geográficos.")
        Component(triage_svc, "TriageService", "app/services/triage_service.py", "Máquina de estados (7 estados, 14 transiciones), signos vitales, evaluación clínica, validación profesional.")
        Component(inference_svc, "InferenceService", "app/services/inference_service.py", "Predict() y explain() usando modelo XGBoost serializado. Singleton global get_inference_service().")
        Component(audit_svc, "AuditService", "app/services/audit_service.py", "Registro inmutable (17 tipos de acciones), consultas con filtros, exportación CSV/Excel.")
        
        Component(login_page, "Login Page", "app/ui/login_page.py", "P01 — Autenticación con bypass bcrypt para demo accounts")
        Component(patient_page, "Patient Page", "app/ui/patient_page.py", "P02 — Registro y búsqueda de pacientes")
        Component(vitals_page, "Vital Signs Page", "app/ui/vital_signs_page.py", "P03 — Captura de 8 signos vitales")
        Component(clinical_page, "Clinical Eval Page", "app/ui/clinical_eval_page.py", "P04 — Evaluación clínica (Glasgow, dolor, comorbilidades)")
        Component(ia_page, "IA Classification Page", "app/ui/ia_classification_page.py", "P05/P06 — Clasificación IA + explicación SHAP")
        Component(validation_page, "Triage Validation Page", "app/ui/triage_validation_page.py", "P07 — Validación profesional y cierre")
        Component(dashboard_page, "Dashboard Page", "app/ui/dashboard_page.py", "P10 — KPIs operativos y gráficos")
        Component(admin_pages, "Admin Pages (4)", "app/ui/*.py", "P08-P09-P11-P12-P13-P14 — Gestión modelos, usuarios, auditoría, cambios, histórico")
    }

    Container_Boundary(db_boundary, "Base de Datos SQLite") {
        ComponentDb(db_conn, "Conexión SQLite", "app/data/database.py", "WAL mode, FK ON. 12 tablas, 11 índices. PascalCase→snake_case.")
    }

    Rel(router, auth_svc, "Autentica y autoriza", "Python call")
    Rel(router, login_page, "Renderiza si no autenticado", "")
    Rel(router, patient_page, "Renderiza P02", "")
    Rel(router, vitals_page, "Renderiza P03", "")
    Rel(router, clinical_page, "Renderiza P04", "")
    Rel(router, ia_page, "Renderiza P05/P06", "")
    Rel(router, validation_page, "Renderiza P07", "")
    Rel(router, dashboard_page, "Renderiza P10", "")
    Rel(router, admin_pages, "Renderiza P08-P14", "")
    
    Rel(patient_page, patient_svc, "Registra/busca pacientes", "")
    Rel(vitals_page, triage_svc, "Guarda signos vitales", "")
    Rel(clinical_page, triage_svc, "Guarda evaluación clínica", "")
    Rel(ia_page, inference_svc, "Predice y explica", "")
    Rel(validation_page, triage_svc, "Valida y cierra", "")
    Rel(dashboard_page, audit_svc, "Consulta métricas", "")
    
    Rel(auth_svc, db_conn, "SQL", "SQLite3")
    Rel(patient_svc, db_conn, "SQL", "SQLite3")
    Rel(triage_svc, db_conn, "SQL", "SQLite3")
    Rel(inference_svc, db_conn, "SQL (lectura features)", "SQLite3")
    Rel(audit_svc, db_conn, "SQL (append-only)", "SQLite3")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### 5.2 Diagrama de Componentes — Pipeline ML

```mermaid
C4Component
    title Diagrama de Componentes — Pipeline ML (Nivel C3)

    Container_Boundary(ml_boundary, "Pipeline de Entrenamiento ML") {
        Component(ingesta, "Data Ingestion", "src/data/ingesta.py", "Carga 4 fuentes CSV → unifica 9 columnas. Mapeo heurístico de nombres de columna. Limpieza de strings numéricos.")
        Component(anonim, "Anonymization", "src/data/anonimizacion.py", "Verifica ausencia de PII (nombres, documentos). Cumplimiento Ley 1581/2012.")
        Component(limpieza, "Data Cleaning", "src/data/limpieza.py", "Imputación, detección outliers fisiológicos (IQR), encoding (OneHot + StandardScaler), features derivadas.")
        Component(nlp_emb, "NLP Embeddings", "src/features/nlp_embeddings.py", "BERT multilingüe → 384-dim embeddings desde texto de motivo de consulta. Batch size=32, max_length=128.")
        Component(trainer, "Model Trainer", "src/models/train_models.py", "5 modelos: LR, RF, XGBoost (unimodal), Early Fusion, Late Fusion. StratifiedKFold CV.")
        Component(evaluator, "Evaluator", "src/evaluation/metrics.py", "F1 Macro, AUC-ROC, matriz confusión. Threshold tuning (prioriza Recall I-II).")
        Component(shap_exp, "SHAP Explainer", "src/evaluation/shap_benchmarks.py", "Explicabilidad (SHAP con fallback a feature_importances_). Comparativa contra benchmarks literatura.")
        Component(serializer, "Model Serializer", "src/serving/serialize.py", "joblib + metadata.json. active_version.txt. Hash SHA256 para integridad.")
    }

    Container_Boundary(data_boundary, "Fuentes de Datos") {
        ComponentDb(csv1, "CSV: Clasificación Triage", "89K filas", "datos.gov.co")
        ComponentDb(csv2, "CSV: San Juan de Dios", "43K filas", "Hospital Armenia")
        ComponentDb(csv3, "CSV: Morbilidad Urgencias", "43K filas", "datos.gov.co")
        ComponentDb(csv4, "CSV: Pitalito 2019", "102 filas", "ESE San Antonio")
        ComponentDb(models_dir, "Modelos Serializados", "models/", "joblib + JSON")
    }

    Rel(ingesta, csv1, "Lee CSV", "")
    Rel(ingesta, csv2, "Lee CSV", "")
    Rel(ingesta, csv3, "Lee CSV", "")
    Rel(ingesta, csv4, "Lee CSV (falla — pivote)", "")
    Rel(ingesta, anonim, "Pasa DataFrame", "176K filas")
    Rel(anonim, limpieza, "Pasa DataFrame", "176K filas")
    Rel(limpieza, nlp_emb, "Texto motivo consulta", "133K textos")
    Rel(limpieza, trainer, "X_train, y_train", "106K train")
    Rel(nlp_emb, trainer, "X_nlp_train (384d)", "106K embeddings")
    Rel(trainer, evaluator, "y_pred, y_proba", "")
    Rel(evaluator, shap_exp, "Mejor modelo + X_test", "")
    Rel(trainer, serializer, "Modelo ganador + scaler + encoder", "")
    Rel(serializer, models_dir, "Escribe joblib + JSON", "")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

---

## 6. Código — Nivel de Clases (C4 Nivel 4)

### 6.1 Diagrama de Clases — Servicios

```mermaid
classDiagram
    class AuthService {
        -db_path: str
        -ROLE_PERMISSIONS: dict
        +authenticate(username, password) dict
        +logout() None
        +get_allowed_pages(rol) List
        +check_permission(rol, page) bool
        +create_user(admin_id, username, ...) str
        +update_user(admin_id, target_id, ...) bool
        +reset_password(admin_id, target_id) str
        +deactivate_user(admin_id, target_id) bool
        +list_users() List~Dict~
        +generate_reset_token(username_or_email) str
        +check_session_timeout() bool
    }

    class PatientService {
        -db_path: str
        +register_patient(21 params) str
        +search_patients(query, tipo_doc, limit) List~Dict~
        +get_patient_history(id_paciente) List~Dict~
        +get_patient_by_document(numero) dict
        +get_patient_triage_history(id_paciente) List
        +get_active_triages_by_documento(numero) List
        +registrar_cambio(entidad, id_entidad, ...) None
        +get_historial_cambios(filtros) List~Dict~
        -_calcular_edad(fecha_nacimiento) int
        -_validar_telefono(telefono) bool
    }

    class TriageService {
        -db_path: str
        -STATE_TRANSITIONS: dict
        +create_triage_event(id_paciente, profesional) dict
        +get_triage_event(id_triaje) dict
        +get_active_triage_for_patient(id_paciente) dict
        +transition_state(id_triaje, nuevo_estado, ...) dict
        +save_vital_signs(id_triaje, 8 params) dict
        +save_clinical_evaluation(id_triaje, ...) dict
        +validate_classification(id_triaje, nivel, ...) dict
        +reclassify(id_triaje, nuevo_nivel, ...) dict
        +close_event(id_triaje, usuario) dict
    }

    class InferenceService {
        -models_dir: Path
        -model_loaded: bool
        -model: XGBoost
        -scaler: StandardScaler
        -encoder: OneHotEncoder
        -feature_names: List
        +load_model() bool
        +predict(clinical_data, motivo_texto) dict
        +explain(clinical_data, motivo_texto) dict
        +get_status() dict
        -_build_feature_vector(data) ndarray
        -_preprocess(X) ndarray
        -_apply_thresholds(y_proba) int
        -_enrich_explanation(shap_output, data) dict
    }

    class AuditService {
        -db_path: str
        +register(usuario, accion, ...) str
        +query(filtros) Tuple~List, int~
        +get_acciones_disponibles() List
        +export_csv(resultados) str
        +generate_triage_report(id_triaje) dict
    }

    class ReportService {
        +generate_triage_html(id_triaje) str
    }

    AuthService ..> AuditService : "registra login/logout"
    TriageService ..> AuditService : "registra transiciones"
    PatientService ..> AuditService : "registra creación"
    InferenceService ..> TriageService : "consulta datos paciente"
    ReportService ..> AuditService : "generate_triage_report()"
```

### 6.2 Diagrama de Clases — Base de Datos

```mermaid
classDiagram
    class Paciente {
        +IdPaciente: TEXT PK
        +TipoDocumento: TEXT
        +NumeroDocumento: TEXT UNIQUE
        +Nombres: TEXT
        +Apellidos: TEXT
        +FechaNacimiento: TEXT
        +Edad: INTEGER
        +Sexo: TEXT
        +Telefono: TEXT
        +Correo: TEXT
        +EPS: TEXT
        +RegimenSalud: TEXT
        +Departamento: TEXT
        +Ciudad: TEXT
        +DireccionResidencia: TEXT
        +ContactoEmergencia: TEXT
        +ViaLlegada: TEXT
        +EpisodiosPreviosUrgencias: INTEGER
        +FechaRegistro: TEXT
    }

    class EventoTriaje {
        +IdTriaje: TEXT PK
        +IdPaciente: TEXT FK
        +Estado: TEXT
        +NivelSugeridoIA: TEXT
        +NivelAsignadoProfesional: TEXT
        +ProbabilidadesIA: TEXT
        +Concordancia: INTEGER
        +MotivoDiscrepancia: TEXT
        +VersionModeloUsado: TEXT
        +ProfesionalResponsable: TEXT
        +FechaHoraIngreso: TEXT
        +FechaHoraClasificacion: TEXT
        +FechaHoraCierre: TEXT
        +FechaModificacion: TEXT
    }

    class SignosVitales {
        +IdSignosVitales: TEXT PK
        +IdTriaje: TEXT FK UNIQUE
        +Temperatura: REAL
        +FrecuenciaCardiaca: INTEGER
        +FrecuenciaRespiratoria: INTEGER
        +SaturacionO2: INTEGER
        +PresionSistolica: INTEGER
        +PresionDiastolica: INTEGER
        +Peso: REAL
        +Talla: REAL
        +IMC: REAL
    }

    class EvaluacionClinica {
        +IdEvaluacion: TEXT PK
        +IdTriaje: TEXT FK UNIQUE
        +MotivoTextoLibre: TEXT
        +MotivoCategoria: TEXT
        +EscalaDolor: INTEGER
        +Glasgow: INTEGER
        +NivelConciencia: TEXT
        +Diabetes: INTEGER
        +Hipertension: INTEGER
        +EnfermedadRenal: INTEGER
        +Embarazo: INTEGER
        +Cancer: INTEGER
        +Cardiopatias: INTEGER
        +EnfermedadPulmonar: INTEGER
        +CirugiasRecientes: INTEGER
        +MedicacionRelevante: TEXT
        +Alergias: TEXT
    }

    class PrediccionIA {
        +IdPrediccion: TEXT PK
        +IdTriaje: TEXT FK
        +IdModelo: TEXT
        +NivelPredicho: TEXT
        +Probabilidades: TEXT
        +Confianza: REAL
        +TiempoInferencia: REAL
    }

    class Usuario {
        +IdUsuario: TEXT PK
        +NombreUsuario: TEXT UNIQUE
        +PasswordHash: TEXT
        +Email: TEXT
        +Rol: TEXT
        +Activo: INTEGER
        +IntentosFallidos: INTEGER
        +BloqueadoHasta: TEXT
        +HistorialPasswords: TEXT
        +FechaCreacion: TEXT
        +UltimoAcceso: TEXT
    }

    class Auditoria {
        +IdAuditoria: TEXT PK
        +Usuario: TEXT
        +FechaHora: TEXT
        +Accion: TEXT
        +EntidadAfectada: TEXT
        +IdEntidad: TEXT
        +ValorAnterior: TEXT
        +ValorNuevo: TEXT
        +IP: TEXT
        +Observaciones: TEXT
    }

    class Modelo {
        +IdModelo: TEXT PK
        +Nombre: TEXT UNIQUE
        +Version: TEXT
        +Arquitectura: TEXT
        +Algoritmo: TEXT
        +Hiperparametros: TEXT
        +F1Score: REAL
        +Precision: REAL
        +Recall: REAL
        +AUCROC: REAL
        +Estado: TEXT
    }

    Paciente "1" -- "N" EventoTriaje : tiene
    EventoTriaje "1" -- "1" SignosVitales : registra
    EventoTriaje "1" -- "1" EvaluacionClinica : evaluado_con
    EventoTriaje "1" -- "1" PrediccionIA : clasificado_por
    Modelo "1" -- "N" PrediccionIA : usado_en
```

---

## 7. Diagramas de Secuencia

### 7.1 Flujo Principal — Registro y Triaje de Paciente

```mermaid
sequenceDiagram
    actor Profesional as 👨‍⚕️ Profesional
    participant UI as Streamlit UI
    participant Auth as AuthService
    participant Patient as PatientService
    participant Triage as TriageService
    participant IA as InferenceService
    participant DB as SQLite DB
    participant Audit as AuditService

    Note over Profesional,Audit: === FASE 1: LOGIN ===
    Profesional->>UI: Ingresa usuario/contraseña
    UI->>Auth: authenticate("admin", "admin123")
    Auth->>DB: SELECT * FROM Usuario
    DB-->>Auth: datos usuario
    Auth-->>UI: user dict ✅
    UI->>Audit: register("LOGIN_EXITOSO")
    UI->>UI: st.session_state.user = user

    Note over Profesional,Audit: === FASE 2: REGISTRO PACIENTE ===
    Profesional->>UI: Llena formulario P02 (21 campos)
    UI->>Patient: register_patient(...)
    Patient->>DB: SELECT COUNT(*) FROM Paciente (dup check)
    DB-->>Patient: 0 (no duplicado)
    Patient->>DB: INSERT INTO Paciente
    DB-->>Patient: OK
    Patient->>Audit: register("PACIENTE_CREADO")
    Patient-->>UI: IdPaciente ✅

    Note over Profesional,Audit: === FASE 3: INICIAR TRIAJE ===
    Profesional->>UI: Clic "Iniciar Triaje"
    UI->>Triage: create_triage_event(id_paciente)
    Triage->>DB: INSERT INTO EventoTriaje (Estado='Registrado')
    DB-->>Triage: OK
    Triage-->>UI: triaje_activo dict ✅
    UI->>UI: st.session_state.triaje_activo = triaje

    Note over Profesional,Audit: === FASE 4: SIGNOS VITALES ===
    Profesional->>UI: Llena P03 (FC, FR, T°, SpO₂, TA, peso, talla)
    UI->>Triage: save_vital_signs(id_triaje, ...)
    Triage->>Triage: Validar rangos fisiológicos
    Triage->>DB: INSERT INTO SignosVitales
    Triage->>DB: UPDATE EventoTriaje SET Estado='EnEvaluacion'
    Triage->>Audit: register("SIGNOS_VITALES_REGISTRADOS")
    Triage-->>UI: OK ✅

    Note over Profesional,Audit: === FASE 5: EVALUACIÓN CLÍNICA ===
    Profesional->>UI: Llena P04 (Glasgow, dolor, motivo, comorbilidades)
    UI->>Triage: save_clinical_evaluation(id_triaje, ...)
    Triage->>DB: INSERT INTO EvaluacionClinica
    Triage->>DB: UPDATE EventoTriaje SET Estado='PendienteIA'
    Triage->>Audit: register("EVALUACION_CLINICA_REGISTRADA")
    Triage-->>UI: OK ✅

    Note over Profesional,Audit: === FASE 6: CLASIFICACIÓN IA ===
    Profesional->>UI: Clic "Clasificar con IA"
    UI->>IA: predict(clinical_data, motivo_texto)
    IA->>DB: SELECT * FROM Paciente, SignosVitales, EvaluacionClinica
    DB-->>IA: datos consolidados
    IA->>IA: _build_feature_vector() → 387 dims
    IA->>IA: model.predict(X) → nivel III (88% prob)
    IA->>IA: _apply_thresholds(proba)
    IA->>DB: INSERT INTO PrediccionIA
    IA->>DB: UPDATE EventoTriaje SET NivelSugeridoIA='III', Estado='Clasificado'
    IA->>Audit: register("IA_EJECUTADA")
    IA-->>UI: {nivel: "III", probas: {...}, confianza: 0.89}

    Note over Profesional,Audit: === FASE 7: VALIDACIÓN PROFESIONAL ===
    Profesional->>UI: Revisa clasificación IA, confirma o corrige
    UI->>Triage: validate_classification(id_triaje, "III", concordancia=1)
    Triage->>DB: UPDATE EventoTriaje SET NivelAsignadoProfesional='III', Estado='Validado'
    Triage->>Audit: register("TRIAJE_VALIDADO")
    Triage-->>UI: OK ✅

    Note over Profesional,Audit: === FASE 8: CIERRE ===
    Profesional->>UI: Clic "Cerrar Evento"
    UI->>Triage: close_event(id_triaje)
    Triage->>DB: UPDATE EventoTriaje SET Estado='Cerrado', FechaHoraCierre=now
    Triage->>Audit: register("TRIAJE_CERRADO")
    Triage-->>UI: OK ✅
```

### 7.2 Flujo — Pipeline de Entrenamiento ML

```mermaid
sequenceDiagram
    actor Developer as 👨‍💻 Desarrollador
    participant Pipeline as run_pipeline.py
    participant Ingesta as DataIngester
    participant Clean as DataCleaner
    participant NLP as NLPEmbedder
    participant Trainer as ModelTrainer
    participant Eval as Evaluator
    participant SHAP as SHAPExplainer
    participant Serial as ModelSerializer
    participant FS as Sistema de Archivos

    Developer->>Pipeline: python run_pipeline.py

    Note over Pipeline,FS: === PASOS 1-2: INGESTA ===
    Pipeline->>Ingesta: load_unified_dataset("datasets/")
    Ingesta->>FS: Lee 4 CSVs
    Ingesta->>Ingesta: Mapeo heurístico → 9 columnas unificadas
    Ingesta->>Ingesta: _clean_numeric_columns() → "24 AÑOS"→24
    Ingesta-->>Pipeline: DataFrame 176,641 × 9

    Note over Pipeline,FS: === PASOS 3-4: LIMPIEZA ===
    Pipeline->>Clean: clean_and_prepare(df, target="nivel_triaje")
    Clean->>Clean: Elimina 43,594 filas sin target
    Clean->>Clean: Imputa nulos (mediana/moda)
    Clean->>Clean: Features derivadas (pam, shock_index, qsofa)
    Clean->>Clean: OneHotEncoder + StandardScaler → 3 features
    Clean-->>Pipeline: X_struct (133K,3), scaler, encoder

    Note over Pipeline,FS: === PASO 5: SPLIT ===
    Pipeline->>Pipeline: train_test_split(80/20, stratify=y)
    Pipeline-->>Pipeline: X_train (106K), X_test (27K)

    Note over Pipeline,FS: === PASO 6: EMBEDDINGS NLP ===
    Pipeline->>NLP: generate_embeddings(textos_train)
    NLP->>FS: Carga MiniLM (384 dims, ~420 MB)
    NLP-->>Pipeline: X_nlp_train (106K, 384), X_nlp_test (27K, 384)

    Note over Pipeline,FS: === PASOS 7-9: MODELOS ===
    Pipeline->>Trainer: train_baselines(X_s, y)
    Trainer->>Trainer: LR (F1=0.01), RF (F1=0.03), XGBoost (F1=0.19)
    Pipeline->>Trainer: train_early_fusion(X_s, X_nlp, y)
    Trainer->>Trainer: XGBoost sobre 387 dims → F1=0.19
    Pipeline->>Trainer: train_late_fusion(X_s, X_nlp, y)
    Trainer->>Trainer: Stacking XGBoost+LR → F1=0.10

    Note over Pipeline,FS: === PASO 10: SELECCIÓN ===
    Trainer->>Trainer: select_best_model(criterion="f1_macro")
    Trainer-->>Pipeline: Early Fusion 🥇 (F1=0.1899)

    Note over Pipeline,FS: === PASOS 11-12: EVALUACIÓN ===
    Pipeline->>Eval: ThresholdTuning (priorizar Recall I-II)
    Eval-->>Pipeline: Umbrales: {I:0.20, II:0.05, ...}
    Pipeline->>Eval: evaluate_model() + print_report()

    Note over Pipeline,FS: === PASO 13: SHAP ===
    Pipeline->>SHAP: explain(X_test[:200])
    SHAP->>SHAP: TreeExplainer → ERROR (incompatibilidad)
    SHAP->>SHAP: Fallback: feature_importances_
    SHAP-->>Pipeline: Top 10 features

    Note over Pipeline,FS: === PASO 14: SERIALIZACIÓN ===
    Pipeline->>Serial: serialize(model, scaler, encoder, metrics)
    Serial->>FS: model.joblib + scaler.joblib + encoder.joblib
    Serial->>FS: metadata.json + thresholds.json
    Serial->>FS: active_version.txt
    Serial-->>Pipeline: ✓ Modelo serializado en models/

    Pipeline-->>Developer: ✅ Pipeline completado (17.3 min)
```

### 7.3 Flujo — Máquina de Estados del Triaje

```mermaid
stateDiagram-v2
    [*] --> Registrado: create_triage_event()
    
    Registrado --> EnEvaluacion: save_vital_signs()
    Registrado --> Cancelado: cancelar (admin)
    
    EnEvaluacion --> PendienteIA: save_clinical_evaluation()
    EnEvaluacion --> Registrado: reiniciar evaluación
    EnEvaluacion --> Cancelado: cancelar (admin)
    
    PendienteIA --> Clasificado: IA clasifica (predict)
    PendienteIA --> EnEvaluacion: re-evaluar
    PendienteIA --> Cancelado: cancelar (admin)
    
    Clasificado --> Validado: validar profesional
    Clasificado --> PendienteIA: re-clasificar IA
    Clasificado --> Cancelado: cancelar (admin)
    
    Validado --> Cerrado: close_event()
    Validado --> Clasificado: revertir validación
    Validado --> Cancelado: cancelar (admin)
    
    Cerrado --> [*]: terminal
    
    Cancelado --> Registrado: reactivar

    note right of Registrado
        Estado inicial
        Solo datos demográficos
    end note

    note right of PendienteIA
        Signos vitales + evaluación
        Listo para clasificación IA
    end note

    note right of Validado
        Profesional confirmó o corrigió
        Nivel de triaje definitivo
    end note
```

---

## 8. Modelo de Datos

### 8.1 Diagrama Entidad-Relación

```mermaid
erDiagram
    Paciente ||--o{ EventoTriaje : "1:N tiene"
    EventoTriaje ||--|| SignosVitales : "1:1 registra"
    EventoTriaje ||--|| EvaluacionClinica : "1:1 evaluado_con"
    EventoTriaje ||--o| PrediccionIA : "1:1 clasificado_por"
    PrediccionIA ||--o| ExplicacionSHAP : "1:1 explicado_por"
    Modelo ||--o{ PrediccionIA : "1:N usado_en"
    Usuario ||--o{ Auditoria : "1:N genera"
    
    Paciente {
        string IdPaciente PK
        string TipoDocumento "CC|TI|CE|PA|RC"
        string NumeroDocumento UK
        string Nombres
        string Apellidos
        date FechaNacimiento
        int Edad
        string Sexo "M|F"
        string Telefono
        string Correo
        string EPS
        string RegimenSalud
        string Departamento
        string Ciudad
        string DireccionResidencia
        string ContactoEmergencia
        string ViaLlegada
        int EpisodiosPreviosUrgencias
        datetime FechaRegistro
    }

    EventoTriaje {
        string IdTriaje PK
        string IdPaciente FK
        string Estado "7 estados"
        string NivelSugeridoIA "I|II|III|IV|V"
        string NivelAsignadoProfesional "I-V"
        json ProbabilidadesIA
        int Concordancia "0|1"
        string MotivoDiscrepancia
        string VersionModeloUsado
        datetime FechaHoraIngreso
        datetime FechaHoraClasificacion
        datetime FechaHoraCierre
    }

    SignosVitales {
        string IdSignosVitales PK
        string IdTriaje FK_UK
        real Temperatura "30-45°C"
        int FrecuenciaCardiaca "lpm"
        int FrecuenciaRespiratoria "rpm"
        int SaturacionO2 "%"
        int PresionSistolica "mmHg"
        int PresionDiastolica "mmHg"
        real Peso "kg"
        real Talla "cm"
        real IMC "kg/m2"
    }

    EvaluacionClinica {
        string IdEvaluacion PK
        string IdTriaje FK_UK
        text MotivoTextoLibre
        string MotivoCategoria "10 categorías"
        int EscalaDolor "0-10"
        int Glasgow "3-15"
        string NivelConciencia "4 niveles"
        bool Diabetes
        bool Hipertension
        bool EnfermedadRenal
        bool Embarazo
        bool Cancer
        bool Cardiopatias
        bool EnfermedadPulmonar
        bool CirugiasRecientes
        text MedicacionRelevante
        text Alergias
    }

    Usuario {
        string IdUsuario PK
        string NombreUsuario UK
        string PasswordHash "bcrypt 12 rounds"
        string Email
        string Rol "Admin|Medico|Enfermera|Investigador|Auditor"
        bool Activo
        int IntentosFallidos
        datetime BloqueadoHasta
        json HistorialPasswords
    }

    Auditoria {
        string IdAuditoria PK
        string Usuario
        datetime FechaHora
        string Accion "17 tipos"
        string EntidadAfectada
        string IdEntidad
        json ValorAnterior
        json ValorNuevo
        string IP
        text Observaciones
    }

    Modelo {
        string IdModelo PK
        string Nombre UK
        string Version
        string Arquitectura "Early|Late|Unimodal"
        string Algoritmo
        json Hiperparametros
        real F1Score
        real Precision
        real Recall
        real AUCROC
        string Estado "Activo|Inactivo|EnValidacion"
    }
```

---

## 9. Arquitectura de Machine Learning

### 9.1 Diagrama de Pipeline de Datos

```mermaid
flowchart LR
    subgraph "Fuentes de Datos"
        A1[("CSV: Clasificación Triage\n89K filas")]
        A2[("CSV: San Juan de Dios\n43K filas")]
        A3[("CSV: Morbilidad Urgencias\n43K filas")]
        A4[("CSV: Pitalito 2019\n102 filas ✗")]
    end

    subgraph "Ingesta y Unificación"
        B1[DataIngester\nload_all_sources]
        B2[Mapeo Heurístico\n_map_to_unified]
        B3[Limpieza Numérica\n_clean_numeric_columns]
    end

    subgraph "Preprocesamiento"
        C1[Anonimización\nLey 1581/2012]
        C2[Imputación\nSimpleImputer]
        C3[Outliers Fisiológicos\nIQR Ranges]
        C4[Feature Engineering\nedad_cat, pam, shock_index]
        C5[Encoding + Scaling\nOneHot + StandardScaler]
    end

    subgraph "Feature Store"
        D1[("X_struct\n3 features")]
        D2[("X_nlp\n384 dims BERT")]
    end

    subgraph "Modelos"
        E1[LR\nF1=0.01]
        E2[RF\nF1=0.03]
        E3[XGBoost\nF1=0.19]
        E4[Early Fusion\nF1=0.19 🥇]
        E5[Late Fusion\nF1=0.10]
    end

    subgraph "Evaluación"
        F1[Threshold Tuning\nRecall I-II priority]
        F2[Matriz Confusión\n5×5]
        F3[SHAP Explain\n→ Fallback: feature_importances_]
        F4[Benchmark Comparison\nvs Raita, Levin, Klug]
    end

    subgraph "Serialización"
        G1[("models/\nmodel.joblib\nscaler.joblib\nencoder.joblib\nmetadata.json")]
    end

    A1 & A2 & A3 & A4 --> B1
    B1 --> B2 --> B3
    B3 --> C1 --> C2 --> C3 --> C4 --> C5
    C5 --> D1
    A2 -->|"texto diagnóstico"| D2
    D1 --> E1 & E2 & E3
    D1 & D2 --> E4 & E5
    E3 & E4 & E5 --> F1
    F1 --> F2 --> F3 --> F4
    E4 --> G1
```

### 9.2 Diagrama de Arquitectura de Inferencia

```mermaid
flowchart TB
    subgraph "Entrada — Datos del Paciente"
        IN1["Signos Vitales\n(FC, FR, T°, SpO₂, TA)"]
        IN2["Datos Demográficos\n(edad, sexo, EPS)"]
        IN3["Motivo de Consulta\n(texto libre)"]
    end

    subgraph "Preprocesamiento"
        P1["_build_feature_vector()\nMapeo DB → features"]
        P2["_preprocess()\nScaler + Encoder"]
        P3["_generate_nlp_features()\nTF-IDF / BERT (fallback)"]
    end

    subgraph "Modelo Serializado"
        M1[("model.joblib\nXGBoost Early Fusion")]
        M2[("scaler.joblib\nStandardScaler")]
        M3[("encoder.joblib\nOneHotEncoder")]
    end

    subgraph "Inferencia"
        INF1["model.predict(X)\n→ clase I-V"]
        INF2["model.predict_proba(X)\n→ 5 probabilidades"]
        INF3["_apply_thresholds()\nUmbrales por clase"]
    end

    subgraph "Explicabilidad"
        EXP1["SHAP TreeExplainer\n→ valores SHAP por feature"]
        EXP2["_enrich_explanation()\nNombres clínicos"]
        EXP3["Fallback:\nfeature_importances_"]
    end

    subgraph "Salida"
        OUT1["Nivel Sugerido: III"]
        OUT2["Confianza: 89.2%"]
        OUT3["Top Features SHAP"]
    end

    IN1 & IN2 --> P1
    IN3 --> P3
    P1 --> P2
    P2 --> INF1
    P3 --> INF1
    M1 --> INF1
    M2 --> P2
    M3 --> P2
    INF1 --> INF2 --> INF3
    INF1 --> EXP1
    EXP1 --> EXP2
    EXP1 -.->|"si falla"| EXP3
    INF3 --> OUT1
    INF2 --> OUT2
    EXP2 --> OUT3
```

### 9.3 Comparativa de Arquitecturas de Modelos

```mermaid
flowchart LR
    subgraph "Unimodal (XGBoost)"
        U1["3 features\nestructuradas"] --> U2["XGBoost\nn=200, d=8"] --> U3["5 clases\nF1=0.19"]
    end

    subgraph "Early Fusion 🥇"
        EF1["3 features\nestructuradas"] --> EF3["Concatenación\n387 dims"] --> EF4["XGBoost\nn=300, d=10"] --> EF5["5 clases\nF1=0.19"]
        EF2["384 dims\nNLP BERT"] --> EF3
    end

    subgraph "Late Fusion"
        LF1["3 features\nestructuradas"] --> LF3["XGBoost\nn=200, d=8"] --> LF5["5 probas"]
        LF2["384 dims\nNLP BERT"] --> LF4["LogisticRegression\nmax_iter=2000"] --> LF6["5 probas"]
        LF5 & LF6 --> LF7["Stacking\n10 dims → LR"] --> LF8["5 clases\nF1=0.10"]
    end

    style EF4 fill:#1a3a2a,stroke:#3fb950,color:#c9d1d9
    style EF5 fill:#1a3a2a,stroke:#3fb950,color:#c9d1d9
```

---

## 10. Arquitectura de Despliegue

```mermaid
flowchart TB
    subgraph "Máquina Local (Windows 11 / CPU)"
        subgraph "Proceso Python — Streamlit"
            UI["Streamlit App\n:8501"]
            SVC["Services\n(auth, patient, triage, audit)"]
            INF["InferenceService\n(modelo en memoria)"]
        end
        
        subgraph "Almacenamiento"
            DB[("SQLite DB\ndata/triaje.db")]
            MODELS[("Modelos Serializados\nmodels/*.joblib")]
            NLP[("Modelo NLP Cache\n~/.cache/huggingface/")]
        end
        
        subgraph "Pipeline ML (offline)"
            PIPE["run_pipeline.py\n(manual/CI)"]
        end
    end

    subgraph "Internet (solo en entrenamiento)"
        HF["HuggingFace Hub\nBERT model download"]
        DG["datos.gov.co\nCSV download"]
    end

    UI --> SVC
    SVC --> DB
    UI --> INF
    INF --> MODELS
    INF --> DB
    PIPE --> DG
    PIPE --> HF
    PIPE --> MODELS
```

---

## 11. Seguridad y Autenticación

### 11.1 Modelo de Seguridad

| Capa | Mecanismo | Implementación |
|---|---|---|
| **Autenticación** | Usuario + contraseña con bcrypt (12 rondas) | `AuthService.authenticate()` |
| **Autorización** | RBAC con 5 roles y permisos hardcodeados | `ROLE_PERMISSIONS` dict |
| **Sesión** | `st.session_state.user` + timeout 15 min | `check_session_timeout()` |
| **Contraseñas** | Hash bcrypt + historial (JSON) + bloqueo tras 5 intentos | `PasswordHash`, `BloqueadoHasta` |
| **Auditoría** | Append-only, 17 tipos de acciones | `AuditService.register()` |
| **PII** | Verificación de ausencia de identificadores en datasets | `anonimizacion.py` |

### 11.2 Matriz RBAC

| Página | Admin | Médico | Enfermera | Investigador | Auditor |
|---|---|---|---|---|---|
| P01 — Login | ✅ | ✅ | ✅ | ✅ | ✅ |
| P02 — Registro Paciente | ✅ | ✅ | ✅ | ❌ | ❌ |
| P03 — Signos Vitales | ✅ | ✅ | ✅ | ❌ | ❌ |
| P04 — Evaluación Clínica | ✅ | ✅ | ✅ | ❌ | ❌ |
| P05 — Clasificación IA | ✅ | ✅ | ✅ | ❌ | ❌ |
| P07 — Validación Triaje | ✅ | ✅ | ❌ | ❌ | ❌ |
| P08 — Comparación Modelos | ✅ | ❌ | ❌ | ✅ | ❌ |
| P09 — Gestión Modelos | ✅ | ❌ | ❌ | ❌ | ❌ |
| P10 — Dashboard | ✅ | ✅ | ❌ | ✅ | ✅ |
| P11 — Auditoría | ✅ | ❌ | ❌ | ❌ | ✅ |
| P12 — Gestión Usuarios | ✅ | ❌ | ❌ | ❌ | ❌ |
| P13 — Control Cambios | ✅ | ❌ | ❌ | ❌ | ❌ |
| P14 — Histórico Paciente | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 12. Deuda Técnica y Hallazgos

### 12.1 Hallazgos Críticos

| # | Hallazgo | Impacto | Recomendación |
|---|---|---|---|
| H-001 | **Sin tests automatizados** — carpeta `tests/` vacía | Riesgo de regresión en cada cambio | Agregar pytest + tests unitarios para servicios |
| H-002 | **Bypass bcrypt hardcodeado** — 5 usuarios demo tienen `if password == "admin123"` | Vulnerabilidad de seguridad | Eliminar bypass; usar solo bcrypt |
| H-003 | **@auditar decorator es un stub** — solo loguea, no persiste | Auditoría incompleta en algunas operaciones | Implementar conexión real a AuditService |
| H-004 | **F1 Macro = 0.19 vs meta ≥ 0.82** | Modelo no cumple objetivo clínico | Enriquecer datasets con signos vitales reales + SMOTE |
| H-005 | **AUC-ROC = 0.00** — posible bug en sklearn 1.9+ | Métrica no confiable | Investigar `roc_auc_score` multiclase |

### 12.2 Deuda Técnica Moderada

| # | Hallazgo | Recomendación |
|---|---|---|
| H-006 | `importlib.reload()` hack para módulos stale en Streamlit | Migrar a Streamlit native pages (v1.40+) |
| H-007 | Servicios acceden directamente a `st.session_state` | Inyectar estado como parámetro |
| H-008 | Sin ORM — SQL crudo con `row_to_dict()` manual | Evaluar SQLAlchemy si el proyecto escala |
| H-009 | `InferenceService` cruza capas (src/ + app/) | Mover serialización a `app/services/` |
| H-010 | `generate_reset_token()` usa columna `BloqueadoHasta` como almacén de token | Crear tabla `ResetToken` dedicada |
| H-011 | Datasets en `datasets/` sin versionado | Usar DVC o almacenar hash SHA256 |
| H-012 | `_clean_numeric_columns` aplica regex a todas las filas | Mover a ingesta una sola vez |

### 12.3 Violaciones Arquitectónicas

| # | Violación | Ubicación |
|---|---|---|
| V-001 | UI llama a `get_connection()` directamente en algunas páginas | `patient_page.py`, `historico_paciente_page.py` |
| V-002 | `InferenceService` importa `src.data.limpieza` (capa de pipeline) | `inference_service.py:23` |
| V-003 | `st.session_state` usado como base de datos (estado de triaje) | `app.py`, múltiples páginas |
| V-004 | `sys.path.insert` hack para resolver imports cross-package | `inference_service.py:22`, `run_pipeline.py:33` |

---

## 13. ADRs (Architecture Decision Records)

### ADR-001: Monolito en Capas sobre Streamlit
- **Estado:** Aceptado
- **Contexto:** TFM académico, ejecutable en laptop del tribunal, sin infraestructura cloud.
- **Decisión:** Arquitectura monolítica en capas (UI → Servicios → Datos) sobre Streamlit.
- **Alternativas consideradas:** FastAPI + React (descartado por complejidad), Microservicios (descartado por sobrediseño).
- **Consecuencias:** Acoplamiento a Streamlit, sin API REST, difícil escalar horizontalmente.

### ADR-002: SQLite con SQL Directo
- **Estado:** Aceptado
- **Contexto:** Necesidad de portabilidad (ejecutar sin instalar PostgreSQL/MySQL).
- **Decisión:** SQLite 3 con WAL mode, sin ORM. Conversión PascalCase→snake_case manual.
- **Alternativas consideradas:** SQLAlchemy (descartado por simplicidad), PostgreSQL (descartado por portabilidad).
- **Consecuencias:** Sin migraciones automáticas, sin concurrencia, acoplamiento a SQLite.

### ADR-003: Pipeline ML como Script Offline
- **Estado:** Aceptado
- **Contexto:** El entrenamiento consume ~17 min CPU y requiere datasets que no cambian en la demo.
- **Decisión:** `run_pipeline.py` como script CLI separado de la aplicación Streamlit.
- **Alternativas consideradas:** Entrenamiento en la app (descartado por tiempo de ejecución), MLflow (descartado por complejidad).
- **Consecuencias:** Modelo estático hasta re-entrenamiento manual; sin MLOps.

### ADR-004: Early Fusion sobre Late Fusion
- **Estado:** Aceptado (con salvedades)
- **Contexto:** Early Fusion obtuvo F1=0.1899 vs Late Fusion F1=0.0997. Sin embargo, Late Fusion detecta las 5 clases.
- **Decisión:** Seleccionar Early Fusion por mayor F1 Macro.
- **Salvedad:** Para uso clínico real, reconsiderar Late Fusion con métrica ponderada por criticidad.
- **Consecuencias:** El modelo no detecta Niveles I y V (Recall=0%).

### ADR-005: SHAP con Fallback a feature_importances_
- **Estado:** Aceptado (workaround)
- **Contexto:** SHAP 0.51.0 es incompatible con XGBoost 3.2.0. La alternativa (downgrade) rompe otras dependencias.
- **Decisión:** Usar feature_importances_ nativas de XGBoost como fallback cuando SHAP falla.
- **Consecuencias:** Explicabilidad limitada (no hay valores SHAP por muestra, solo importancia global).

---

## 14. Supuestos

| # | Supuesto | Riesgo si es incorrecto |
|---|---|---|
| S-001 | La aplicación siempre se ejecuta en un solo proceso (monousuario) | Concurrencia causaría corrupción en SQLite |
| S-002 | Los datasets colombianos no contienen PII (verificado por anonimizacion.py) | Violación de Ley 1581/2012 |
| S-003 | El modelo NLP (MiniLM) cabe en 1.5 GB de RAM | OutOfMemoryError en equipos con <4 GB |
| S-004 | Las contraseñas demo solo se usan en entorno de desarrollo | Exposición de credenciales en producción |
| S-005 | El bypass bcrypt para demo accounts es aceptable para el tribunal | No aceptable en producción |
| S-006 | Streamlit no requiere HTTPS para la demo (localhost) | Aceptable para demo; no para producción |

---

## Apéndice A: Stack Tecnológico Completo

| Capa | Tecnología | Versión |
|---|---|---|
| **Lenguaje** | Python | 3.11.7 |
| **Framework UI** | Streamlit | 1.59.2 |
| **Base de Datos** | SQLite 3 | Incluido en Python |
| **Autenticación** | bcrypt | 5.0.0 |
| **ML — Clasificación** | scikit-learn, XGBoost | 1.9.0, 3.2.0 |
| **ML — NLP** | PyTorch, Transformers, sentence-transformers | 2.13.0, 5.14.1 |
| **ML — Explicabilidad** | SHAP | 0.51.0 |
| **ML — Serialización** | joblib | 1.5.3 |
| **Visualización** | matplotlib, seaborn, plotly | 3.11.1, 0.13.2, 6.9.0 |
| **Configuración** | python-dotenv, PyYAML | 1.2.2, 6.0.3 |
| **Pipeline ML** | imbalanced-learn | 0.14.2 |

## Apéndice B: Métricas del Modelo en Producción

| Métrica | Valor | Meta | Estado |
|---|---|---|---|
| F1 Macro | 0.1895 | ≥ 0.82 | ❌ |
| Accuracy | 0.7986 | — | — |
| AUC-ROC | 0.0000 | ≥ 0.87 | ❌ (bug) |
| Recall Nivel I | 0.0000 | ≥ 0.90 | ❌ |
| Recall Nivel II | 0.0995 | ≥ 0.85 | ❌ |
| Recall Nivel III | 0.8984 | — | ✅ |
| Tiempo Inferencia | ~1.5s | < 5s | ✅ |

---

*Documento generado por STriAI — TFM UNIR Máster en Inteligencia Artificial — Julio 2026*
*Caso B: Documentación AS-IS validada contra el código fuente*
