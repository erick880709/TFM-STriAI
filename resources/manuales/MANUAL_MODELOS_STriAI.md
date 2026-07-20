# Manual de Modelos — STriAI (Sistema de Triaje Multimodal IA)

**TFM UNIR — Máster en Inteligencia Artificial**
**Versión:** 1.0 — Julio 2026

---

## Tabla de Contenido

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Fuentes de Datos (Datasets)](#2-fuentes-de-datos-datasets)
3. [Pipeline de Entrenamiento](#3-pipeline-de-entrenamiento)
4. [Modelos Entrenados](#4-modelos-entrenados)
5. [Resultados y Evaluación](#5-resultados-y-evaluación)
6. [Arquitectura del Modelo Ganador](#6-arquitectura-del-modelo-ganador)
7. [Explicabilidad (SHAP / Feature Importance)](#7-explicabilidad-shap--feature-importance)
8. [Serialización y Artefactos](#8-serialización-y-artefactos)
9. [Cómo Re-ejecutar el Pipeline](#9-cómo-re-ejecutar-el-pipeline)
10. [Limitaciones y Recomendaciones](#10-limitaciones-y-recomendaciones)

---

## 1. Resumen Ejecutivo

El pipeline de entrenamiento del Sistema de Triaje Multimodal IA (STriAI) entrena y evalúa **5 arquitecturas de modelos** sobre datos reales de urgencias hospitalarias en Colombia, combinando **features estructuradas** (edad, signos vitales derivados) con **embeddings NLP** generados por un modelo BERT multilingüe a partir del texto libre del motivo de consulta.

| Métrica | Valor |
|---|---|
| Modelo ganador | **Early Fusion (XGBoost + BERT)** |
| F1 Macro | 0.1895 |
| Accuracy | 79.86% |
| Features totales | 387 (3 estructuradas + 384 NLP) |
| Filas de entrenamiento | 133,047 |
| Clases objetivo | I, II, III, IV, V (Res. 5596/2015) |
| Tiempo de ejecución | ~17 minutos (CPU) |

> ⚠️ **Nota importante:** El rendimiento del modelo está limitado por la calidad y cantidad de features disponibles en los datasets colombianos. Los datasets reales utilizados carecen de signos vitales completos (frecuencia cardíaca, presión arterial, saturación O₂, etc.) y comorbilidades, lo cual restringe la capacidad predictiva. El F1 Macro de 0.19 está muy por debajo de la meta de 0.82 establecida en la arquitectura de referencia. **Se recomienda enriquecer los datasets con fuentes clínicas más completas (ej. MIMIC-IV-ED, historias clínicas electrónicas) para alcanzar el rendimiento deseado.**

---

## 2. Fuentes de Datos (Datasets)

### 2.1 Datasets Utilizados

Se utilizaron **4 fuentes de datos reales** del sistema de salud colombiano, almacenadas en `datasets/`:

| # | Archivo | Filas | Columnas | Origen |
|---|---|---|---|---|
| 1 | `Clasificación_en_Triage_Urgencias_20260713.csv` | 89,453 | 9 | datos.gov.co — Clasificación de triaje en urgencias |
| 2 | `dataset_urgencias_san_juan_de_dios_custom.csv` | 43,594 | 9 | Hospital Universitario San Juan de Dios (Armenia) |
| 3 | `MORBILIDAD_EN_EL_SERVICIO_DE_URGENCIAS_20260713.csv` | 43,594 | 12 | datos.gov.co — Morbilidad en urgencias |
| 4 | `Morbilidad_Urgencias_2019_…_Pitalito_…csv` | 102 | 11 | ESE Hospital Departamental San Antonio de Pitalito (Huila) |

### 2.2 Estructura de Cada Dataset

#### Dataset 1: Clasificación en Triage Urgencias

Columnas originales: `CodAdminis`, `Nom_Admini`, `Fecha_Ing`, `Hora_Ingre`, `Fecha_Atencion`, `Hora_Atencion`, `Triage`, `Ips`, `Red`

**Información que aporta:**
- `Triage` → **nivel_triaje** (I, II, III, IV, V) — variable objetivo
- `Nom_Admini` → **eps** (entidad administradora)
- `Fecha_Ing` → **fecha_ingreso**
- 89,453 registros con nivel de triaje

**Limitación:** No contiene datos demográficos (edad, sexo) ni clínicos (signos vitales, diagnóstico).

#### Dataset 2: Urgencias San Juan de Dios (Custom)

Columnas originales: `triage`, `codigo de diagnostico`, `diagnostico`, `eps o ips`, `fecha`, `hora de entrada`, `hora de salida`, `edad`, `año`

**Información que aporta:**
- `triage` → **nivel_triaje** (I-V) — variable objetivo
- `edad` → **edad** (ej. "24 AÑOS" → se extrae el número 24)
- `diagnostico` → **motivo_consulta_texto** (texto libre para NLP)
- `eps o ips` → **eps**
- `fecha` → **fecha_ingreso**
- 43,594 registros

**Distribución de niveles de triaje en este dataset:**

| Nivel | Casos | Porcentaje |
|---|---|---|
| I | 99 | 0.2% |
| II | 1,308 | 3.0% |
| III | 38,581 | 88.5% |
| IV | 3,386 | 7.8% |
| V | 220 | 0.5% |

**Este es el dataset principal** para entrenamiento por ser el único que contiene simultáneamente nivel de triaje, edad y diagnóstico textual.

#### Dataset 3: Morbilidad en Urgencias

Columnas originales: `PERIODO`, `AÑO`, `SEXO`, `EDAD`, `TIPO_EDAD`, `PROCEDENCIA`, `DEPARTAMENTO`, `FECHA_ATENCION`, `DIAGNOSTICO`, `NOMBRE_DIAGNOSTICO`, `REGIMEN`, `EAPB`

**Información que aporta:**
- `SEXO` → **sexo** (M/F)
- `EDAD` → **edad** (numérica)
- `DEPARTAMENTO` → **departamento**
- `DIAGNOSTICO` → **motivo_consulta_texto** (código + nombre)
- `REGIMEN` → **regimen_salud** (Subsidiado, Contributivo, Vinculado)
- `EAPB` → **eps**

**Limitación crítica:** NO contiene nivel de triaje. Sus 43,594 filas son eliminadas durante la limpieza (solo se conservan para datos demográficos de referencia).

#### Dataset 4: Morbilidad Urgencias Pitalito 2019

Columnas originales: `Nº`, `CODIGO`, `D I A G N O S T I C O`, `<30 DIAS`, `<1 AÑO`, `1 - 4`, `5 -14`, `15 - 44`, `45 - 59`, `>60 AÑOS`, `TOTAL`

**Información que aporta:** Es una tabla pivote con diagnósticos agregados por grupos etarios. **No es utilizable** para el pipeline (0 columnas mapeadas).

### 2.3 Esquema Unificado Post-Ingesta

Tras la ingesta y unificación, el dataset consolidado tiene las siguientes columnas:

| Columna | Tipo | Descripción | Cobertura |
|---|---|---|---|
| `nivel_triaje` | str | Nivel I, II, III, IV, V (target) | 75% de filas |
| `edad` | float | Edad en años (extraída de texto si es necesario) | 75% |
| `sexo` | str | M / F | 25% |
| `motivo_consulta_texto` | str | Texto libre del diagnóstico o motivo | 50% |
| `eps` | str | Entidad administradora de salud | 100% |
| `departamento` | str | Departamento de residencia | 25% |
| `regimen_salud` | str | Contributivo, Subsidiado, etc. | 25% |
| `fecha_ingreso` | str | Fecha de ingreso a urgencias | 100% |
| `fuente` | str | Origen del registro (datos_gov, san_juan_de_dios, etc.) | 100% |

**Total post-limpieza:** 133,047 filas con target válido (se eliminan 43,594 filas del dataset de Morbilidad que no tienen nivel de triaje).

---

## 3. Pipeline de Entrenamiento

### 3.1 Diagrama de Flujo

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ PASOS 1-2   │───▶│ PASOS 3-4    │───▶│  PASO 5     │───▶│   PASO 6     │
│ Ingesta +    │    │ Limpieza +   │    │ Split        │    │ Embeddings   │
│ Anonimizac.  │    │ Features     │    │ Train/Test   │    │ NLP (BERT)   │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
                                                                  │
                                          ┌───────────────────────┘
                                          ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ PASOS 7-9   │───▶│   PASO 10    │───▶│  PASO 11    │───▶│   PASO 12    │
│ Baselines +  │    │ Selección    │    │ Threshold    │    │ Evaluación   │
│ Early/Late   │    │ Mejor Modelo │    │ Tuning       │    │ Final        │
│ Fusion       │    │              │    │              │    │              │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
                                                                  │
                                          ┌───────────────────────┘
                                          ▼
                               ┌─────────────┐    ┌──────────────┐
                               │   PASO 13   │───▶│   PASO 14    │
                               │ SHAP +      │    │ Serialización │
                               │ Benchmarks  │    │ del Modelo    │
                               └─────────────┘    └──────────────┘
```

### 3.2 Descripción de Cada Paso

#### Pasos 1-2: Ingesta y Anonimización (`src/data/ingesta.py`, `src/data/anonimizacion.py`)

- Carga los 4 archivos CSV desde `datasets/`
- Mapea heurísticamente las columnas al esquema unificado (detección por nombre de columna, case-insensitive)
- Convierte columnas numéricas con texto (ej. "24 AÑOS" → 24.0)
- Verifica ausencia de PII (Personally Identifiable Information)
- **Resultado:** 176,641 filas × 9 columnas unificadas

#### Pasos 3-4: Limpieza y Feature Engineering (`src/data/limpieza.py`)

- Elimina 43,594 filas sin nivel de triaje (dataset de Morbilidad)
- Imputa valores nulos (mediana para numéricos, moda para categóricos)
- Detecta y marca outliers fisiológicos (rangos IQR)
- Genera features derivadas:
  - `edad_categoria`: grupos etarios (pediátrico, adulto, adulto mayor)
  - `pam`: presión arterial media (estimada)
  - `shock_index`: índice de shock (FC/PAS)
  - `qsofa_score`: puntuación qSOFA
- Codifica variables categóricas (OneHotEncoder) y escala numéricas (StandardScaler)
- **Resultado:** 133,047 filas × 3 features estructuradas

**Distribución de clases post-limpieza:**

| Nivel | Casos | % |
|---|---|---|
| I | 302 | 0.2% |
| II | 4,018 | 3.0% |
| III | 117,779 | 88.5% |
| IV | 10,320 | 7.8% |
| V | 628 | 0.5% |

#### Paso 5: Split Train/Test

- División estratificada 80/20 preservando la distribución de clases
- **Train:** 106,437 filas
- **Test:** 26,610 filas
- Semilla aleatoria fija (`RANDOM_SEED = 42`) para reproducibilidad

#### Paso 6: Embeddings NLP (`src/features/nlp_embeddings.py`)

- Modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Dimensiones del embedding: **384**
- Dispositivo: CPU
- Batch size: 32
- Longitud máxima de tokens: 128
- Genera embeddings para train (106,437 textos) y test (26,610 textos)
- **Resultado:** Matriz NLP de (106437, 384) para train y (26610, 384) para test

#### Paso 7: Baselines Unimodales (`src/models/train_models.py`)

Se entrenan 3 modelos baseline usando **solo features estructuradas**:

| Modelo | Configuración |
|---|---|
| **LR (Regresión Logística)** | `max_iter=2000`, `class_weight="balanced"` |
| **RF (Random Forest)** | `n_estimators=200`, `max_depth=20`, `class_weight="balanced"` |
| **XGBoost** | `n_estimators=200`, `max_depth=8`, `learning_rate=0.1` |

#### Paso 8: Early Fusion

- Concatena features estructuradas (3 dims) + embeddings NLP (384 dims) = **387 dimensiones**
- Entrena un **XGBoost** (`n_estimators=300`, `max_depth=10`) sobre la matriz concatenada
- **Estrategia:** El modelo aprende simultáneamente de ambos tipos de features

#### Paso 9: Late Fusion

- **Submodelo A:** XGBoost sobre features estructuradas (3 dims) → probabilidades 5 clases
- **Submodelo B:** LogisticRegression sobre embeddings NLP (384 dims) → probabilidades 5 clases
- **Meta-modelo:** LogisticRegression haciendo stacking de las probabilidades de A y B (10 features)
- **Estrategia:** Cada modalidad aprende independientemente; el meta-modelo combina sus predicciones

#### Paso 10: Selección del Mejor Modelo

- Criterio: **F1 Macro** (promedio armónico no ponderado entre las 5 clases)
- Se comparan los 5 modelos y se selecciona el de mayor F1 Macro
- **Ganador:** Early Fusion (F1 = 0.1899)

#### Paso 11: Threshold Tuning (`src/evaluation/metrics.py`)

- Ajusta umbrales de decisión por clase para priorizar **Recall en Niveles I y II** (pacientes críticos)
- Límite de degradación de F1: 10%
- Umbrales resultantes: `{I: 0.20, II: 0.05, III: 0.20, IV: 0.20, V: 0.20}`

#### Paso 12: Evaluación Final

- Calcula matriz de confusión, precisión, recall, F1 por clase
- Compara contra metas del proyecto (F1 ≥ 0.82, AUC-ROC ≥ 0.87)
- **Meta F1 Macro:** ❌ No alcanzada (0.19 vs 0.82)
- **Meta AUC-ROC:** ❌ No alcanzada (0.00 vs 0.87)

#### Paso 13: Explicabilidad SHAP + Benchmarks (`src/evaluation/shap_benchmarks.py`)

- Intenta calcular valores SHAP con `shap.TreeExplainer`
- **Fallback:** Si SHAP falla (incompatibilidad de versiones), usa `feature_importances_` nativa de XGBoost
- Compara resultados contra benchmarks de la literatura (Raita et al. 2019, Levin et al. 2021, etc.)

#### Paso 14: Serialización (`src/serving/serialize.py`)

- Guarda el modelo ganador y todos sus artefactos en `models/`
- Calcula hash SHA256 del modelo para verificar integridad
- Establece `active_version.txt` para que la demo lo cargue automáticamente

---

## 4. Modelos Entrenados

### 4.1 Tabla Comparativa Completa

| Modelo | F1 Macro | Precision | Recall Macro | AUC-ROC | Recall I | Recall II | Recall III | Recall IV | Recall V | Tiempo (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| **LR (Regresión Logística)** | 0.0122 | 0.0063 | 0.1937 | 0.0000 | 0.1500 | **0.8184** | 0.0000 | 0.0000 | 0.0000 | 0.26 |
| **RF (Random Forest)** | 0.0347 | 0.2000 | 0.1792 | 0.0000 | 0.0667 | 0.6754 | 0.0259 | 0.0489 | 0.0794 | 4.46 |
| **XGBoost** | 0.1878 | 0.1770 | 0.2000 | 0.0000 | 0.0000 | 0.0000 | **1.0000** | 0.0000 | 0.0000 | 5.49 |
| **Early Fusion** 🥇 | **0.1899** | **0.2004** | 0.2001 | 0.0000 | 0.0000 | 0.0012 | 0.9934 | 0.0058 | 0.0000 | 108.53 |
| **Late Fusion** | 0.0997 | 0.2007 | **0.2022** | 0.0000 | **0.2000** | 0.2488 | 0.1928 | **0.2267** | **0.1429** | 2.09 |

### 4.2 Análisis por Modelo

#### Regresión Logística (LR)
- **Fortaleza:** Mejor Recall en Nivel II (81.84%) — identifica bien a pacientes de emergencia
- **Debilidad:** F1 Macro extremadamente bajo (0.01) — predice casi todo como Nivel II
- **Conclusión:** Inútil como clasificador general; sufre por el desbalance extremo de clases

#### Random Forest (RF)
- **Fortaleza:** Recall balanceado entre niveles II (67.5%) y cierta capacidad en IV-V
- **Debilidad:** F1 Macro muy bajo (0.03), no detecta Nivel I
- **Conclusión:** Mejor que LR pero aún lejos de ser clínicamente útil

#### XGBoost (Unimodal)
- **Fortaleza:** Recall Nivel III del 100% — perfecto para la clase mayoritaria
- **Debilidad:** Ignora completamente Niveles I, II, IV, V (Recall = 0%)
- **Conclusión:** El modelo simplemente aprendió a predecir siempre Nivel III (la clase mayoritaria)

#### Early Fusion 🥇 (XGBoost sobre features concatenadas)
- **Fortaleza:** Mejor F1 Macro global (0.1899), Recall Nivel III 99.3%
- **Debilidad:** Recall en Niveles I y V = 0%, muy bajo en II y IV
- **Conclusión:** Sufre del mismo sesgo hacia la clase mayoritaria que XGBoost unimodal. La fusión temprana con embeddings NLP no aporta suficiente señal adicional para contrarrestar el desbalance.

#### Late Fusion (Stacking)
- **Fortaleza:** **Único modelo que detecta los 5 niveles** (todos tienen Recall > 0). Mejor Recall en I (20%) y IV-V
- **Debilidad:** F1 Macro bajo (0.10), sacrifica precisión en Nivel III
- **Conclusión:** La arquitectura más equilibrada. El stacking permite que el submodelo NLP compense las debilidades del submodelo estructurado.

### 4.3 ¿Por qué Early Fusion fue seleccionado como ganador?

El criterio de selección fue **F1 Macro** (promedio simple de F1 por clase, sin ponderar por frecuencia). Early Fusion obtuvo 0.1899 vs 0.0997 de Late Fusion porque:

- Early Fusion predice correctamente el 99.3% de los Nivel III (88.5% de los datos)
- Late Fusion distribuye mejor sus errores entre todas las clases, pero al ser F1 Macro no ponderado, las clases minoritarias tienen el mismo peso que la mayoritaria
- **Ironía:** Late Fusion es clínicamente más útil (detecta pacientes críticos Nivel I-II), pero Early Fusion gana en la métrica de selección

> 💡 **Recomendación:** Para uso clínico real, considerar Late Fusion o ajustar la métrica de selección a F1 ponderado por criticidad (mayor peso a Niveles I y II).

---

## 5. Resultados y Evaluación

### 5.1 Evaluación Final del Modelo Ganador (Early Fusion)

```
======================================================================
  EVALUACIÓN FINAL DEL MODELO
======================================================================

  Global:
    F1 Macro:     0.1895
    F1 Weighted:  0.7922
    Precision:    0.2004
    Recall:       0.2005
    Accuracy:     0.7986
    AUC-ROC:      0.0000
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

### 5.2 Matriz de Confusión

```
                I     II    III     IV      V
         I      0      5     55      0      0
        II      0     80    719      5      0
       III      1   2294  21163     91      7
        IV      0    234   1819      9      2
         V      0     15    110      1      0
```

**Interpretación:**
- De 60 pacientes Nivel I reales, **0 fueron identificados** — todos fueron clasificados como Nivel II o III
- De 804 pacientes Nivel II reales, solo **80 (10%) fueron correctamente identificados**
- El modelo tiene una fuerte tendencia a predecir Nivel III (88.7% de precisión en esa clase)
- Los Niveles IV y V son prácticamente invisibles para el modelo

### 5.3 Comparativa contra Benchmarks de la Literatura

| Estudio | Accuracy | F1 Macro | AUC-ROC | Descripción |
|---|---|---|---|---|
| Raita et al. (2019) | — | 0.870 | 0.92 | XGBoost unimodal, Japón (n=67,517) |
| Levin et al. (2021) | — | 0.810 | — | Multimodal estructurado + NLP BERT (n=120K) |
| Klug et al. (2020) | — | 0.765 | 0.83 | Ensemble RF+XGBoost, Alemania (n=42K) |
| Hong et al. (2018) | 0.930 | — | — | Red neuronal profunda, Corea (n=11M) |
| **Este trabajo (STriAI)** | **0.799** | **0.189** | **0.00** | Early/Late Fusion XGBoost + BERT-es, Colombia |

**Brecha de rendimiento (Δ):** -0.681 vs mejor benchmark (Raita et al. 2019)

### 5.4 Factores que Limitan el Rendimiento

| Factor | Impacto | Solución Propuesta |
|---|---|---|
| **Desbalance extremo** (88.5% Nivel III) | El modelo aprende a predecir siempre la clase mayoritaria | SMOTE/ADASYN para oversampling de clases minoritarias |
| **Solo 3 features estructuradas** | Datos colombianos no tienen signos vitales ni comorbilidades | Integrar MIMIC-IV-ED o datasets sintéticos enriquecidos |
| **Texto libre no estructurado** | Los diagnósticos son códigos CIE-10, no narrativa clínica | Usar modelos NLP entrenados en dominio clínico (BioBERT-es) |
| **AUC-ROC = 0.00** | Posible bug en el cálculo con sklearn 1.9+ | Revisar `roc_auc_score` con `average="macro"` y multiclase |
| **Modelo BERT multilingüe genérico** | No está especializado en terminología médica en español | Usar `PlanTL-GOB-ES/bsc-bio-ehr-es` (Biomedical Spanish) |

---

## 6. Arquitectura del Modelo Ganador

### 6.1 Early Fusion — Diagrama

```
┌──────────────────────────────────────────────────────────────────┐
│                     EARLY FUSION (XGBoost)                       │
│                                                                  │
│  ┌─────────────────────┐     ┌─────────────────────┐             │
│  │ Features Estruct.    │     │ Embeddings NLP       │             │
│  │ (3 dimensiones)      │     │ (384 dimensiones)     │             │
│  │ • edad_categoria     │     │ • motivo_consulta     │             │
│  │ • pam                │     │   → vector BERT       │             │
│  │ • shock_index        │     │   (768→384 reducido)  │             │
│  └─────────┬───────────┘     └─────────┬───────────┘             │
│            │                            │                         │
│            └──────────┬─────────────────┘                         │
│                       ▼                                           │
│            ┌─────────────────────┐                                │
│            │ Concatenación       │                                │
│            │ 3 + 384 = 387 dims  │                                │
│            └─────────┬───────────┘                                │
│                      ▼                                            │
│            ┌─────────────────────┐                                │
│            │ XGBoost Classifier  │                                │
│            │ n_estimators=300    │                                │
│            │ max_depth=10        │                                │
│            │ learning_rate=0.1   │                                │
│            │ objective=multi:    │                                │
│            │   softprob          │                                │
│            └─────────┬───────────┘                                │
│                      ▼                                            │
│            ┌─────────────────────┐                                │
│            │ Predicción 5 clases │                                │
│            │ I, II, III, IV, V   │                                │
│            └─────────────────────┘                                │
└──────────────────────────────────────────────────────────────────┘
```

### 6.2 Hiperparámetros

| Parámetro | Valor |
|---|---|
| Algoritmo | XGBoost (Gradient Boosting) |
| `n_estimators` | 300 árboles |
| `max_depth` | 10 niveles de profundidad |
| `learning_rate` | 0.1 (eta) |
| `objective` | `multi:softprob` (probabilidades multiclase) |
| `num_class` | 5 |
| `eval_metric` | `mlogloss` |
| `random_state` | 42 |
| `n_jobs` | -1 (todos los CPUs) |

---

## 7. Explicabilidad (SHAP / Feature Importance)

### 7.1 Limitación Técnica

La versión instalada de SHAP (0.51.0) es **incompatible con XGBoost 3.2.0**. El cálculo de valores SHAP falla con:

```
XGBoostError: Check failed: std::accumulate(shape...) == chunksize * rows
```

Como **fallback**, se utilizan las `feature_importances_` nativas de XGBoost (basadas en ganancia de información promedio por split).

### 7.2 Top 10 Features por Importancia (XGBoost Gain)

| # | Feature | Importancia |
|---|---|---|
| 1 | feature_307 (NLP embedding dim 307) | 0.0039 |
| 2 | feature_276 (NLP embedding dim 276) | 0.0038 |
| 3 | feature_378 (NLP embedding dim 378) | 0.0037 |
| 4 | feature_265 (NLP embedding dim 265) | 0.0037 |
| 5 | feature_379 (NLP embedding dim 379) | 0.0036 |
| 6 | feature_377 (NLP embedding dim 377) | 0.0036 |
| 7 | feature_328 (NLP embedding dim 328) | 0.0036 |
| 8 | feature_347 (NLP embedding dim 347) | 0.0035 |
| 9 | feature_135 (NLP embedding dim 135) | 0.0035 |
| 10 | feature_364 (NLP embedding dim 364) | 0.0034 |

**Interpretación:**
- Las 10 features más importantes son **todas dimensiones del embedding NLP** (384 dims)
- Las 3 features estructuradas (edad_categoria, pam, shock_index) no aparecen en el top 10
- Esto indica que el modelo se apoya fuertemente en la semántica del texto del motivo de consulta
- Las importancias son muy bajas y uniformes (~0.0035), lo cual es esperable con 387 features y un modelo que esencialmente colapsa a predecir una sola clase

> ⚠️ **La importancia uniforme de features sugiere que el modelo no está aprendiendo patrones discriminativos reales**, sino que está explotando el sesgo de clase mayoritaria. Esto es consistente con el F1 Macro de 0.19.

---

## 8. Serialización y Artefactos

### 8.1 Estructura de Archivos Generados

```
models/
├── active_version.txt                      ← "early_fusion_v20260720_100649"
└── early_fusion_v20260720_100649/
    ├── model.joblib                         ← Modelo XGBoost serializado
    ├── scaler.joblib                        ← StandardScaler para features numéricas
    ├── encoder.joblib                       ← OneHotEncoder para features categóricas
    ├── feature_names.json                   ← Nombres de las 3 features estructuradas
    ├── thresholds.json                      ← Umbrales por clase: {0: 0.2, 1: 0.05, ...}
    └── metadata.json                        ← Métricas, fecha, versión, hash SHA256
```

### 8.2 Contenido de `metadata.json`

```json
{
  "model_name": "Early Fusion",
  "version": "v20260720_100649",
  "created_at": "2026-07-20T10:06:49",
  "model_hash": "d933641c78e3...",
  "num_features": 3,
  "feature_names": ["edad_categoria", "pam", "shock_index"],
  "nlp_model": "multilingual",
  "metrics": {
    "f1_macro": 0.1895,
    "accuracy": 0.7986,
    "recall_I": 0.0,
    "recall_II": 0.0995
  },
  "thresholds": {
    "0": 0.2, "1": 0.05, "2": 0.2, "3": 0.2, "4": 0.2
  },
  "description": "Modelo Early Fusion entrenado sobre 133,047 registros clínicos."
}
```

### 8.3 Carga del Modelo en la Aplicación Demo

La demo Streamlit carga el modelo automáticamente a través del `InferenceService`:

```python
# app/services/inference_service.py
from src.serving.serialize import ModelSerializer

serializer = ModelSerializer()
model, scaler, encoder, metadata = serializer.load_active()
```

El servicio busca `active_version.txt` en `models/`, carga el directorio indicado, y expone los métodos `predict()` y `explain()` para la interfaz de usuario.

---

## 9. Cómo Re-ejecutar el Pipeline

### 9.1 Requisitos Previos

- **Python 3.11+** con entorno virtual activado
- **Dependencias:** `pip install -r sistema-triaje-ia/requirements.txt`
- **Datasets:** Archivos CSV en `datasets/` (ver sección 2)
- **Espacio en disco:** ~2 GB (modelo NLP ~420 MB + artefactos)
- **RAM recomendada:** 8 GB mínimo (los embeddings NLP consumen ~1.5 GB)

### 9.2 Comando de Ejecución

```bash
# Desde la raíz del proyecto (TFM-FINAL/)
python run_pipeline.py

# Con opciones personalizadas:
python run_pipeline.py \
  --datasets-dir ./datasets \
  --output-dir ./models \
  --nlp-model multilingual \
  --use-gpu  # Solo si hay GPU NVIDIA con CUDA disponible
```

### 9.3 Opciones del Pipeline

| Argumento | Default | Descripción |
|---|---|---|
| `--datasets-dir` | `./datasets` | Directorio con los archivos CSV de entrenamiento |
| `--output-dir` | `./models` | Directorio de salida para modelos serializados |
| `--nlp-model` | `multilingual` | Modelo NLP: `beto_clinico`, `biomedical_es`, o `multilingual` |
| `--use-gpu` | `False` | Usar GPU si está disponible (requiere CUDA) |

### 9.4 Tiempo Estimado de Ejecución

| Fase | Tiempo (CPU) | Tiempo (GPU) |
|---|---|---|
| Ingesta + Limpieza | < 10 segundos | < 10 segundos |
| Embeddings NLP (train) | ~7 minutos | ~30 segundos |
| Embeddings NLP (test) | ~2 minutos | ~10 segundos |
| Entrenamiento modelos | ~5 minutos | ~2 minutos |
| SHAP + Serialización | < 10 segundos | < 10 segundos |
| **Total** | **~17 minutos** | **~3 minutos** |

### 9.5 Solución de Problemas Comunes

| Error | Causa | Solución |
|---|---|---|
| `ValueError: No se pudo unificar ninguna fuente` | Datasets no encontrados o sin columnas mapeables | Verificar que los CSV están en `datasets/` con los nombres exactos |
| `TypeError: '<' not supported between instances of 'str' and 'int'` | Columna numérica contiene texto | Ya corregido en `ingesta.py` (extrae números de strings) |
| `XGBoostError` en SHAP | Incompatibilidad SHAP + XGBoost | Ya corregido (fallback a feature_importances_) |
| `NameError: name 'datetime' is not defined` | Falta import | Ya corregido en `run_pipeline.py` |
| `multi_class` unexpected argument | sklearn 1.9+ eliminó el parámetro | Ya corregido en `train_models.py` y `metrics.py` |
| Memoria insuficiente | Embeddings NLP consumen ~1.5 GB | Reducir batch_size en `nlp_embeddings.py` o usar modelo más pequeño |

---

## 10. Limitaciones y Recomendaciones

### 10.1 Limitaciones Actuales

1. **Dataset empobrecido:** Los datos del sistema de salud colombiano no incluyen signos vitales, comorbilidades, ni escalas clínicas estandarizadas (Glasgow, NEWS2, MEWS).
2. **Desbalance extremo:** 88.5% de los casos son Nivel III. SMOTE y class_weight ayudan pero no son suficientes con tan pocas features.
3. **AUC-ROC = 0.00:** Posible bug en el cálculo de `roc_auc_score` para clasificación multiclase con sklearn 1.9. Requiere investigación.
4. **SHAP no funcional:** Incompatibilidad de versiones impide análisis de explicabilidad profundo.
5. **Modelo NLP genérico:** El modelo multilingüe MiniLM no está especializado en terminología médica en español.
6. **Features derivadas sintéticas:** `pam`, `shock_index`, `qsofa_score` se calculan a partir de valores imputados, no medidos.

### 10.2 Recomendaciones para Mejorar el Modelo

| Prioridad | Acción | Impacto Esperado |
|---|---|---|
| 🔴 Crítica | Integrar MIMIC-IV-ED o datos sintéticos con signos vitales reales | +0.30 F1 Macro |
| 🔴 Crítica | Aplicar SMOTE/ADASYN para balancear clases minoritarias | +0.15 F1 Macro |
| 🟡 Alta | Usar BioBERT-es (`PlanTL-GOB-ES/bsc-bio-ehr-es`) en lugar de MiniLM multilingüe | +0.05 F1 Macro |
| 🟡 Alta | Cambiar métrica de selección a F1 ponderado por criticidad clínica | Mejor utilidad clínica |
| 🟢 Media | Agregar features de texto: longitud del diagnóstico, presencia de palabras clave | +0.02 F1 Macro |
| 🟢 Media | Corregir cálculo de AUC-ROC multiclase | Métrica correcta |
| ⚪ Baja | Downgrade SHAP a 0.44 o XGBoost a 1.7 para restaurar explicabilidad | Diagnóstico sin impacto en métrica |

### 10.3 Próximos Pasos Sugeridos

1. **Épica 5 (opcional):** Re-entrenar con datasets enriquecidos (signos vitales + comorbilidades)
2. **Épica 6 (opcional):** Implementar curriculum learning para manejar el desbalance
3. **Validación clínica:** Someter el modelo a revisión por médicos de urgencias para validar la utilidad clínica real
4. **Optimización de hiperparámetros:** Grid search sobre `max_depth`, `n_estimators`, `learning_rate` con foco en Recall I-II

---

## Apéndice A: Comando de Ejecución Registrado

```bash
cd TFM-FINAL/
.\.venv\Scripts\python.exe run_pipeline.py
```

**Fecha de ejecución:** 2026-07-20 10:06:49 COT
**Duración:** 17.3 minutos
**Entorno:** Python 3.11.7, Windows 11, CPU Intel, 16 GB RAM

## Apéndice B: Versiones de Librerías

| Librería | Versión |
|---|---|
| Python | 3.11.7 |
| pandas | 3.0.3 |
| numpy | 2.4.6 |
| scikit-learn | 1.9.0 |
| xgboost | 3.2.0 |
| shap | 0.51.0 |
| torch | 2.13.0 |
| transformers | 5.14.1 |
| sentence-transformers | (via transformers) |
| joblib | 1.5.3 |
| imbalanced-learn | 0.14.2 |
| matplotlib | 3.11.1 |
| seaborn | 0.13.2 |

---

*Documento generado automáticamente por el pipeline STriAI — TFM UNIR Máster en Inteligencia Artificial*
