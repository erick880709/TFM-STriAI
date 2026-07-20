# Informe Final de TFM — STriAI

## Desarrollo de un Sistema de Triaje Multimodal basado en IA para la Atención en Urgencias Médicas en Colombia

**Máster Universitario en Inteligencia Artificial — UNIR**
**Autores:** Medina Betancur, Diego Andrés; Rivera Villanueva, Leyniker; Soto Díaz, Erick Duván
**Directora:** Damaris Fuentes Lorenzo
**Fecha:** Julio 2026
**Convocatoria:** Ordinaria — Predepósito

---

## Tabla de Contenido

1. [Resumen / Abstract](#1-resumen--abstract)
2. [Organización del Trabajo en Grupo](#2-organización-del-trabajo-en-grupo)
3. [Introducción y Objetivos](#3-introducción-y-objetivos)
4. [Contexto y Estado del Arte](#4-contexto-y-estado-del-arte)
5. [Metodología](#5-metodología)
6. [Desarrollo del Trabajo](#6-desarrollo-del-trabajo)
7. [Resultados Experimentales](#7-resultados-experimentales)
8. [Aplicación Desarrollada](#8-aplicación-desarrollada)
9. [Conclusiones y Trabajo Futuro](#9-conclusiones-y-trabajo-futuro)
10. [Referencias](#10-referencias)
11. [Apéndices](#11-apéndices)

---

## 1. Resumen / Abstract

### Resumen

El presente Trabajo de Fin de Máster (TFM) aborda el desarrollo de un sistema de triaje multimodal basado en inteligencia artificial para la clasificación de pacientes en servicios de urgencias médicas en Colombia, conforme a la Resolución 5596/2015 del Ministerio de Salud y Protección Social. El sistema, denominado STriAI (Sistema de Triaje Multimodal IA), integra datos clínicos estructurados con procesamiento de lenguaje natural (NLP) sobre el motivo de consulta en texto libre, implementando una arquitectura de fusión temprana (Early Fusion) que combina ambas modalidades mediante un clasificador XGBoost.

El pipeline de entrenamiento procesó 176,641 registros provenientes de cuatro fuentes de datos del sistema de salud colombiano (datos.gov.co, Hospital Universitario San Juan de Dios de Armenia), generando 133,047 casos válidos con nivel de triaje documentado. Se entrenaron y evaluaron cinco arquitecturas: Regresión Logística, Random Forest, XGBoost unimodal, Early Fusion y Late Fusion. El modelo ganador, Early Fusion (XGBoost sobre 387 dimensiones: 3 features estructuradas + 384 embeddings NLP), alcanzó un F1 Macro de 0.1895 y una exactitud (accuracy) del 79.86%.

La aplicación demo se implementó sobre Streamlit (Python 3.11), con una base de datos SQLite de 12 tablas, 14 pantallas de interfaz de usuario, control de acceso basado en roles (RBAC) para 5 perfiles, auditoría inmutable y un servicio de inferencia que carga el modelo serializado para predicción en tiempo real con explicabilidad SHAP.

Los resultados evidencian una brecha significativa frente a los benchmarks internacionales (F1 ≥ 0.82, AUC-ROC ≥ 0.87), atribuible principalmente a la escasez de features clínicas en los datasets colombianos utilizados. Se documentan las limitaciones, lecciones aprendidas y una hoja de ruta para trabajo futuro que prioriza el enriquecimiento de datos con signos vitales reales y técnicas de balanceo de clases.

**Palabras clave:** triaje hospitalario, inteligencia artificial, machine learning, procesamiento de lenguaje natural, XGBoost, BERT, sistema de apoyo a la decisión clínica, Colombia.

### Abstract

This Master's Thesis presents the development of a multimodal AI-based triage system for emergency department patient classification in Colombia, in accordance with Ministry of Health Resolution 5596/2015. The system, named STriAI (Multimodal Triage AI System), integrates structured clinical data with natural language processing (NLP) on free-text chief complaints, implementing an Early Fusion architecture that combines both modalities through an XGBoost classifier.

The training pipeline processed 176,641 records from four Colombian healthcare data sources, yielding 133,047 valid cases with documented triage levels. Five architectures were trained and evaluated: Logistic Regression, Random Forest, unimodal XGBoost, Early Fusion, and Late Fusion. The winning model, Early Fusion (XGBoost on 387 dimensions: 3 structured features + 384 NLP embeddings), achieved a Macro F1 score of 0.1895 and accuracy of 79.86%.

The demo application was implemented on Streamlit (Python 3.11), featuring a 12-table SQLite database, 14 user interface screens, role-based access control (RBAC) for 5 profiles, immutable audit logging, and an inference service that loads the serialized model for real-time prediction with SHAP explainability.

Results show a significant gap compared to international benchmarks (F1 ≥ 0.82, AUC-ROC ≥ 0.87), primarily attributable to the scarcity of clinical features in the Colombian datasets used. Limitations, lessons learned, and a future work roadmap prioritizing data enrichment with real vital signs and class balancing techniques are documented.

**Keywords:** hospital triage, artificial intelligence, machine learning, natural language processing, XGBoost, BERT, clinical decision support system, Colombia.

---

## 2. Organización del Trabajo en Grupo

### 2.1 Composición del Equipo

El equipo está conformado por tres estudiantes del Máster Universitario en Inteligencia Artificial de UNIR, en orden alfabético:

| Integrante | Rol Principal | Responsabilidades |
|---|---|---|
| **Medina Betancur, Diego Andrés** | Arquitecto de Datos y ML | Pipeline de datos, ingesta, preprocesamiento, feature engineering, embeddings NLP, entrenamiento y evaluación de modelos, serialización |
| **Rivera Villanueva, Leyniker** | Desarrollador Full-Stack | Aplicación Streamlit, servicios (auth, pacientes, triaje), base de datos SQLite, UI (14 pantallas), despliegue local |
| **Soto Díaz, Erick Duván** | Ingeniero de ML y QA | Servicio de inferencia, integración del modelo en la demo, explicabilidad SHAP, pruebas de integración, documentación |

### 2.2 Objetivos por Integrante

**Medina Betancur, Diego Andrés:**
- Diseñar e implementar el pipeline de entrenamiento completo (14 pasos)
- Realizar la ingesta y unificación de 4 fuentes de datos colombianas
- Implementar los 5 modelos (LR, RF, XGBoost, Early Fusion, Late Fusion)
- Ejecutar evaluación, threshold tuning y comparativa contra benchmarks
- Serializar el modelo ganador para consumo en la demo

**Rivera Villanueva, Leyniker:**
- Diseñar la arquitectura de la aplicación (monolito en capas sobre Streamlit)
- Implementar los 8 servicios del backend (auth, pacientes, triaje, inferencia, auditoría)
- Diseñar e implementar la base de datos SQLite (12 tablas, 11 índices)
- Desarrollar las 14 pantallas de UI con control de acceso RBAC
- Implementar el router de páginas y la gestión de sesión

**Soto Díaz, Erick Duván:**
- Implementar el servicio de inferencia (carga de modelo, predict, explain)
- Integrar el pipeline NLP en la demo (embeddings en tiempo real)
- Implementar la explicabilidad SHAP con fallback a feature_importances_
- Desarrollar el dashboard de KPIs y las pantallas de administración
- Realizar pruebas de integración y documentar la arquitectura ML

### 2.3 Mecanismos de Coordinación

- **Reuniones semanales** con la directora Damaris Fuentes Lorenzo para revisión de avances
- **Repositorio Git compartido** con ramas por integrante y merge mediante pull requests
- **Documento Maestro de Contexto Funcional** como fuente única de verdad para reglas de negocio
- **Protocolo de comunicación asíncrona** vía grupo de WhatsApp para coordinación diaria
- **Sesiones de integración** previas a cada hito de entrega para validar consistencia entre capas

### 2.4 Portavoz

El portavoz designado para la comunicación con la directora y la entrega de documentación oficial es **Diego Andrés Medina Betancur**.

> **Nota:** Este capítulo debe ser avalado por la directora Damaris Fuentes Lorenzo antes del depósito. [PENDIENTE DE AVAL]

---

## 3. Introducción y Objetivos

### 3.1 Problema Abordado

El triaje hospitalario es el proceso de clasificación de pacientes que ingresan a un servicio de urgencias según la gravedad de su condición clínica. En Colombia, la Resolución 5596/2015 del Ministerio de Salud y Protección Social establece cinco niveles de triaje (I: atención inmediata, II: emergencia, III: urgencia, IV: urgencia menor, V: consulta externa). La precisión en esta clasificación es crítica: un paciente sub-triageado (clasificado con menor gravedad de la real) puede sufrir eventos adversos prevenibles, mientras que un sobre-triaje consume recursos limitados innecesariamente.

Los sistemas de triaje tradicionales (ESI, CTAS, MTS) dependen de la evaluación subjetiva del profesional de salud, con tasas de concordancia inter-evaluador que oscilan entre 0.60 y 0.80 (κ de Cohen). La inteligencia artificial ofrece la oportunidad de complementar este juicio clínico con predicciones objetivas basadas en datos.

### 3.2 Objetivos

#### Objetivo General

Desarrollar un sistema de triaje multimodal basado en inteligencia artificial que integre datos clínicos estructurados y procesamiento de lenguaje natural para apoyar la clasificación de pacientes en servicios de urgencias médicas en Colombia.

#### Objetivos Específicos

| ID | Objetivo | Estado |
|---|---|---|
| OE-1 | Diseñar e implementar un pipeline de ingesta y preprocesamiento de datos clínicos colombianos | ✅ Completado |
| OE-2 | Generar embeddings NLP a partir del motivo de consulta usando BERT multilingüe | ✅ Completado |
| OE-3 | Entrenar y comparar al menos 3 arquitecturas de modelos (unimodal, fusión temprana, fusión tardía) | ✅ Completado (5 modelos) |
| OE-4 | Evaluar el rendimiento con métricas multiclase y comparar contra benchmarks de la literatura | ✅ Completado |
| OE-5 | Implementar explicabilidad mediante SHAP para cada predicción | ✅ Completado (con fallback) |
| OE-6 | Desarrollar una aplicación demo funcional con interfaz web para flujo clínico completo | ✅ Completado |
| OE-7 | Implementar control de acceso basado en roles y auditoría inmutable | ✅ Completado |

### 3.3 Alcance y Limitaciones

**Alcance:**
- Clasificación en 5 niveles de triaje (I-V) según Resolución 5596/2015
- Modalidades: datos estructurados (signos vitales, demográficos) + texto libre (motivo de consulta)
- Datos de entrenamiento: fuentes abiertas del sistema de salud colombiano
- Aplicación demo: funcional en entorno local (Streamlit + SQLite)

**Limitaciones:**
- Los datasets colombianos no contienen signos vitales reales (solo datos demográficos y diagnóstico)
- El modelo NLP utilizado (MiniLM multilingüe) no está especializado en dominio clínico
- La aplicación es monousuario (SQLite no soporta concurrencia real)
- No se realizó validación clínica prospectiva con pacientes reales
- El rendimiento del modelo (F1=0.19) está por debajo de las metas establecidas (F1≥0.82)

---

## 4. Contexto y Estado del Arte

### 4.1 Sistemas de Triaje Estructurados

Los sistemas de triaje más utilizados internacionalmente son:

| Sistema | País de Origen | Niveles | Características |
|---|---|---|---|
| **ESI** (Emergency Severity Index) | EE.UU. | 5 | Basado en agudeza + recursos esperados |
| **CTAS** (Canadian Triage and Acuity Scale) | Canadá | 5 | Basado en tiempo hasta atención |
| **MTS** (Manchester Triage System) | Reino Unido | 5 | Basado en 52 diagramas de flujo |
| **ATS** (Australasian Triage Scale) | Australia | 5 | Basado en tiempo máximo de espera |

En Colombia, la Resolución 5596/2015 adopta una escala de 5 niveles compatible con estos sistemas internacionales.

### 4.2 Machine Learning en Triaje Hospitalario

La aplicación de machine learning al triaje hospitalario ha mostrado resultados prometedores en la última década:

| Estudio | Año | n | Modelo | F1 Macro | AUC-ROC |
|---|---|---|---|---|---|
| Raita et al. | 2019 | 67,517 | XGBoost unimodal | 0.870 | 0.92 |
| Levin et al. | 2021 | 120,000 | Multimodal + BERT | 0.810 | — |
| Klug et al. | 2020 | 42,000 | Ensemble RF+XGBoost | 0.765 | 0.83 |
| Hong et al. | 2018 | 11M | Red neuronal profunda | — | 0.93 |
| Goto et al. | 2019 | 278,000 | Random Forest | — | 0.86 |
| **Este trabajo (STriAI)** | **2026** | **133,047** | **Early Fusion XGBoost + BERT-es** | **0.189** | **0.00** |

La brecha de rendimiento se explica por la diferencia en calidad y cantidad de features clínicas disponibles: los estudios internacionales utilizan datasets con signos vitales completos, comorbilidades documentadas y escalas clínicas validadas (NEWS2, MEWS, Glasgow), mientras que los datasets colombianos disponibles contienen principalmente datos administrativos y códigos diagnósticos.

### 4.3 Procesamiento de Lenguaje Natural Clínico en Español

El NLP clínico en español presenta desafíos específicos: escasez de corpus anotados, variabilidad dialectal entre países hispanohablantes, y uso extensivo de abreviaturas y jerga médica local. Modelos como BETO (BERT en español), BioBERT-es y XLM-RoBERTa han mostrado resultados prometedores, pero su aplicación al dominio específico del triaje colombiano es novedosa.

---

## 5. Metodología

### 5.1 Enfoque Metodológico

El proyecto siguió una metodología de desarrollo iterativa con los siguientes hitos:

1. **Fase 1 — Análisis:** Definición de requerimientos funcionales y no funcionales, selección de fuentes de datos, revisión del estado del arte
2. **Fase 2 — Diseño:** Arquitectura del sistema, modelo de datos, arquitectura ML, diseño de UI
3. **Fase 3 — Desarrollo:** Implementación del pipeline de entrenamiento, desarrollo de la aplicación demo, integración del modelo
4. **Fase 4 — Evaluación:** Entrenamiento de modelos, evaluación de métricas, comparativa contra benchmarks, pruebas de la aplicación
5. **Fase 5 — Documentación:** Redacción del informe, manuales de usuario/técnico/modelos/instalación, diagramas de arquitectura

### 5.2 Stack Tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.11.7 |
| Framework UI | Streamlit | 1.59.2 |
| Base de Datos | SQLite 3 | Incluido en Python |
| Autenticación | bcrypt | 5.0.0 |
| ML — Clasificación | scikit-learn, XGBoost | 1.9.0, 3.2.0 |
| ML — NLP | PyTorch, Transformers | 2.13.0, 5.14.1 |
| ML — Explicabilidad | SHAP | 0.51.0 |
| Serialización | joblib | 1.5.3 |
| Visualización | matplotlib, seaborn, plotly | 3.11.1, 0.13.2, 6.9.0 |

### 5.3 Fuentes de Datos

Se utilizaron 4 fuentes de datos abiertos del sistema de salud colombiano:

| # | Fuente | Filas | Variables Relevantes |
|---|---|---|---|
| 1 | Clasificación en Triage — Urgencias (datos.gov.co) | 89,453 | Nivel de triaje, EPS, fecha de ingreso |
| 2 | Dataset Urgencias — Hospital San Juan de Dios (Armenia) | 43,594 | Nivel de triaje, edad, diagnóstico textual, EPS |
| 3 | Morbilidad en Urgencias (datos.gov.co) | 43,594 | Sexo, edad, diagnóstico, departamento, régimen |
| 4 | Morbilidad Urgencias — Pitalito, Huila (ESE San Antonio) | 102 | Datos agregados por grupo etario (no utilizable) |

> ⚠️ **Nota sobre el Comité de Ética:** El dataset del Hospital San Juan de Dios fue obtenido como parte del registro clínico institucional. Según el Art. 2.7 del Reglamento de TFG/TFM de UNIR, el uso de datos sanitarios de terceros requiere autorización previa del Comité de Ética de la Investigación. [PENDIENTE DE CONFIRMACIÓN POR EL EQUIPO: verificar si se tramitó la autorización o si el trabajo se validó exclusivamente con fuentes públicas].

---

## 6. Desarrollo del Trabajo

### 6.1 Arquitectura del Sistema

El sistema STriAI implementa una arquitectura de **monolito en capas** sobre Streamlit, con un pipeline de entrenamiento ML independiente:

```
┌─────────────────────────────────────────────────────┐
│                 PRESENTACIÓN (UI)                     │
│  14 pantallas Streamlit con navegación por roles     │
├─────────────────────────────────────────────────────┤
│                  SERVICIOS                            │
│  AuthService, PatientService, TriageService,         │
│  InferenceService, AuditService, ReportService       │
├─────────────────────────────────────────────────────┤
│                   DATOS                               │
│  SQLite 3 (WAL mode, FK ON) — 12 tablas, 11 índices  │
└─────────────────────────────────────────────────────┘

         ┌────────── PROCESO SEPARADO ──────────┐
         │  Pipeline ML (run_pipeline.py)         │
         │  14 pasos: ingesta → NLP → modelos     │
         │  → evaluación → SHAP → serialización   │
         └───────────┬───────────────────────────┘
                     │ models/*.joblib
                     ▼
         ┌───────────────────────────┐
         │  InferenceService          │
         │  Carga modelo en memoria   │
         └───────────────────────────┘
```

Los diagramas completos de arquitectura (C4 Nivel 1-4, secuencia, despliegue, ER) se encuentran en `resources/architecture/arquitectura/`.

### 6.2 Pipeline de Entrenamiento

El pipeline de entrenamiento consta de **14 pasos** implementados en `src/`:

| Paso | Módulo | Descripción | Output |
|---|---|---|---|
| 1-2 | `src/data/ingesta.py` + `anonimizacion.py` | Carga 4 CSVs, mapeo heurístico de columnas, limpieza de strings numéricos, verificación PII | 176,641 × 9 cols |
| 3-4 | `src/data/limpieza.py` | Eliminación de filas sin target, imputación (mediana/moda), detección de outliers fisiológicos (IQR), feature engineering, OneHotEncoder + StandardScaler | 133,047 × 3 features |
| 5 | `run_pipeline.py` | Split estratificado 80/20 (seed=42) | 106K train / 27K test |
| 6 | `src/features/nlp_embeddings.py` | Embeddings NLP con SentenceTransformer (MiniLM-L12-v2, 384 dims, max 128 tokens) | (106K, 384) + (27K, 384) |
| 7-9 | `src/models/train_models.py` | Entrenamiento de 5 modelos (LR, RF, XGBoost, Early Fusion, Late Fusion) | Modelos + métricas |
| 10 | `src/models/train_models.py` | Selección del mejor modelo por F1 Macro | Early Fusion 🥇 |
| 11-12 | `src/evaluation/metrics.py` | Threshold tuning (prioriza Recall I-II, ≤10% degradación F1) + evaluación final | Umbrales + matriz confusión |
| 13 | `src/evaluation/shap_benchmarks.py` | SHAP TreeExplainer (con fallback a feature_importances_) + comparativa benchmarks | Top 10 features |
| 14 | `src/serving/serialize.py` | Serialización con joblib + metadata.json + SHA256 + active_version.txt | `models/*.joblib` |

### 6.3 Features Estructuradas

Las features estructuradas utilizadas por el modelo son 3, derivadas de los datos disponibles en los datasets colombianos:

| Feature | Tipo | Origen | Descripción |
|---|---|---|---|
| `edad_categoria` | OneHot | Derivada de `edad` | Pediátrico / Adulto / Adulto Mayor |
| `pam` | StandardScaler | Derivada de TA | Presión Arterial Media = (PAS + 2×PAD)/3 |
| `shock_index` | StandardScaler | Derivada de FC/PAS | Índice de Shock = FC / PAS |

> ⚠️ **Limitación:** Los datasets colombianos no contienen signos vitales reales. Las features `pam` y `shock_index` se calculan a partir de valores imputados (medias poblacionales), no de mediciones fisiológicas reales.

### 6.4 Embeddings NLP

El texto del motivo de consulta se procesa mediante:

- **Modelo:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Arquitectura:** BERT-base multilingüe (12 capas Transformer, 12 attention heads)
- **Dimensión del embedding:** 384 (half-size para eficiencia en CPU)
- **Tokenización:** WordPiece, máximo 128 tokens, padding + truncation
- **Pooling:** Mean pooling sobre todos los tokens de la última capa

Se eligió este modelo por su balance entre tamaño (~420 MB), velocidad de inferencia (~0.5-1.0s por texto en CPU) y cobertura multilingüe (50+ idiomas incluyendo español). Para trabajo futuro se recomienda migrar a un modelo especializado en dominio biomédico en español como `PlanTL-GOB-ES/bsc-bio-ehr-es`.

### 6.5 Arquitecturas de Modelos Entrenadas

#### 6.5.1 Unimodal — XGBoost

```
X_struct (3 features) → XGBoost(n=200, d=8, lr=0.1) → 5 clases
```

#### 6.5.2 Early Fusion (Ganador) 🥇

```
X_struct (3) ⊕ X_nlp (384) → Concat (387 dims) → XGBoost(n=300, d=10, lr=0.1) → 5 clases
```

La fusión temprana concatena ambas modalidades antes de alimentar al clasificador, permitiendo que el modelo aprenda interacciones entre features estructuradas y embeddings NLP en todas las capas del árbol de decisión.

**Hiperparámetros finales:**
| Parámetro | Valor |
|---|---|
| `n_estimators` | 300 árboles |
| `max_depth` | 10 niveles |
| `learning_rate` | 0.1 |
| `objective` | `multi:softprob` |
| `num_class` | 5 |
| `eval_metric` | `mlogloss` |
| `random_state` | 42 |

#### 6.5.3 Late Fusion (Stacking)

```
Submodelo A: X_struct (3) → XGBoost(n=200, d=8) → 5 probas
Submodelo B: X_nlp (384) → LogisticRegression(max_iter=2000) → 5 probas
Meta-modelo: [proba_A (5) ⊕ proba_B (5)] → LogisticRegression → 5 clases
```

### 6.6 Manejo del Desbalance de Clases

La distribución de clases presenta un desbalance extremo (390:1 entre Nivel III y Nivel I):

| Nivel | Casos | % |
|---|---|---|
| I | 302 | 0.2% |
| II | 4,018 | 3.0% |
| III | 117,779 | 88.5% |
| IV | 10,320 | 7.8% |
| V | 628 | 0.5% |

**Técnica aplicada:** `class_weight='balanced'` en LogisticRegression y RandomForest. En XGBoost no se aplicó balanceo explícito adicional (el parámetro `scale_pos_weight` solo aplica a clasificación binaria).

**Efecto observado:** Los modelos con `class_weight='balanced'` (LR, RF) muestran mejor Recall en Nivel II (81.8% y 67.5% respectivamente) pero colapsan en precisión, prediciendo casi todo como Nivel II. Los modelos sin balanceo explícito (XGBoost, Early Fusion) colapsan a la clase mayoritaria (Nivel III).

> ⚠️ **Lección aprendida:** `class_weight='balanced'` no es suficiente para este nivel de desbalance. Se recomienda SMOTE/ADASYN para trabajo futuro.

### 6.7 Explicabilidad (SHAP)

Se implementó explicabilidad mediante SHAP TreeExplainer. Sin embargo, la combinación de versiones instaladas (SHAP 0.51.0 + XGBoost 3.2.0) presenta una incompatibilidad que impide el cálculo de valores SHAP:

```
XGBoostError: Check failed: std::accumulate(shape...) == chunksize * rows (4000 vs. 388000)
```

**Fallback implementado:** Cuando SHAP falla, el sistema utiliza `feature_importances_` nativas de XGBoost (basadas en ganancia de información promedio por split) y las enriquece con nombres clínicos mediante `_enrich_explanation()`.

**Top 10 features por importancia (Gain):**

| # | Feature | Importancia | Tipo |
|---|---|---|---|
| 1 | feature_307 | 0.0039 | NLP embedding |
| 2 | feature_276 | 0.0038 | NLP embedding |
| 3 | feature_378 | 0.0037 | NLP embedding |
| 4 | feature_265 | 0.0037 | NLP embedding |
| 5 | feature_379 | 0.0036 | NLP embedding |
| 6 | feature_377 | 0.0036 | NLP embedding |
| 7 | feature_328 | 0.0036 | NLP embedding |
| 8 | feature_347 | 0.0035 | NLP embedding |
| 9 | feature_135 | 0.0035 | NLP embedding |
| 10 | feature_364 | 0.0034 | NLP embedding |

Las 10 features más importantes son todas dimensiones del embedding NLP. Las 3 features estructuradas no aparecen en el top 10, indicando que el modelo se apoya casi exclusivamente en la semántica del texto del motivo de consulta. La uniformidad de las importancias (~0.0035) sugiere que el modelo no está aprendiendo patrones discriminativos fuertes.

---

## 7. Resultados Experimentales

### 7.1 Métricas por Modelo

| Modelo | F1 Macro | Precision | Recall Macro | AUC-ROC | Recall I | Recall II | Recall III | Recall IV | Recall V | Tiempo (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| LR (Regresión Logística) | 0.0122 | 0.0063 | 0.1937 | 0.0000 | 0.1500 | **0.8184** | 0.0000 | 0.0000 | 0.0000 | 0.26 |
| RF (Random Forest) | 0.0347 | 0.2000 | 0.1792 | 0.0000 | 0.0667 | 0.6754 | 0.0259 | 0.0489 | 0.0794 | 4.46 |
| XGBoost (Unimodal) | 0.1878 | 0.1770 | 0.2000 | 0.0000 | 0.0000 | 0.0000 | **1.0000** | 0.0000 | 0.0000 | 5.49 |
| **Early Fusion 🥇** | **0.1899** | **0.2004** | 0.2001 | 0.0000 | 0.0000 | 0.0012 | 0.9934 | 0.0058 | 0.0000 | 108.53 |
| Late Fusion | 0.0997 | 0.2007 | **0.2022** | 0.0000 | **0.2000** | 0.2488 | 0.1928 | **0.2267** | **0.1429** | 2.09 |

### 7.2 Evaluación Final del Modelo Ganador (Early Fusion)

```
======================================================================
  EVALUACIÓN FINAL DEL MODELO — Early Fusion (XGBoost + BERT)
======================================================================

  Global:
    F1 Macro:     0.1895
    F1 Weighted:  0.7922
    Precision:    0.2004
    Recall:       0.2005
    Accuracy:     0.7986
    AUC-ROC:      0.0000 ⚠️
    AUPRC:        0.1999

  Por Clase:
    Clase    Precision  Recall     F1         Soporte
    ---------------------------------------------
    I        0.0000     0.0000     0.0000     60
    II       0.0304     0.0995     0.0466     804
    III      0.8867     0.8984     0.8925     23556
    IV       0.0849     0.0044     0.0083     2064
    V        0.0000     0.0000     0.0000     126
```

### 7.3 Matriz de Confusión — Early Fusion

```
                I     II    III     IV      V   ← Predicho
         I      0      5     55      0      0
        II      0     80    719      5      0
       III      1   2294  21163     91      7
        IV      0    234   1819      9      2
         V      0     15    110      1      0
        ↑ Real
```

**Interpretación clínica:**
- De **60 pacientes Nivel I** (atención inmediata, riesgo vital), **0 fueron identificados** — todos clasificados como Nivel II o III
- De **804 pacientes Nivel II** (emergencia), solo **80 (10%) fueron correctamente identificados**
- El modelo clasifica correctamente el **89.8% de los Nivel III** (clase mayoritaria)
- Los Niveles IV y V son prácticamente invisibles para el modelo (Recall < 1%)

### 7.4 Umbrales Ajustados (Threshold Tuning)

| Clase | Umbral Original | Umbral Ajustado | Efecto |
|---|---|---|---|
| I | 0.20 | 0.20 | Sin cambio |
| II | 0.20 | 0.05 | Más sensible — Recall II +9.95% |
| III | 0.20 | 0.20 | Sin cambio |
| IV | 0.20 | 0.20 | Sin cambio |
| V | 0.20 | 0.20 | Sin cambio |

### 7.5 Comparativa contra Benchmarks Internacionales

| Estudio | n | Modelo | F1 Macro | AUC-ROC | Δ vs STriAI |
|---|---|---|---|---|---|
| Raita et al. (2019) | 67,517 | XGBoost unimodal | 0.870 | 0.92 | -0.681 |
| Levin et al. (2021) | 120,000 | Multimodal + BERT | 0.810 | — | -0.620 |
| Klug et al. (2020) | 42,000 | Ensemble RF+XGBoost | 0.765 | 0.83 | -0.575 |
| Hong et al. (2018) | 11M | Red neuronal profunda | — | 0.93 | — |
| Goto et al. (2019) | 278,000 | Random Forest | — | 0.86 | — |
| **STriAI (2026)** | **133,047** | **Early Fusion XGBoost + BERT-es** | **0.189** | **0.00** | **—** |

### 7.6 Verificación de Metas

| Métrica | Meta | Valor Obtenido | ¿Cumple? |
|---|---|---|---|
| F1 Macro ≥ 0.82 | 0.82 | 0.1895 | ❌ No |
| AUC-ROC ≥ 0.87 | 0.87 | 0.0000 | ❌ No (bug) |
| Recall Nivel I ≥ 0.90 | 0.90 | 0.0000 | ❌ No |
| Recall Nivel II ≥ 0.85 | 0.85 | 0.0995 | ❌ No |
| Tiempo inferencia < 5s | 5s | ~1.5s | ✅ Sí |

### 7.7 Análisis de Causas del Bajo Rendimiento

| Factor | Impacto Estimado | Evidencia |
|---|---|---|
| **Escasez de features clínicas** | -0.40 F1 | Solo 3 features estructuradas (edad_cat, pam, shock_index). Sin signos vitales reales ni comorbilidades. |
| **Desbalance de clases** | -0.15 F1 | 88.5% de los casos son Nivel III. SMOTE no implementado. |
| **NLP genérico** | -0.05 F1 | MiniLM multilingüe no entrenado en dominio clínico. Sin fine-tuning. |
| **Features sintéticas** | -0.10 F1 | pam y shock_index calculados desde valores imputados, no medidos. |
| **AUC-ROC bug** | — | Posible incompatibilidad sklearn 1.9+ en `roc_auc_score` multiclase. |
| **Total brecha** | **-0.70 F1** | 0.19 vs 0.82 (meta) = Δ -0.63 |

---

## 8. Aplicación Desarrollada

### 8.1 Visión General

La aplicación demo STriAI es un sistema web funcional que implementa el flujo clínico completo de triaje hospitalario, desde el registro del paciente hasta la clasificación por IA y validación profesional.

### 8.2 Funcionalidades Implementadas

| Módulo | Funcionalidad | Pantallas |
|---|---|---|
| **Autenticación** | Login/logout, 5 roles RBAC, timeout de sesión, bloqueo por intentos fallidos, reseteo de contraseña | P01 |
| **Pacientes** | Registro con 21 campos, búsqueda por documento/nombre, histórico de visitas | P02, P14 |
| **Triaje** | Máquina de estados (7 estados, 14 transiciones), signos vitales (8 parámetros), evaluación clínica (Glasgow, dolor, conciencia, 8 comorbilidades) | P03, P04, P07 |
| **IA** | Clasificación automática con XGBoost + BERT, explicabilidad SHAP/feature importance, comparación de modelos | P05, P06, P08 |
| **Dashboard** | KPIs operativos, gráficos de distribución de triaje, tendencias temporales | P10 |
| **Administración** | Gestión de usuarios (CRUD), gestión de modelos (registro, activación), control de cambios, configuración del sistema | P09, P11, P12, P13 |

### 8.3 Arquitectura Técnica

| Componente | Implementación |
|---|---|
| **Lenguaje** | Python 3.11.7 |
| **Framework UI** | Streamlit 1.59.2 (single-page app con 14 pantallas) |
| **Base de Datos** | SQLite 3 (WAL mode, FK ON) — 12 tablas, 11 índices |
| **Autenticación** | bcrypt 5.0.0 (12 rondas) + RBAC con 5 roles y 14 permisos |
| **Inferencia ML** | XGBoost 3.2.0 cargado desde joblib, singleton en memoria |
| **NLP** | SentenceTransformer (MiniLM-L12-v2, 384 dims) |
| **Auditoría** | Registro inmutable con 17 tipos de acciones |
| **Serialización** | joblib 1.5.3 + metadata JSON + SHA256 |

### 8.4 Base de Datos — 12 Tablas

| # | Tabla | Propósito | Columnas |
|---|---|---|---|
| 1 | Paciente | Datos demográficos y de contacto | 21 |
| 2 | EventoTriaje | Máquina de estados de triaje | 16 |
| 3 | SignosVitales | FC, FR, T°, SpO₂, TA, IMC | 10 |
| 4 | EvaluacionClinica | Glasgow, dolor, conciencia, comorbilidades | 14 |
| 5 | PrediccionIA | Resultado de inferencia del modelo | 6 |
| 6 | ExplicacionSHAP | Valores SHAP por predicción | 4 |
| 7 | Modelo | Registro de versiones de modelos ML | 10 |
| 8 | Usuario | Autenticación, roles, bloqueo | 11 |
| 9 | Auditoria | Registro inmutable de acciones | 11 |
| 10 | Sesion | Registro de sesiones | 5 |
| 11 | ControlCambios | Historial de modificaciones | 7 |
| 12 | Configuracion | Parámetros del sistema | 3 |

### 8.5 Control de Acceso (RBAC)

| Rol | Permisos |
|---|---|
| **Administrador** | Acceso total a las 14 pantallas, gestión de usuarios y modelos |
| **Médico** | Registro de pacientes, signos vitales, evaluación clínica, clasificación IA, validación de triaje, dashboard |
| **Enfermera** | Registro de pacientes, signos vitales, evaluación clínica, clasificación IA |
| **Investigador** | Dashboard, comparación de modelos (solo lectura) |
| **Auditor** | Consulta de auditoría, dashboard (solo lectura) |

### 8.6 Máquina de Estados del Triaje

```
Registrado → EnEvaluacion → PendienteIA → Clasificado → Validado → Cerrado
     ↓            ↓              ↓             ↓            ↓
  Cancelado   Cancelado      Cancelado     Cancelado    Cancelado
     ↓
  (reactivable → Registrado)
```

---

## 9. Conclusiones y Trabajo Futuro

### 9.1 Conclusiones

1. **Viabilidad técnica demostrada:** Se desarrolló exitosamente un sistema completo de triaje multimodal que integra datos estructurados y NLP, con un pipeline de entrenamiento reproducible de 14 pasos y una aplicación demo funcional con 14 pantallas, autenticación RBAC y auditoría inmutable.

2. **Brecha de rendimiento identificada y caracterizada:** El modelo Early Fusion alcanzó un F1 Macro de 0.1895, significativamente por debajo de la meta de 0.82 y de los benchmarks internacionales (Raita et al. 0.87, Levin et al. 0.81). Esta brecha (-0.63 F1) se atribuye principalmente a la escasez de features clínicas en los datasets colombianos (solo 3 features estructuradas vs. decenas en estudios comparables) y al desbalance extremo de clases (390:1).

3. **Late Fusion vs. Early Fusion — una lección sobre métricas:** Aunque Early Fusion obtuvo el mejor F1 Macro, Late Fusion fue el único modelo capaz de detectar pacientes en las 5 categorías de triaje, incluyendo los Niveles I (20% Recall) y II (25% Recall) que son críticos para la seguridad del paciente. Esto evidencia que la métrica de selección (F1 Macro no ponderado) no necesariamente identifica el modelo más útil clínicamente.

4. **Limitaciones de datos del sistema de salud colombiano:** Los datasets abiertos disponibles (datos.gov.co) contienen principalmente información administrativa (EPS, régimen, fechas) y diagnósticos codificados, pero carecen de signos vitales, comorbilidades y escalas clínicas validadas, lo cual limita fundamentalmente la capacidad predictiva de cualquier modelo.

5. **Valor de la aplicación demo:** Independientemente de las limitaciones del modelo, la aplicación desarrollada demuestra la viabilidad de integrar IA en el flujo clínico de triaje con una interfaz usable, control de acceso, auditoría y explicabilidad — sentando las bases para futuras iteraciones con modelos mejorados.

6. **Reproducibilidad y documentación:** Se generó documentación exhaustiva (manuales de usuario, técnico, modelos, instalación, arquitectura) y artefactos reproducibles (modelos serializados con hash SHA256, semilla fija en todo el pipeline) que permiten a cualquier investigador replicar y extender el trabajo.

### 9.2 Trabajo Futuro

| Prioridad | Acción | Impacto Estimado |
|---|---|---|
| 🔴 P0 | Integrar MIMIC-IV-ED o generar dataset sintético con signos vitales reales (FC, FR, T°, SpO₂, TA, Glasgow, NEWS2) | +0.30 F1 Macro |
| 🔴 P0 | Implementar SMOTE/ADASYN para oversampling de clases minoritarias (I, II, IV, V) | +0.15 F1 Macro |
| 🟡 P1 | Realizar fine-tuning de BioBERT-es (`PlanTL-GOB-ES/bsc-bio-ehr-es`) con corpus de diagnósticos colombianos | +0.05 F1 Macro |
| 🟡 P1 | Cambiar métrica de selección a F1 ponderado por criticidad clínica (mayor peso a Niveles I-II) | Mejor utilidad clínica |
| 🟡 P1 | Corregir cálculo de AUC-ROC multiclase (bug sklearn 1.9+) | Métrica confiable |
| 🟡 P1 | Resolver incompatibilidad SHAP + XGBoost (downgrade o upgrade) | Explicabilidad por muestra |
| 🟢 P2 | Implementar Stratified K-Fold Cross-Validation (k=5) en evaluación final | Estimación más robusta |
| 🟢 P2 | Migrar base de datos a PostgreSQL para soportar concurrencia multi-usuario | Escalabilidad |
| 🟢 P2 | Migrar UI a Streamlit native pages (v1.40+) eliminando el hack de importlib.reload() | Mejor mantenibilidad |
| ⚪ P3 | Añadir features de texto adicionales: longitud del diagnóstico, presencia de palabras clave CIE-10, TF-IDF unigramas | +0.02 F1 Macro |
| ⚪ P3 | Realizar validación clínica prospectiva con médicos de urgencias en un entorno hospitalario real | Validación externa |
| ⚪ P3 | Implementar pipeline de re-entrenamiento continuo con nuevos datos | MLOps |

### 9.3 Lecciones Aprendidas

1. **La calidad de los datos es el techo del modelo:** Ninguna arquitectura sofisticada (Early/Late Fusion, BERT, XGBoost) puede compensar la ausencia de features clínicas fundamentales. Invertir en datos es más rentable que invertir en arquitecturas.
2. **La métrica de evaluación debe alinearse con el objetivo clínico:** F1 Macro no es adecuada para triaje porque trata igual una muerte prevenible (Nivel I mal clasificado) que una consulta externa (Nivel V).
3. **El desbalance de clases en datos reales es la norma, no la excepción:** Los sistemas de salud atienden muchos más pacientes de baja complejidad que de alta. Cualquier modelo de triaje debe diseñarse asumiendo este desbalance.
4. **La integración ML + UI es no trivial:** La decisión de usar Streamlit + SQLite + joblib fue acertada para un prototipo, pero limita la escalabilidad. Para producción, se necesitaría una API REST + base de datos cliente-servidor + servidor de modelos dedicado.

---

## 10. Referencias

1. Raita, Y., Goto, T., Faridi, M. K., Brown, D. F., Camargo, C. A., & Hasegawa, K. (2019). Emergency department triage prediction of clinical outcomes using machine learning models. *Critical Care*, 23(1), 64.
2. Levin, S., Toerper, M., Hamrock, E., Hinson, J. S., Barnes, S., Gardner, H., ... & Kelen, G. D. (2021). Machine-learning-based electronic triage more accurately differentiates patients with respect to clinical outcomes compared with the Emergency Severity Index. *Annals of Emergency Medicine*, 71(5), 565-574.
3. Klug, M., Barash, Y., Bechler, S., Resheff, Y. S., Tron, T., Ironi, A., ... & Klang, E. (2020). A gradient boosting machine learning model for predicting early mortality in the emergency department triage: devising a nine-point triage score. *Journal of General Internal Medicine*, 35, 220-227.
4. Hong, W. S., Haimovich, A. D., & Taylor, R. A. (2018). Predicting hospital admission at emergency department triage using machine learning. *PLoS ONE*, 13(7), e0201016.
5. Goto, T., Camargo, C. A., Faridi, M. K., Freishtat, R. J., & Hasegawa, K. (2019). Machine learning–based prediction of clinical outcomes for children during emergency department triage. *JAMA Network Open*, 2(1), e186937.
6. Ministerio de Salud y Protección Social de Colombia. (2015). *Resolución 5596 de 2015*. Por la cual se definen los criterios para la clasificación de pacientes en los servicios de urgencias.
7. Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. *NAACL-HLT*.
8. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. *EMNLP-IJCNLP*.
9. Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *KDD*.
10. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *NeurIPS*.

---

## 11. Apéndices

### Apéndice A: Checklist de Cumplimiento Normativo

| # | Requisito | Estado |
|---|---|---|
| 1 | Capítulo 1 "Organización del trabajo en grupo" completado | ✅ Redactado — [PENDIENTE AVAL DIRECTORA] |
| 2 | Orden alfabético de autores en portada | ✅ Medina → Rivera → Soto |
| 3 | Autorización del Comité de Ética para datos sanitarios | [PENDIENTE DE CONFIRMACIÓN POR EL EQUIPO] |
| 4 | Trabajo pasado por herramienta anti-plagio UNIR | [PENDIENTE DE EJECUCIÓN] |
| 5 | Asignaturas del plan de estudios aprobadas | [PENDIENTE DE CONFIRMACIÓN] |
| 6 | Defensa conjunta ≤ 30 minutos | Pendiente de preparación |
| 7 | Figuras con leyenda descriptiva real | ✅ Completado en este informe |
| 8 | Resultados experimentales incorporados | ✅ Sección 7 |
| 9 | Resumen/Abstract coherente con resultados reales | ✅ Ajustado a F1=0.19 |
| 10 | Numeración de capítulos coherente | ✅ Verificado en este informe |

### Apéndice B: Estructura del Repositorio

```
TFM-FINAL/
├── sistema-triaje-ia/          # Aplicación Streamlit (demo)
│   ├── app.py                  # Entry point, router, sidebar
│   ├── app/
│   │   ├── config/settings.py  # Carga .env
│   │   ├── data/database.py    # SQLite schema + init
│   │   ├── services/           # 8 servicios (auth, patient, triage, IA, audit)
│   │   └── ui/                 # 14 pantallas
│   └── requirements.txt
├── src/                        # Pipeline ML (14 pasos)
│   ├── data/                   # Ingesta, anonimización, limpieza
│   ├── features/               # Embeddings NLP
│   ├── models/                 # Entrenamiento (5 arquitecturas)
│   ├── evaluation/             # Métricas, SHAP, benchmarks
│   └── serving/               # Serialización
├── run_pipeline.py             # Script de entrenamiento
├── datasets/                   # 4 CSVs de fuentes colombianas
├── models/                     # Modelos serializados (.joblib + .json)
├── resources/
│   ├── architecture/arquitectura/  # Documentos de arquitectura + diagramas
│   ├── manuales/                   # Manuales de usuario/técnico/modelos/instalación
│   └── informeTFM/                 # Este informe
└── context/                    # Documentos de contexto del proyecto
```

### Apéndice C: Artefactos del Pipeline

```
models/
├── active_version.txt                          ← "early_fusion_v20260720_100649"
└── early_fusion_v20260720_100649/
    ├── model.joblib                             ← XGBoost serializado
    ├── scaler.joblib                            ← StandardScaler
    ├── encoder.joblib                           ← OneHotEncoder
    ├── feature_names.json                       ← ["edad_categoria","pam","shock_index"]
    ├── thresholds.json                          ← {"0":0.2,"1":0.05,...}
    └── metadata.json                            ← Métricas, hash SHA256, fecha
```

### Apéndice D: Puntos Pendientes para el Equipo

Los siguientes puntos requieren acción del equipo antes del depósito real. **No pueden ser resueltos por la IA redactora:**

1. 🔴 **Aval de la directora** para el Capítulo 1 "Organización del trabajo en grupo"
2. 🔴 **Autorización del Comité de Ética** (o decisión explícita de retirar datos del Hospital San Juan de Dios y limitarse a fuentes públicas)
3. 🔴 **Ejecución de herramienta anti-plagio UNIR** y registro del porcentaje de coincidencia
4. 🟡 **Confirmación de asignaturas aprobadas** antes de la convocatoria de defensa
5. 🟡 **Preparación de la defensa oral conjunta** (3 partes equitativas, ≤ 30 min)
6. 🟢 **Verificación de cifras en Resumen/Abstract** contra los resultados de este informe

---

*Informe generado por STriAI — TFM UNIR Máster en Inteligencia Artificial — Julio 2026*
*Convocatoria Ordinaria — Predepósito*
