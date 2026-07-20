# Plan de Pruebas Consolidado — Épicas 3-4-5-6

**Versión:** 1.0 · **Fecha:** 2026-07-19 · **Run ID:** run-001
**Proyecto:** TFM UNIR · **Sistema:** Triaje Multimodal IA
**Entorno:** `http://localhost:8501` · **Tipo:** QA Code Review + Browser

---

## ÉPICA 3 — Pipeline de Datos y Entrenamiento (9 TT)

### TC-E3-01 [Crítico] — Ingesta unificada de 5 fuentes
- **TT:** TT-E3-01 | **Archivo:** `src/data/ingesta.py`
- **Verificación:** `DataIngester.load_all_sources()` carga CSVs con detección de encoding
- **Esperado:** `load_unified_dataset()` produce DataFrame con schema unificado de 34 columnas

### TC-E3-02 [Crítico] — Anonimización Ley 1581/2012
- **TT:** TT-E3-01 | **Archivo:** `src/data/anonimizacion.py`
- **Verificación:** `Anonymizer.remove_direct_identifiers()` elimina PII
- **Esperado:** 17 identificadores directos eliminados, `verify_no_pii()` retorna True

### TC-E3-03 [Crítico] — Limpieza y feature engineering
- **TT:** TT-E3-02 | **Archivo:** `src/data/limpieza.py`
- **Verificación:** `DataCleaner` aplica IQR outliers, imputación, StandardScaler, OneHotEncoder
- **Esperado:** Features derivadas: PAM, Shock Index, qSOFA, edad_categoria

### TC-E3-04 [Crítico] — Embeddings NLP
- **TT:** TT-E3-03 | **Archivo:** `src/features/nlp_embeddings.py`
- **Verificación:** `NLPEmbedder` soporta BETO, BioBERT-es, Multilingual, fallback TF-IDF
- **Esperado:** Embeddings 768-dim (BERT) o 256-dim (TF-IDF)

### TC-E3-05 [Crítico] — Baselines unimodales
- **TT:** TT-E3-04 | **Archivo:** `src/models/train_models.py`
- **Verificación:** `train_baselines()` entrena LR, RF, XGBoost con métricas por clase
- **Esperado:** 3 modelos con F1, Precision, Recall, AUC-ROC reportados

### TC-E3-06 [Crítico] — Early Fusion
- **TT:** TT-E3-05 | **Archivo:** `src/models/train_models.py`
- **Verificación:** `train_early_fusion()` concatena X_struct + X_nlp
- **Esperado:** XGBoost sobre vector combinado, métricas > baseline unimodal

### TC-E3-07 [Crítico] — Late Fusion (Stacking)
- **TT:** TT-E3-06 | **Archivo:** `src/models/train_models.py`
- **Verificación:** `train_late_fusion()` submodelo A (XGBoost struct) + B (LR NLP) + stacking
- **Esperado:** Meta-modelo LogisticRegression sobre probabilidades concatenadas

### TC-E3-08 [Alto] — Threshold tuning I-II
- **TT:** TT-E3-07 | **Archivo:** `src/evaluation/metrics.py`
- **Verificación:** `ThresholdTuner.tune()` prueba umbrales 0.05-0.50 con límite degradación F1 10%
- **Esperado:** Umbral óptimo por clase, Recall I-II maximizado

### TC-E3-09 [Alto] — Serialización del modelo
- **TT:** TT-E3-09 | **Archivo:** `src/serving/serialize.py`
- **Verificación:** `ModelSerializer.serialize()` guarda model.joblib + metadata.json + thresholds
- **Esperado:** Carga reproducible con `ModelSerializer.load()`, SHA256 hash en metadata

---

## ÉPICA 4 — Motor IA + XAI (5 items)

### TC-E4-01 [Crítico] — Carga del modelo serializado
- **TT:** TT-E4-01 | **Archivo:** `app/services/inference_service.py`
- **Verificación:** `InferenceService.load_model()` busca active_version.txt, carga con ModelSerializer
- **Esperado:** `model_loaded=True`, SHAP Explainer inicializado

### TC-E4-02 [Crítico] — Inferencia < 3 segundos
- **HU:** HU-E4-01 | **Archivo:** `app/services/inference_service.py` → `predict()`
- **Verificación:** Construye feature vector, aplica scaler/encoder, predict_proba, thresholds
- **Esperado:** `tiempo_inferencia_s < 3`, nivel_sugerido I-V, probabilidades 5 clases

### TC-E4-03 [Crítico] — Explicación SHAP clínica
- **HU:** HU-E4-02 | **Archivo:** `app/services/inference_service.py` → `explain()`
- **Verificación:** `_enrich_explanation()` traduce features a lenguaje clínico, compara MTS
- **Esperado:** Top 10 variables con nombres clínicos, waterfall plot data

### TC-E4-04 [Alto] — Campo profesional independiente
- **HU:** HU-E4-03 | **Archivo:** `app/ui/ia_classification_page.py`
- **Verificación:** Columna "Su Clasificación" nunca autocompletada, concordancia automática
- **Esperado:** Si discrepancia → exige MotivoDiscrepancia antes de continuar

### TC-E4-05 [Alto] — Comparación Early vs Late Fusion
- **HU:** HU-E4-04 | **Archivo:** `app/ui/model_comparison_page.py`
- **Verificación:** Carga metadata.json de modelos, tabla comparativa F1/AUC/Recall
- **Esperado:** Métricas lado a lado, ganador por conteo de métricas

---

## ÉPICA 5 — Auditoría y Trazabilidad (3 items)

### TC-E5-01 [Crítico] — Registro append-only
- **TT:** TT-E5-01 | **Archivo:** `app/services/audit_service.py`
- **Verificación:** `AuditService.register()` inserta en tabla Auditoria con 17 acciones
- **Esperado:** Sin DELETE permission, `@auditar` decorator funcional

### TC-E5-02 [Alto] — Consulta con 6 filtros + exportación
- **HU:** HU-E5-01 | **Archivo:** `app/services/audit_service.py` + `app/ui/audit_page.py`
- **Verificación:** Filtros: usuario, acción, fecha, entidad, ID triaje; CSV/Excel/JSON
- **Esperado:** Paginación funcional, 3 formatos de exportación

### TC-E5-03 [Alto] — Reporte HTML de triaje
- **HU:** HU-E5-02 | **Archivo:** `app/services/report_service.py`
- **Verificación:** `generate_triage_html()` con datos anonimizados, diseño A4
- **Esperado:** Paciente anonimizado, signos vitales, IA vs prof, probabilidades, disclaimer

---

## ÉPICA 6 — Dashboard y Gestión Modelos (3 items)

### TC-E6-01 [Crítico] — Dashboard con 7 KPIs
- **HU:** HU-E6-01 | **Archivo:** `app/ui/dashboard_page.py`
- **Verificación:** Métricas desde BD: total triajes, pacientes, concordancia, tiempo inf, 7-días
- **Esperado:** 5 KPI cards, distribución I-V, tendencia, semáforo de metas

### TC-E6-02 [Alto] — Gestión de modelos (3 tabs)
- **HU:** HU-E6-02 | **Archivo:** `app/ui/model_management_page.py`
- **Verificación:** Tab Disco (serializados), Tab BD (registro), Tab Registrar (form)
- **Esperado:** Activar/desactivar modelo, registrar nuevo con métricas

### TC-E6-03 [Medio] — Exportación CSV/Excel/JSON
- **HU:** HU-E6-03 | **Archivo:** `app/ui/dashboard_page.py`
- **Verificación:** 3 botones descarga con datos del dashboard
- **Esperado:** CSV con métricas, Excel multi-hoja, JSON estructurado

---

## Criterios de Entrada/Salida

| Criterio | Condición |
|---|---|
| **Entrada** | Código fuente completo, app desplegada en localhost:8501 |
| **Salida GO** | 100% críticos pass, ≥ 80% total pass |
| **Salida NO-GO** | Algún caso crítico falla |
