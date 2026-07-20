# Línea Base — Sistema de Triaje Multimodal IA

**Fecha:** 2026-07-19 · **Versión:** 1.0 · **Proyecto:** TFM UNIR

---

## Resumen de fuentes validadas

| Bloque | Estado | Fuente |
|---|---|---|
| Contexto de negocio | ✅ Definido | `01-CONTEXTO-MAESTRO-CONSOLIDADO.md`, `contexto-tfm.md` |
| Stack tecnológico | ✅ Definido | RT-002 |
| Arquitectura de fusión | ✅ Definido | RT-001 |
| Fuentes de datos | ✅ Definido | RT-003 |
| Modelo de dominio | ✅ Definido | RD-002 |
| Flujo de clasificación | ✅ Definido | RD-003 |
| Pantallas | ✅ Definido | RD-001 |
| Seguridad | ✅ Definido | RNF-003, RF-SEC |
| Rendimiento | ✅ Definido | RNF-001, RNF-006 |
| Disponibilidad | ✅ Definido | RNF-002 |
| Trazabilidad | ✅ Definido | RNF-005, RF-AUD |
| Explicabilidad | ✅ Definido | RT-006, RF-XAI |
| Mantenibilidad | ✅ Definido | RNF-007 |
| Entorno despliegue | ✅ Definido | RT-007 |
| Métricas modelo | ✅ Definido | RNF-006 |
| Pipeline entrenamiento | ✅ Definido | RT-005 |
| Manejo desbalance | ✅ Definido | RT-004 |
| Framework UI | ⚠️ Pendiente | Streamlit (recomendado) vs Flask — ADR-002 |
| Método late fusion | ⚠️ Experimental | ADR-005 |
| Gobernanza IA | ✅ Definido | RNS-009, RNS-010, RNA-001 a 010 |

---

## Validación de la línea base ML/IA

| Aspecto | Estado | Fuente |
|---|---|---|
| Rol del sistema (apoyo, no autónomo) | ✅ Definido | RNA-001 |
| Anonimización obligatoria | ✅ Definido | RNS-009, RNS-010, Ley 1581/2012 |
| Autorización ética | ✅ Aprobada | Hospital San Juan de Dios (CONTEXTO_TRIAJE.txt v2.0) |
| Trazabilidad de predicciones | ✅ Definido | RNAU-001 a 006 |
| Detección de deriva | ✅ Previsto | RNA-010 |
| Reproducibilidad del entrenamiento | ✅ Definido | RNA-004, RT-005 |
| Métricas por clase | ✅ Definido | RNF-006 |
| Sesgo geográfico documentado | ✅ Identificado | RT-003, Riesgos |
| Sesgo de anclaje documentado | ✅ Identificado | RD-003, Riesgos |

---

## Definiciones de arquitectura utilizadas

| ID | Archivo | Decisiones incorporadas |
|---|---|---|
| RNF-001 | Rendimiento — Inferencia y concurrencia | < 3s, 10 concurrentes, SHAP no bloqueante |
| RNF-002 | Disponibilidad y escalabilidad | Modo degradado sin IA, arquitectura desacoplada |
| RNF-003 | Seguridad y protección de datos | TLS, cifrado en reposo, RBAC, Ley 1581 |
| RNF-004 | Usabilidad entorno clínico | < 5 min triaje, ≤ 3 pantallas, alertas visuales |
| RNF-005 | Trazabilidad y gobierno del dato | Append-only, catálogos centralizados |
| RNF-006 | Metas cuantitativas modelo | F1 ≥ 0.82, Recall priorizado I-II |
| RNF-007 | Mantenibilidad y extensibilidad | Arquitectura modular, config externalizada |
| RT-001 | Arquitectura multimodal fusión | Early + Late Fusion, baselines, criterio ganador |
| RT-002 | Stack tecnológico | Python 3.10+, scikit-learn, XGBoost, BERT, SHAP, Streamlit |
| RT-003 | Fuentes de datos | 5 fuentes, mapeo a entidades |
| RT-004 | Desbalance de clases y umbral | Class weights, SMOTE, threshold tuning I-II |
| RT-005 | Pipeline técnico entrenamiento | 13 pasos, reproducibilidad |
| RT-006 | Explicabilidad SHAP XAI | TreeExplainer, contrato de 4 elementos |
| RT-007 | Entorno despliegue demo | App autocontenida, SQLite, modelo serializado |

## Modelos de diseño utilizados

| ID | Archivo | Decisiones incorporadas |
|---|---|---|
| RD-001 | Inventario de pantallas | 12 pantallas (7 flujo + 5 soporte) |
| RD-002 | Modelo de dominio extendido | ENT-001 a 012 con ViaLlegada, EpisodiosPrevios, concordancia |
| RD-003 | Flujo clasificación IA + validación | 6 pasos, campo independiente del profesional |
