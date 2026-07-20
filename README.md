# 🧠 STriAI — Sistema de Triaje Multimodal IA

**Desarrollo de un sistema de triaje multimodal basado en IA para la atención en urgencias médicas en Colombia**

[![Python](https://img.shields.io/badge/Python-3.11.7-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.59.2-red.svg)](https://streamlit.io/)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.2.0-green.svg)](https://xgboost.readthedocs.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9.0-orange.svg)](https://scikit-learn.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.13.0-red.svg)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/Transformers-5.14.1-yellow.svg)](https://huggingface.co/docs/transformers/)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-lightgrey.svg)](LICENSE)
[![TFM UNIR](https://img.shields.io/badge/TFM-UNIR%20M%C3%A1ster%20IA-663399.svg)](https://www.unir.net/)

---

## 📋 Tabla de Contenido

- [Resumen](#resumen)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación Rápida](#instalación-rápida)
- [Ejecución](#ejecución)
- [Pipeline de Entrenamiento](#pipeline-de-entrenamiento)
- [Modelos](#modelos)
- [Documentación](#documentación)
- [Estructura del Repositorio](#estructura-del-repositorio)
- [Resultados](#resultados)
- [Autores](#autores)
- [Licencia](#licencia)

---

## Resumen

STriAI es un **Trabajo de Fin de Máster (TFM)** del Máster Universitario en Inteligencia Artificial de UNIR. El sistema integra **inteligencia artificial multimodal** — combinando datos clínicos estructurados con procesamiento de lenguaje natural (NLP) — para asistir a profesionales de la salud en la clasificación de pacientes en servicios de urgencias según los 5 niveles de triaje establecidos por la Resolución 5596/2015 del Ministerio de Salud de Colombia.

El proyecto consta de dos componentes principales:

1. **Pipeline de Entrenamiento ML** (`src/` + `run_pipeline.py`): 14 pasos que abarcan ingesta de datos, preprocesamiento, embeddings NLP, entrenamiento de 5 arquitecturas de modelos, evaluación, explicabilidad y serialización.

2. **Aplicación Demo** (`sistema-triaje-ia/`): Interfaz web funcional desarrollada en Streamlit con 14 pantallas, base de datos SQLite de 12 tablas, control de acceso basado en roles (RBAC) para 5 perfiles, auditoría inmutable y servicio de inferencia en tiempo real.

### Métricas del Modelo Ganador

| Métrica | Valor |
|---|---|
| **Modelo** | Early Fusion (XGBoost + BERT) |
| **F1 Macro** | 0.1895 |
| **Accuracy** | 79.86% |
| **Features** | 387 (3 estructuradas + 384 NLP) |
| **Datos entrenamiento** | 133,047 registros clínicos colombianos |

> ⚠️ El rendimiento está limitado por la escasez de features clínicas en los datasets colombianos. Ver [Resultados](#resultados) para análisis detallado.

---

## Arquitectura del Proyecto

```
┌─────────────────────────────────────────────────────┐
│                 APLICACIÓN DEMO (Streamlit)           │
│  14 pantallas UI · 8 servicios · 12 tablas SQLite    │
│  RBAC 5 roles · Auditoría inmutable                   │
├─────────────────────────────────────────────────────┤
│                 SERVICIO DE INFERENCIA                │
│  XGBoost + BERT · SHAP · Singleton en memoria        │
└─────────────────────────────────────────────────────┘
                         ▲
                         │ models/*.joblib
                         │
┌─────────────────────────────────────────────────────┐
│              PIPELINE ML (Offline)                    │
│  14 pasos: Ingesta → Limpieza → NLP → Modelos        │
│  → Evaluación → SHAP → Serialización                 │
│  Ejecución: python run_pipeline.py                    │
└─────────────────────────────────────────────────────┘
```

---

## Requisitos

| Componente | Mínimo | Recomendado |
|---|---|---|
| **Python** | 3.11+ | 3.11.7 |
| **RAM** | 4 GB | 8 GB |
| **Disco** | 1 GB | 3 GB (con modelo NLP) |
| **SO** | Windows 10+, macOS 12+, Ubuntu 20.04+ | — |
| **GPU** | No requerida | NVIDIA CUDA (opcional) |

---

## Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/striai-tfm.git
cd striai-tfm

# 2. Crear y activar entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r sistema-triaje-ia/requirements.txt

# 4. Configurar entorno
cp sistema-triaje-ia/.env.example sistema-triaje-ia/.env

# 5. Iniciar aplicación
streamlit run app.py --server.port 8501
```

Abrir http://localhost:8501 — Usuario: `admin` / Contraseña: `admin123`

> 📘 Consulta el **[Manual de Instalación](resources/manuales/MANUAL_INSTALACION_STriAI.html)** para instrucciones detalladas y solución de problemas.

---

## Ejecución

### Aplicación Demo

```bash
cd sistema-triaje-ia
streamlit run app.py --server.port 8501
```

### Pipeline de Entrenamiento (re-entrenar modelos)

```bash
python run_pipeline.py

# Con GPU:
python run_pipeline.py --use-gpu --nlp-model biomedical_es
```

---

## Pipeline de Entrenamiento

El pipeline ejecuta **14 pasos** secuenciales:

| Paso | Módulo | Descripción |
|---|---|---|
| 1-2 | `src/data/ingesta.py` | Carga 4 fuentes CSV → 176,641 filas unificadas |
| 3-4 | `src/data/limpieza.py` | Imputación, outliers, encoding, features derivadas |
| 5 | `run_pipeline.py` | Split estratificado 80/20 (seed=42) |
| 6 | `src/features/nlp_embeddings.py` | Embeddings BERT multilingüe (MiniLM, 384 dims) |
| 7-9 | `src/models/train_models.py` | 5 arquitecturas: LR, RF, XGBoost, Early/Late Fusion |
| 10 | `src/models/train_models.py` | Selección del mejor modelo por F1 Macro |
| 11-12 | `src/evaluation/metrics.py` | Threshold tuning + evaluación final |
| 13 | `src/evaluation/shap_benchmarks.py` | SHAP (con fallback) + comparativa benchmarks |
| 14 | `src/serving/serialize.py` | Serialización joblib + metadata JSON + SHA256 |

⏱️ **Tiempo total:** ~17 min (CPU) / ~3 min (GPU)

---

## Modelos

Se entrenaron y evaluaron **5 arquitecturas**:

| Modelo | F1 Macro | Recall I | Recall II | Recall III | Arquitectura |
|---|---|---|---|---|---|
| LR | 0.0122 | 0.15 | 0.82 | 0.00 | Unimodal |
| RF | 0.0347 | 0.07 | 0.68 | 0.03 | Unimodal |
| XGBoost | 0.1878 | 0.00 | 0.00 | 1.00 | Unimodal |
| **Early Fusion 🥇** | **0.1899** | 0.00 | 0.00 | 0.99 | **XGBoost(387d)** |
| Late Fusion | 0.0997 | 0.20 | 0.25 | 0.19 | Stacking |

> 📘 Consulta el **[Manual de Modelos](resources/manuales/MANUAL_MODELOS_STriAI.html)** para detalles de arquitectura, hiperparámetros y explicabilidad.

---

## Documentación

Toda la documentación del proyecto se encuentra en `resources/`:

| Documento | Ruta | Contenido |
|---|---|---|
| **Manual de Usuario** | `resources/manuales/MANUAL_USUARIO_STriAI.html` | Guía de uso de la aplicación |
| **Manual Técnico** | `resources/manuales/MANUAL_TECNICO_STriAI.html` | Arquitectura, DB, servicios, desarrollo |
| **Manual de Modelos** | `resources/manuales/MANUAL_MODELOS_STriAI.html` | Pipeline ML, arquitecturas, resultados |
| **Manual de Instalación** | `resources/manuales/MANUAL_INSTALACION_STriAI.html` | Requisitos, instalación paso a paso, troubleshooting |
| **Documento de Arquitectura** | `resources/architecture/arquitectura/Documento_Arquitectura_STriAI.html` | C4 Model (Nivel 1-4), secuencia, ER, seguridad |
| **Arquitectura de Modelos** | `resources/architecture/arquitectura/Documento_Arquitectura_Modelos_STriAI.html` | ML pipeline, NLP, inferencia, comparativa |
| **Diagramas Draw.io** | `resources/architecture/arquitectura/*.drawio` | Diagramas C4 + Arquitectura ML editables |
| **Informe TFM** | `resources/informeTFM/Informe_TFM_STriAI.html` | Informe académico final |

---

## Estructura del Repositorio

```
TFM-FINAL/
├── app.py                          ← Entry point Streamlit (raíz)
├── run_pipeline.py                 ← Pipeline entrenamiento ML
├── .gitignore
├── README.md                       ← Este archivo
│
├── sistema-triaje-ia/              ← 🖥️ Aplicación Demo
│   ├── app.py                      ← Entry point Streamlit
│   ├── requirements.txt            ← Dependencias Python
│   ├── .env.example                ← Plantilla configuración
│   ├── app/
│   │   ├── config/settings.py      ← Carga .env
│   │   ├── data/database.py        ← SQLite schema (12 tablas)
│   │   ├── services/               ← 8 servicios (auth, pacientes, triaje, IA)
│   │   └── ui/                     ← 14 pantallas Streamlit
│   ├── data/                       ← SQLite DB (gitignored)
│   └── models/                     ← Modelos locales
│
├── src/                            ← 🔬 Pipeline ML
│   ├── data/                       ← Ingesta, anonimización, limpieza
│   ├── features/                   ← Embeddings NLP (BERT)
│   ├── models/                     ← Entrenamiento (5 arquitecturas)
│   ├── evaluation/                 ← Métricas, SHAP, benchmarks
│   └── serving/                    ← Serialización (joblib)
│
├── datasets/                       ← 📊 Datos entrenamiento (gitignored)
├── models/                         ← 🧠 Modelos serializados (gitignored)
├── notebooks/                      ← 📓 Jupyter notebooks
├── context/                        ← 📋 Documentos de contexto
│
└── resources/                      ← 📚 Documentación
    ├── architecture/arquitectura/  ← Diagramas C4 + docs arquitectura
    ├── manuales/                   ← Manuales (usuario, técnico, modelos, instalación)
    └── informeTFM/                 ← Informe TFM final
```

---

## Resultados

### Comparativa contra Benchmarks Internacionales

| Estudio | n | F1 Macro | AUC-ROC | Modelo |
|---|---|---|---|---|
| Raita et al. (2019) | 67,517 | 0.870 | 0.92 | XGBoost unimodal |
| Levin et al. (2021) | 120,000 | 0.810 | — | Multimodal + BERT |
| Klug et al. (2020) | 42,000 | 0.765 | 0.83 | Ensemble RF+XGBoost |
| **STriAI (2026)** | **133,047** | **0.189** | **0.00** | **Early Fusion + BERT-es** |

La brecha (-0.68 F1) se atribuye a la escasez de features clínicas (3 vs decenas en benchmarks) y al desbalance extremo de clases (390:1). Ver [Informe TFM](resources/informeTFM/Informe_TFM_STriAI.html) para análisis completo.

---

## Autores

**Máster Universitario en Inteligencia Artificial — UNIR**

| Integrante | Rol | GitHub |
|---|---|---|
| **Medina Betancur, Diego Andrés** | Arquitecto de Datos y ML | [@dmedina]() |
| **Rivera Villanueva, Leyniker** | Desarrollador Full-Stack | [@lrivera]() |
| **Soto Díaz, Erick Duván** | Ingeniero de ML y QA | [@esoto]() |

**Directora:** Damaris Fuentes Lorenzo

---

## Licencia

Este proyecto es de uso académico para el TFM del Máster en Inteligencia Artificial de UNIR. Consulte con los autores antes de utilizar el código con otros fines.

---

*TFM UNIR — Julio 2026 · Armenia, Colombia*
