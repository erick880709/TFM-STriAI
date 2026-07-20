# Matriz de Trazabilidad — Historias de Usuario y Tareas Técnicas

**Versión:** 7.0 (FINAL) · **Fecha:** 2026-07-19 · **Proyecto:** TFM UNIR · **Sistema:** Triaje Multimodal IA

> **🎉 PROYECTO COMPLETO — 36/36 items implementados (100%)**

> **Objetivo:** Trazabilidad completa desde requerimientos (Janus) → épicas (Epicureo) → historias/tareas (Specter) → diseño UX (figma-prd-mockups) → arquitectura (archi) → implementación (builder). Cada fila indica qué se ha construido, dónde está el código y qué mockup lo respalda.

---

## 📊 Resumen General

| Épica | Total HU/TT | ✅ Implementadas | 🔜 Pendientes | % Completado |
|---|---|---|---|---|
| E1 · Fundación del Sistema | 8 | **8** | 0 | **100%** |
| E2 · Flujo Clínico de Triaje | 8 | **8** | 0 | **100%** |
| E3 · Pipeline de Entrenamiento | 9 | **9** | 0 | **100%** |
| E4 · Motor IA + XAI | 5 | **5** | 0 | **100%** |
| E5 · Auditoría y Trazabilidad | 3 | **3** | 0 | **100%** |
| E6 · Dashboard + Gestión Modelos | 3 | **3** | 0 | **100%** |
| **TOTAL** | **36** | **36** | **0** | **100%** ✅ |

---

## ÉPICA 1 — Fundación del Sistema ✅ 100%

**Archivo épica:** `resources/functional/reqs/001-fundacion-del-sistema.md`  
**Carpeta de código:** `sistema-triaje-ia/`  
**Mockup referencia:** [P01 · Login](mockups/p01-login.md) | [Imagen](../../resources/diseno/imagenes/p01.png)

| ID | Tipo | Nombre | Estado | Archivo implementado | Mockup |
|---|---|---|---|---|---|
| **TT-E1-01** | Tarea Técnica | Inicializar proyecto con stack Python + Streamlit | ✅ Implementado | `sistema-triaje-ia/requirements.txt`, `app.py`, `.env.example`, `.gitignore`, `README.md` | — |
| **TT-E1-02** | Tarea Técnica | Configurar BD y modelo de dominio (ENT-001 a 012) | ✅ Implementado | `sistema-triaje-ia/app/data/database.py` | — |
| **TT-E1-04** | Tarea Técnica | Crear estructura modular del proyecto y puntos de extensión HCE | ✅ Implementado | `sistema-triaje-ia/app/{config,data,services,ui,ia}/` + `__init__.py` | — |
| **TT-E1-03** | Tarea Técnica | Implementar TLS/HTTPS y documentar cifrado en reposo | ✅ Implementado | Documentado en `app.py` (HTTPS local) + `README.md` (estrategia prod) | — |
| **HU-E1-01** | Historia de Usuario | Login de usuarios con autenticación y bloqueo por intentos | ✅ Implementado | `sistema-triaje-ia/app/services/auth_service.py` → `login()` | [P01](mockups/p01-login.md) |
| **HU-E1-02** | Historia de Usuario | Gestión de roles y permisos RBAC (5 roles) | ✅ Implementado | `sistema-triaje-ia/app/services/auth_service.py` → `ROLE_PERMISSIONS`, `create_user()`, `update_user_role()`, `deactivate_user()` | — |
| **HU-E1-03** | Historia de Usuario | Recuperación de contraseña por email | ✅ Implementado | `sistema-triaje-ia/app/services/auth_service.py` → `generate_reset_token()`, `reset_password()` | [P01](mockups/p01-login.md) |
| **HU-E1-04** | Historia de Usuario | Cierre automático de sesión por inactividad | ✅ Implementado | `sistema-triaje-ia/app/services/auth_service.py` → `check_session_timeout()` | [P01](mockups/p01-login.md) |

### CAs cubiertos — Épica 1

| ID | CAs totales | CAs implementados | Evidencia |
|---|---|---|---|
| HU-E1-01 | 5 | 5 | bcrypt + salt, mensaje genérico, bloqueo 5 intentos, redirección por rol |
| HU-E1-02 | 7 | 7 | CRUD usuarios, 5 roles, visibilidad condicional en sidebar, auditoría por cambio |
| HU-E1-03 | 5 | 5 | Token 30min, políticas (8+ chars, 1 mayús, 1 núm), no reutilización |
| HU-E1-04 | 4 | 4 | Timeout 15min configurable, redirección, aviso previo |

---

## ÉPICA 2 — Flujo Clínico de Triaje ✅ 100%

**Archivo épica:** `resources/functional/reqs/002-flujo-clinico-triaje.md`  
**Mockups referencia:** [P02](mockups/p02-registro-paciente.md) · [P03](mockups/p03-signos-vitales.md) · [P04](mockups/p04-evaluacion-clinica.md) · [P07](mockups/p07-validacion-triaje.md)  
**Dependencia:** Épica 1 ✅

| ID | Tipo | Nombre | Estado | Archivo implementado | Mockup |
|---|---|---|---|---|---|
| **HU-E2-01** | HU | Registrar nuevo paciente con búsqueda de duplicados y ViaLlegada | ✅ Implementado | `sistema-triaje-ia/app/services/patient_service.py` → `register_patient()`, `sistema-triaje-ia/app/ui/patient_page.py` | [P02](mockups/p02-registro-paciente.md) |
| **HU-E2-02** | HU | Buscar paciente existente por documento, nombre o historia clínica | ✅ Implementado | `sistema-triaje-ia/app/services/patient_service.py` → `search_patients()`, `sistema-triaje-ia/app/ui/patient_page.py` | [P02](mockups/p02-registro-paciente.md) |
| **HU-E2-03** | HU | Consultar historial de triajes del paciente | ✅ Implementado | `sistema-triaje-ia/app/services/patient_service.py` → `get_patient_triage_history()`, `sistema-triaje-ia/app/ui/patient_page.py` | [P02](mockups/p02-registro-paciente.md) |
| **HU-E2-04** | HU | Captura de 8 signos vitales con validación de rangos y alertas | ✅ Implementado | `sistema-triaje-ia/app/services/triage_service.py` → `save_vital_signs()`, `sistema-triaje-ia/app/ui/vital_signs_page.py` | [P03](mockups/p03-signos-vitales.md) |
| **HU-E2-05** | HU | Evaluación clínica (motivo consulta, dolor, conciencia, antecedentes, alergias) | ✅ Implementado | `sistema-triaje-ia/app/services/triage_service.py` → `save_clinical_evaluation()`, `sistema-triaje-ia/app/ui/clinical_eval_page.py` | [P04](mockups/p04-evaluacion-clinica.md) |
| **HU-E2-06** | HU | Flujo de 7 estados del triaje (Registrado → Cerrado) | ✅ Implementado | `sistema-triaje-ia/app/services/triage_service.py` → `TRANSICIONES_VALIDAS` + `transition_state()`, `sistema-triaje-ia/app/ui/triage_validation_page.py` | Transversal P02-P07 |
| **HU-E2-07** | HU | Reclasificación del paciente con motivo obligatorio y preservación de historial | ✅ Implementado | `sistema-triaje-ia/app/services/triage_service.py` → `reclassify()`, `sistema-triaje-ia/app/ui/triage_validation_page.py` | [P07](mockups/p07-validacion-triaje.md) |
| **HU-E2-08** | HU | Cierre del evento de triaje con validación de concordancia | ✅ Implementado | `sistema-triaje-ia/app/services/triage_service.py` → `close_event()`, `sistema-triaje-ia/app/ui/triage_validation_page.py` | [P07](mockups/p07-validacion-triaje.md) |

### CAs cubiertos — Épica 2

| ID | CAs totales | CAs implementados | Evidencia |
|---|---|---|---|
| HU-E2-01 | 2 | 2 | Registro con detección de duplicados, creación automática de evento de triaje, ViaLlegada como catálogo |
| HU-E2-02 | 1 | 1 | Búsqueda por documento con filtro de tipo, resultados paginados |
| HU-E2-03 | 1 | 1 | Historial completo con JOIN a signos vitales y evaluación clínica |
| HU-E2-04 | 6 | 6 | 8 signos vitales, 6 obligatorios, validación de rangos fisiológicos, alertas visuales (SpO₂ < 90%, FR > 25, etc.), cálculo automático de IMC |
| HU-E2-05 | 4 | 4 | Captura de motivo (categoría + texto libre), escala dolor 0-10, Glasgow, conciencia, 8 antecedentes, EpisodiosPrevios predictivo |
| HU-E2-06 | 7 | 7 | 7 estados con transiciones controladas, máquina de estados con TRANSICIONES_VALIDAS, indicador visual en cada pantalla |
| HU-E2-07 | 3 | 3 | Reclasificación con motivo obligatorio, preservación de nivel anterior, registro en auditoría |
| HU-E2-08 | 4 | 4 | Cierre con validación de concordancia, exigencia de motivo si discrepancia, checklist de prerrequisitos, timestamp de cierre |

---

## ÉPICA 3 — Pipeline de Datos y Entrenamiento ✅ 100%

**Archivo épica:** `resources/functional/reqs/003-pipeline-datos-entrenamiento-modelo.md`
**Datasets:** `datasets/` (4 archivos CSV, 177K filas totales)
**Dependencia:** Épica 1 ✅ · **Ejecución en paralelo con:** Épica 2

| ID | Tipo | Nombre | Estado | Archivo implementado | Mockup |
|---|---|---|---|---|---|
| **TT-E3-01** | TT | Pipeline de ingesta y anonimización de 5 fuentes de datos | ✅ Implementado | `src/data/ingesta.py` + `src/data/anonimizacion.py` | — |
| **TT-E3-02** | TT | Pipeline de limpieza, normalización y feature engineering | ✅ Implementado | `src/data/limpieza.py` | — |
| **TT-E3-03** | TT | Generación de embeddings NLP con BERT clínico en español | ✅ Implementado | `src/features/nlp_embeddings.py` | — |
| **TT-E3-04** | TT | Entrenamiento de 3 baselines unimodales (LR, RF, XGBoost) | ✅ Implementado | `src/models/train_models.py` → `train_baselines()` | — |
| **TT-E3-05** | TT | Entrenamiento de arquitectura Early Fusion | ✅ Implementado | `src/models/train_models.py` → `train_early_fusion()` | — |
| **TT-E3-06** | TT | Entrenamiento de arquitectura Late Fusion | ✅ Implementado | `src/models/train_models.py` → `train_late_fusion()` | — |
| **TT-E3-07** | TT | Threshold tuning por clase y evaluación final sobre test set | ✅ Implementado | `src/evaluation/metrics.py` → `ThresholdTuner` + `evaluate_model()` | — |
| **TT-E3-08** | TT | Generación de SHAP y comparativa contra benchmarks de la literatura | ✅ Implementado | `src/evaluation/shap_benchmarks.py` → `SHAPExplainer` + `compare_with_benchmarks()` | — |
| **TT-E3-09** | TT | Serialización del modelo ganador + transformadores para la demo | ✅ Implementado | `src/serving/serialize.py` → `ModelSerializer` | — |

### Métricas objetivo alcanzadas

| Métrica | Meta | Evidencia |
|---|---|---|
| F1 Macro | ≥ 0.82 | `run_pipeline.py` → salida de `print_evaluation_report()` |
| AUC-ROC | ≥ 0.87 | Ídem |
| Recall I-II prioritario | Maximizado sin degradar F1 > 10% | `ThresholdTuner.tune()` con f1_degradation_limit=0.10 |
| Reproducibilidad | 100% (mismo seed → mismos resultados) | `RANDOM_SEED=42` fijado en todo el pipeline |
| Modelo serializado | joblib + metadata.json | `models/` → `ModelSerializer.serialize()` |

---

## ÉPICA 4 — Motor de IA y Explicabilidad ✅ 100%

**Archivo épica:** `resources/functional/reqs/004-motor-ia-explicabilidad-demo.md`  
**Mockups referencia:** [P05](mockups/p05-clasificacion-ia.md) · [P06](mockups/p06-explicacion-shap.md) · [P08](mockups/p08-comparacion-modelos.md)  
**Dependencia:** Épicas 1 ✅ + 2 ✅ + 3 ✅

| ID | Tipo | Nombre | Estado | Archivo implementado | Mockup |
|---|---|---|---|---|---|
| **TT-E4-01** | TT | Servicio de carga del modelo serializado al iniciar la app | ✅ Implementado | `sistema-triaje-ia/app/services/inference_service.py` → `InferenceService.load_model()` | — |
| **HU-E4-01** | HU | Ejecutar inferencia asíncrona y ver probabilidades por nivel (<3s) | ✅ Implementado | `sistema-triaje-ia/app/services/inference_service.py` → `predict()`, `sistema-triaje-ia/app/ui/ia_classification_page.py` | [P05](mockups/p05-clasificacion-ia.md) |
| **HU-E4-02** | HU | Visualizar explicación SHAP (top variables en lenguaje clínico + gráficos) | ✅ Implementado | `sistema-triaje-ia/app/services/inference_service.py` → `explain()`, `sistema-triaje-ia/app/ui/ia_classification_page.py` | [P05](mockups/p05-clasificacion-ia.md) · [P06](mockups/p06-explicacion-shap.md) |
| **HU-E4-03** | HU | Validar clasificación del profesional y registrar concordancia IA vs. humano | ✅ Implementado | `sistema-triaje-ia/app/ui/ia_classification_page.py` → columna profesional + concordancia | [P05](mockups/p05-clasificacion-ia.md) · [P07](mockups/p07-validacion-triaje.md) |
| **HU-E4-04** | HU | Comparar modelos Early vs. Late Fusion lado a lado | ✅ Implementado | `sistema-triaje-ia/app/ui/model_comparison_page.py` | [P08](mockups/p08-comparacion-modelos.md) |

### CAs cubiertos — Épica 4

| ID | CAs | Evidencia |
|---|---|---|
| TT-E4-01 | Carga lazy desde `models/` con `ModelSerializer`, fallback TF-IDF | `InferenceService.load_model()` |
| HU-E4-01 | Inferencia < 3s (RNP-001), spinner, modo degradado si modelo no disponible | `predict()` + `_render_degraded_mode()` |
| HU-E4-02 | Top 10 SHAP traducido a lenguaje clínico, waterfall, fallback fisiológico | `explain()` + `_enrich_explanation()` |
| HU-E4-03 | Campo profesional independiente, concordancia automática, motivo si discrepancia | Columna "Su Clasificación" en P05 |
| HU-E4-04 | Tabla métricas lado a lado, Recall I-V, ficha técnica | `render_model_comparison()` |

---

## ÉPICA 5 — Auditoría y Trazabilidad ✅ 100%

**Archivo épica:** `resources/functional/reqs/005-auditoria-trazabilidad-cumplimiento.md`
**Mockups referencia:** [P11](mockups/p11-auditoria.md) · [P12](mockups/p12-registro-triaje-pdf.md)
**Dependencia:** Épica 1 ✅ · Se integra con Épicas 2 y 4

| ID | Tipo | Nombre | Estado | Archivo implementado | Mockup |
|---|---|---|---|---|---|
| **TT-E5-01** | TT | Implementar registro de auditoría append-only con decorador @auditar | ✅ Implementado | `sistema-triaje-ia/app/services/audit_service.py` → `AuditService.register()` + `@auditar` decorator | — |
| **HU-E5-01** | HU | Consultar y exportar auditoría con filtros (CSV, Excel, JSON) | ✅ Implementado | `sistema-triaje-ia/app/services/audit_service.py` → `query()` + `export_*()`, `sistema-triaje-ia/app/ui/audit_page.py` | [P11](mockups/p11-auditoria.md) |
| **HU-E5-02** | HU | Generar registro de triaje descargable (HTML/PDF) | ✅ Implementado | `sistema-triaje-ia/app/services/report_service.py` → `generate_triage_html()`, botón en `triage_validation_page.py` | [P12](mockups/p12-registro-triaje-pdf.md) |

### CAs cubiertos — Épica 5

| ID | CAs | Evidencia |
|---|---|---|
| TT-E5-01 | Registro inmutable de 17 acciones, append-only, decorador reutilizable | `AuditService.register()` + tabla Auditoria sin DELETE |
| HU-E5-01 | Filtros: usuario, acción, fecha, entidad, ID triaje; paginación; CSV/Excel/JSON | `AuditService.query()` + UI con 6 filtros + 3 formatos |
| HU-E5-02 | PDF/HTML con paciente anonimizado, signos vitales, clasificación IA vs prof, auditoría | `ReportService.generate_triage_html()` con diseño A4 imprimible |

---

## ÉPICA 6 — Dashboard y Gestión de Modelos ✅ 100%

**Archivo épica:** `resources/functional/reqs/006-dashboard-gestion-modelos-analitica.md`
**Mockups referencia:** [P09](mockups/p09-gestion-modelos.md) · [P10](mockups/p10-dashboard-operativo.md)
**Dependencia:** Épicas 1 ✅ + 4 ✅

| ID | Tipo | Nombre | Estado | Archivo implementado | Mockup |
|---|---|---|---|---|---|
| **HU-E6-01** | HU | Dashboard operativo con 7 indicadores y semáforo de metas | ✅ Implementado | `sistema-triaje-ia/app/ui/dashboard_page.py` | [P10](mockups/p10-dashboard-operativo.md) |
| **HU-E6-02** | HU | Gestión de modelos (registro, versionado, activación, rollback) | ✅ Implementado | `sistema-triaje-ia/app/ui/model_management_page.py` | [P09](mockups/p09-gestion-modelos.md) |
| **HU-E6-03** | HU | Exportación de reportes en Excel, CSV y JSON | ✅ Implementado | `sistema-triaje-ia/app/ui/dashboard_page.py` → exportación, `sistema-triaje-ia/app/ui/audit_page.py` → exportación | [P10](mockups/p10-dashboard-operativo.md) |

### CAs cubiertos — Épica 6

| ID | CAs | Evidencia |
|---|---|---|
| HU-E6-01 | 7 KPIs: total triajes, pacientes, concordancia, tiempo inf, tasa cierre, distribución I-V, tendencia 7d | `render_dashboard()` con métricas desde BD |
| HU-E6-02 | CRUD modelos, versionado, activación/rollback desde disco y BD | `render_model_management()` con 3 tabs |
| HU-E6-03 | CSV, Excel (multi-hoja), JSON con todos los datos del dashboard | Botones de descarga en Dashboard + Auditoría |

---

## 🗺️ Trazabilidad cruzada: HU/TT ↔ Artefactos

| HU/TT | Janus (RF/RNF/RT) | Mockup | Archi (§ doc) | Código |
|---|---|---|---|---|
| HU-E1-01 | RF-SEC-001 | P01 | §5, §8.1 | `auth_service.py::login()` |
| HU-E1-02 | RF-SEC-002 | — | §5, §8.1 | `auth_service.py::ROLE_PERMISSIONS` |
| HU-E1-03 | RF-SEC-003 | P01 | §5 | `auth_service.py::generate_reset_token()` |
| HU-E1-04 | RF-SEC-004 | P01 | §5 | `auth_service.py::check_session_timeout()` |
| TT-E1-01 | RT-002, RT-007 | — | §5, §14 | `requirements.txt`, `app.py` |
| TT-E1-02 | RD-002 | — | §9 | `database.py` (12 tablas) |
| TT-E1-03 | RNF-003 | — | §2 | Documentado en README |
| TT-E1-04 | RNF-007 | — | §6 | `app/{config,data,services,ui,ia}/` |

---

## 📁 Referencia rápida de archivos del proyecto

| Recurso | Ruta |
|---|---|
| **Código fuente** | `sistema-triaje-ia/` |
| **Requerimientos (Janus)** | `resources/functional/requests/` (19 RF) |
| **Definiciones arquitectura (Janus)** | `resources/architecture/definitions/` (14 RNF+RT) |
| **Modelos de diseño (Janus)** | `resources/design/models/` (3 RD) |
| **Épicas (Epicureo)** | `resources/functional/reqs/` (6 archivos) |
| **HU y TT (Specter)** | `resources/functional/hu/` (36 archivos) |
| **Mockups UX/UI** | `resources/diseno/mockups/` (12 archivos .md) |
| **Imágenes mockups** | `resources/diseno/imagenes/` (13 archivos) |
| **Guía builder (trazabilidad HU↔Mockup)** | `resources/diseno/guia-builder-trazabilidad-hu-mockups.md` |
| **Documento de Arquitectura** | `resources/architecture/Documento_Arquitectura_Sistema_Triaje_IA.md` |
| **Documento de Arquitectura (HTML)** | `resources/architecture/Documento_Arquitectura_Sistema_Triaje_IA.html` |
| **Línea Base** | `resources/architecture/Linea_Base_Sistema_Triaje_IA.md` |
| **Diagramas .drawio** | `resources/architecture/diagrams/` (9 archivos) |
| **Datasets** | `datasets/` (4 archivos CSV) |
| **Resumen Ejecutivo (Janus)** | `resources/summary/executive-summary.md` |
| **Matriz de Trazabilidad** | `resources/summary/trazabilidad-hu-tt-por-epica.md` ← **Este archivo** |

---

> **Última actualización:** 2026-07-19 22:45 COT  
> **Próximo hito:** Épica 2 — Flujo Clínico de Triaje (8 HU, mockups P02-P07)
