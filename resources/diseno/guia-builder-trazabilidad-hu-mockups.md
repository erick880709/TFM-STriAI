# Guía para el Builder — Trazabilidad HU/TT ↔ Mockups UX/UI

**Versión:** 1.0 · **Fecha:** 2026-07-19 · **Proyecto:** TFM UNIR

> **Para el builder/desarrollador:** Este documento cruza cada historia de usuario y tarea técnica de Specter con su mockup de diseño correspondiente en `resources/diseno/`. Antes de implementar cualquier HU/TT, abre el mockup asignado para conocer el diseño visual exacto (layout, colores, tipografía, interacciones, estados).

---

## 📋 Reglas de uso

1. **Abrir el mockup primero.** Cada HU tiene un archivo en `resources/diseno/mockups/pNN-*.md` que describe: layout ASCII, elementos de diseño (colores, tamaños, fuentes), interacciones (click, hover, validación) y estados (default, error, vacío, carga, éxito).
2. **Consultar el design system.** `resources/diseno/design-system.md` define la paleta Healthcare App, tipografía Corporate Trust, colores de niveles de triaje, espaciado y reglas de accesibilidad.
3. **Ver la imagen de referencia.** `resources/diseno/imagenes/pNN.png` contiene la captura visual renderizada del mockup.
4. **Las TT sin mockup** son trabajo de infraestructura/backend que no tiene UI directa — se implementan contra los criterios de aceptación de la propia TT y el documento de arquitectura.

---

## 🗺️ Matriz de Trazabilidad

### ÉPICA 1 — Fundación del Sistema

| ID | Tipo | Historia / Tarea | Mockup | Imagen | Design System |
|---|---|---|---|---|---|
| **HU-E1-01** | HU | Login de usuarios | [P01 · Login](mockups/p01-login.md) | [p01.png](imagenes/p01.png) | `design-system.md` |
| **HU-E1-02** | HU | Gestión de roles y permisos RBAC | *Sin mockup dedicado* — funcionalidad administrativa. El selector de roles se integra en sidebar. | — | Colores de badge por rol |
| **HU-E1-03** | HU | Recuperación de contraseña | [P01 · Login](mockups/p01-login.md) — enlace "¿Olvidó su contraseña?" + flujo de recuperación | [p01.png](imagenes/p01.png) | Link color: `#0891B2` |
| **HU-E1-04** | HU | Cierre automático de sesión | [P01 · Login](mockups/p01-login.md) — contador regresivo + redirección a login | [p01.png](imagenes/p01.png) | Modal de aviso: fondo `#FFF7ED` |
| **TT-E1-01** | TT | Inicializar proyecto con stack | *Sin mockup* — tarea de infraestructura. Ver `RT-002` y `RT-007`. | — | — |
| **TT-E1-02** | TT | Configurar BD y modelo de dominio | *Sin mockup* — tarea de base de datos. Ver `RD-002` y `Documento_Arquitectura` §9. | — | — |
| **TT-E1-03** | TT | Implementar TLS y cifrado | *Sin mockup* — tarea de seguridad. Ver `RNF-003`. | — | — |
| **TT-E1-04** | TT | Estructura modular del proyecto | *Sin mockup* — tarea de arquitectura. Ver `Documento_Arquitectura` §6. | — | — |

---

### ÉPICA 2 — Flujo Clínico de Triaje

| ID | Tipo | Historia / Tarea | Mockup | Imagen | Design System |
|---|---|---|---|---|---|
| **HU-E2-01** | HU | Registrar nuevo paciente | [P02 · Registro de Paciente](mockups/p02-registro-paciente.md) | [p02.png](imagenes/p02.png) | Inputs 44px, border `#A5F3FC`, ViaLlegada destacado naranja |
| **HU-E2-02** | HU | Buscar paciente existente | [P02 · Registro de Paciente](mockups/p02-registro-paciente.md) — barra de búsqueda + resultados + precarga | [p02.png](imagenes/p02.png) | Resultados paginados, hover highlight |
| **HU-E2-03** | HU | Consultar historial de triajes | [P02 · Registro de Paciente](mockups/p02-registro-paciente.md) — sección de historial + badge EpisodiosPrevios | [p02.png](imagenes/p02.png) | Badge verde `#059669` para predictor |
| **HU-E2-04** | HU | Captura de signos vitales | [P03 · Signos Vitales](mockups/p03-signos-vitales.md) | [p03.png](imagenes/p03.png) | SpO₂/FR en tarjeta roja `#DC2626`, IMC auto verde |
| **HU-E2-05** | HU | Evaluación clínica | [P04 · Evaluación Clínica](mockups/p04-evaluacion-clinica.md) | [p04.png](imagenes/p04.png) | Textarea 70px, slider dolor naranja, checkboxes |
| **HU-E2-06** | HU | Flujo de estados del triaje | *Transversal a P02→P07* — indicador de estado en cada pantalla. Badge de color según estado. | — | Badge de estado: `#0891B2` primary |
| **HU-E2-07** | HU | Reclasificación del paciente | [P07 · Validación de Triaje](mockups/p07-validacion-triaje.md) — modal/timeline de reclasificación | [p07.png](imagenes/p07.png) | Modal con motivo obligatorio, timeline histórico |
| **HU-E2-08** | HU | Cierre del evento de triaje | [P07 · Validación de Triaje](mockups/p07-validacion-triaje.md) — botón "Cerrar Evento" + checklist | [p07.png](imagenes/p07.png) | Botón `#059669`, checklist verde |

---

### ÉPICA 3 — Pipeline de Datos y Entrenamiento

| ID | Tipo | Historia / Tarea | Mockup | Notas |
|---|---|---|---|---|
| **TT-E3-01** | TT | Pipeline de ingesta y anonimización | *Sin mockup* — tarea offline. Los datasets están en `datasets/`. Ver `RT-003` + `RT-005`. | El builder debe implementar contra los criterios de done de la TT y el diagrama de pipeline en `Documento_Arquitectura` §10.2 |
| **TT-E3-02** | TT | Pipeline de limpieza y normalización | *Sin mockup* — tarea offline. | ⚠️ Datos reales tienen formatos de fecha inconsistentes (ver análisis de datasets). |
| **TT-E3-03** | TT | Embeddings NLP con BERT clínico | *Sin mockup* — tarea offline. | Usar `diagnostico` del dataset San Juan de Dios como texto de entrada. |
| **TT-E3-04** | TT | Baselines unimodales (LR, RF, XGBoost) | *Sin mockup* — tarea offline. | — |
| **TT-E3-05** | TT | Entrenamiento Early Fusion | *Sin mockup* — tarea offline. | Ver `RT-001` para arquitectura. |
| **TT-E3-06** | TT | Entrenamiento Late Fusion | *Sin mockup* — tarea offline. | ⚠️ Método de stacking pendiente de decisión experimental. |
| **TT-E3-07** | TT | Threshold tuning y evaluación | *Sin mockup* — tarea offline. | Producir métricas que alimentan P10 (Dashboard). |
| **TT-E3-08** | TT | SHAP y comparativa benchmarks | *Sin mockup* — tarea offline. | Producir gráficos SHAP que alimentan P06. |
| **TT-E3-09** | TT | Serialización del modelo | *Sin mockup* — tarea offline. | El artefacto (joblib + metadata.json) es consumido por TT-E4-01. |

---

### ÉPICA 4 — Motor de IA y Explicabilidad

| ID | Tipo | Historia / Tarea | Mockup | Imagen | Design System |
|---|---|---|---|---|---|
| **HU-E4-01** | HU | Ejecutar inferencia y ver resultados | [P05 · Clasificación IA](mockups/p05-clasificacion-ia.md) — lado izquierdo: nivel sugerido + probabilidades + metadatos | [p05.png](imagenes/p05.png) | Nivel II badge `#EA580C` 32px, barras de probabilidad coloreadas por nivel |
| **HU-E4-02** | HU | Visualizar explicación SHAP | [P05 · Clasificación IA](mockups/p05-clasificacion-ia.md) — sección inferior: variables SHAP + [P06 · Explicación SHAP](mockups/p06-explicacion-shap.md) — waterfall + ranking | [p05.png](imagenes/p05.png) + [p06.png](imagenes/p06.png) | 🟠 Naranja = aumenta prob, ⚪ Gris = neutro, 📋 MTS en verde |
| **HU-E4-03** | HU | Validar clasificación y concordancia | [P05 · Clasificación IA](mockups/p05-clasificacion-ia.md) — panel derecho: campo profesional + [P07 · Validación](mockups/p07-validacion-triaje.md) — confirmación | [p05.png](imagenes/p05.png) + [p07.png](imagenes/p07.png) | Selector profesional borde naranja, badge concordancia verde |
| **HU-E4-04** | HU | Comparar modelos (early vs late) | [P08 · Comparación de Modelos](mockups/p08-comparacion-modelos.md) | [p08.png](imagenes/p08.png) | Tabla comparativa, delta en verde, badge ganador |
| **TT-E4-01** | TT | Servicio de carga del modelo serializado | *Sin mockup* — tarea de backend. El modelo se carga al iniciar Streamlit. | — |

---

### ÉPICA 5 — Auditoría y Trazabilidad

| ID | Tipo | Historia / Tarea | Mockup | Imagen | Design System |
|---|---|---|---|---|---|
| **HU-E5-01** | HU | Consultar y exportar auditoría | [P11 · Auditoría](mockups/p11-auditoria.md) | [p11.png](imagenes/p11.png) | Filtros inline, tabla con header `#E8F1F6`, botones export |
| **HU-E5-02** | HU | Generar registro de triaje descargable | [P12 · Registro de Triaje PDF](mockups/p12-registro-triaje-pdf.md) | [p12.png](imagenes/p12.png) | Formato PDF con membrete, secciones, anonimización automática |
| **TT-E5-01** | TT | Implementar registro de auditoría append-only | *Sin mockup* — tarea de backend. El decorador `@auditar` es transparente para la UI. | — |

---

### ÉPICA 6 — Dashboard y Gestión de Modelos

| ID | Tipo | Historia / Tarea | Mockup | Imagen | Design System |
|---|---|---|---|---|---|
| **HU-E6-01** | HU | Dashboard operativo con indicadores | [P10 · Dashboard Operativo](mockups/p10-dashboard-operativo.md) | [p10.png](imagenes/p10.png) | KPIs 170px, barras distribución coloreadas I-V, semáforo 🟢 |
| **HU-E6-02** | HU | Gestión de modelos (CRUD, versionado, rollback) | [P09 · Gestión de Modelos](mockups/p09-gestion-modelos.md) | [p09.png](imagenes/p09.png) | Tabla con badges ACTIVO (verde) / EN VALID. (gris), botones Activar/Rollb. |
| **HU-E6-03** | HU | Exportación de reportes | [P10 · Dashboard](mockups/p10-dashboard-operativo.md) — botones exportar + [P11 · Auditoría](mockups/p11-auditoria.md) — botones CSV/Excel/PDF | [p10.png](imagenes/p10.png) + [p11.png](imagenes/p11.png) | Botones outline `#0891B2` |

---

## 📊 Resumen de Cobertura

| Épica | Total HU/TT | Con mockup directo | Sin mockup (infra/backend) | Cobertura UX |
|---|---|---|---|---|
| E1 · Fundación | 8 | 3 (P01) | 5 (TT infra) | 37% |
| E2 · Flujo Clínico | 8 | 8 (P02→P07) | 0 | **100%** |
| E3 · Pipeline | 9 | 0 | 9 (TT offline) | 0% (no aplica) |
| E4 · Motor IA + XAI | 5 | 4 (P05, P06, P07, P08) | 1 (TT backend) | 80% |
| E5 · Auditoría | 3 | 2 (P11, P12) | 1 (TT backend) | 67% |
| E6 · Dashboard | 3 | 3 (P09, P10, P11) | 0 | **100%** |
| **TOTAL** | **36** | **20** | **16** | — |

---

## 🎯 Orden de implementación recomendado para el builder

```
Fase 1 — Fundación (E1): TT-E1-01 → TT-E1-02 → TT-E1-04 → HU-E1-01 [P01] → HU-E1-02
                         → TT-E1-03 → HU-E1-03 [P01] → HU-E1-04 [P01]

Fase 2 — Flujo Clínico (E2): HU-E2-01 [P02] → HU-E2-02 [P02] → HU-E2-04 [P03]
                              → HU-E2-05 [P04] → HU-E2-06 [P02-P07]
                              → HU-E2-03 [P02] → HU-E2-08 [P07] → HU-E2-07 [P07]

Fase 2b — Pipeline (E3, paralelo): TT-E3-01 → TT-E3-02 → TT-E3-03 → TT-E3-04
                                    → TT-E3-05 → TT-E3-06 → TT-E3-07
                                    → TT-E3-08 → TT-E3-09

Fase 3 — Motor IA (E4): TT-E4-01 → HU-E4-01 [P05] → HU-E4-02 [P05+P06]
                        → HU-E4-03 [P05+P07] → HU-E4-04 [P08]

Fase 4 — Auditoría (E5): TT-E5-01 → HU-E5-01 [P11] → HU-E5-02 [P12]

Fase 5 — Dashboard (E6): HU-E6-02 [P09] → HU-E6-01 [P10] → HU-E6-03 [P10+P11]
```

> `[PXX]` = Abrir `resources/diseno/mockups/pXX-*.md` antes de implementar.

---

## ⚠️ Validaciones y hallazgos

| # | Hallazgo | Acción |
|---|---|---|
| 1 | ✅ **Cobertura completa del flujo clínico.** Las 7 pantallas del flujo principal (P01→P07) cubren el 100% de las HU de E2. | Sin acción. |
| 2 | ✅ **HU-E4-01, HU-E4-02, HU-E4-03 comparten P05.** La pantalla de Clasificación IA unifica 3 historias de usuario — el builder debe implementarlas juntas en una sola vista. | Implementar P05 como una sola pantalla con 3 secciones: (1) resultados IA, (2) SHAP, (3) campo profesional. |
| 3 | ⚠️ **HU-E1-02 (Gestión de roles) no tiene mockup dedicado.** La funcionalidad es administrativa y se integra en sidebar + página de admin. | Usar P01 como referencia de estilo. La UI de gestión de usuarios sigue el patrón de tabla + formulario de P09. |
| 4 | ✅ **TT-E3-01 a TT-E3-09 no requieren mockup.** Son tareas de pipeline offline que producen artefactos (modelo serializado, métricas) consumidos por E4 y E6. | Los gráficos SHAP generados en TT-E3-08 deben ser visualmente compatibles con P06. |
| 5 | ✅ **Design system cubre todas las pantallas.** `design-system.md` define colores de niveles de triaje (I-V) que se usan en P03, P05, P07, P10. | Usar variables CSS o constantes Python para los 5 colores de triaje. |
