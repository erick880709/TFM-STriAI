# Resumen Ejecutivo — Sistema de Triaje Multimodal basado en IA (Colombia)

**Cliente:** Trabajo Fin de Máster — Máster Universitario en Inteligencia Artificial, UNIR
**Fecha del documento:** Julio 2026
**Documentos fuente:** `CONTEXT TRIA.txt` (Documento Maestro de Contexto Funcional, 3558 líneas), `CONTEXTO_TRIAJE.txt` v2.0, `contexto-tfm.md`, `01-CONTEXTO-MAESTRO-CONSOLIDADO.md`, `02-ESPECIFICACION-TECNICA-MODELOS-IA.md`, `03-CATALOGO-DATOS-Y-VARIABLES.md`, `04-ESPECIFICACION-APLICACION-DEMO.md`, `06-CAPTURA-SINTOMAS-Y-COMPARATIVA-IA-PROFESIONAL.md`

## Objetivo y alcance del proyecto

Diseñar, implementar y validar un sistema inteligente multimodal basado en Inteligencia Artificial que asista el proceso de clasificación de pacientes en servicios de urgencias colombianos, integrando información clínica estructurada (signos vitales, demográficos, antecedentes) y no estructurada (texto libre de notas clínicas) para predecir los cinco niveles de triaje definidos por la Resolución 5596 de 2015 del Ministerio de Salud y Protección Social de Colombia.

El sistema es un **Clinical Decision Support System (CDSS)** — apoya, nunca reemplaza, al profesional sanitario. Toda predicción incluye explicabilidad (SHAP) y trazabilidad completa.

**Alcance del prototipo (TFM Tipología 2+3):** modelo entrenado y evaluado offline + demo funcional interactiva (Streamlit o Flask) con flujo completo de triaje y dashboard de indicadores.

**Autores:** Medina Betancur, Diego Andrés · Rivera Villanueva, Leyniker · Soto Díaz, Erick Duván
**Directora:** Damaris Fuentes Lorenzo

## Plazos

- El TFM se encuentra en desarrollo con Capítulos 1-3 redactados (Introducción, Estado del Arte, Objetivos y Metodología).
- Capítulos 4-6 pendientes (Desarrollo, Resultados, Conclusiones).
- La autorización ética del Hospital San Juan de Dios está **APROBADA** (según `CONTEXTO_TRIAJE.txt` v2.0, 16 jul 2026), pendiente de reflejar en el PDF del TFM.

## Presupuesto / modelo de contratación

No aplica (proyecto académico). Los datos provienen de fuentes públicas (datos.gov.co, BDUA/ADRES, Supersalud), acceso acreditado a MIMIC-IV-ED (PhysioNet), y registro clínico del Hospital San Juan de Dios con autorización ética aprobada.

## Criterios de evaluación de la propuesta

No aplica (no es una licitación). El proyecto será evaluado por el tribunal de TFM de UNIR con base en: calidad técnica de los modelos, rigor metodológico, completitud funcional de la demo, calidad de la documentación y relevancia clínica.

## Stakeholders identificados

| Stakeholder | Interés | Influencia |
|---|---|---|
| Pacientes | Muy Alto | Medio |
| Enfermería de Triaje | Muy Alto | Muy Alto |
| Médicos de Urgencias | Muy Alto | Muy Alto |
| Coordinador de Urgencias / Dirección Médica | Alto | Muy Alto |
| Comité de Ética (Hospital San Juan de Dios) | Alto | Muy Alto |
| Equipo IA / Científicos de Datos / Arquitectos | Muy Alto | Alto |
| Ministerio de Salud y Protección Social | Muy Alto | Muy Alto |
| Investigadores UNIR | Alto | Medio |

## Entregables esperados

1. **Modelo de IA entrenado y validado** con métricas de desempeño documentadas (F1 ≥ 0.82, Precisión ≥ 0.85, Recall ≥ 0.80, AUC-ROC ≥ 0.87).
2. **Demo funcional interactiva** con flujo completo de triaje (12 pantallas: registro → signos vitales → evaluación → IA → SHAP → validación) + dashboard de indicadores.
3. **Documento TFM completo** (6 capítulos + apéndices).
4. **Código fuente** documentado y reproducible (pipeline de entrenamiento + aplicación demo).
5. **Documentación de arquitectura** y modelo de datos.

## Supuestos y restricciones generales

- **Supuesto 1:** La autorización ética del Hospital San Juan de Dios permite el uso de datos clínicos reales para fine-tuning del modelo.
- **Supuesto 2:** El idioma principal de los textos clínicos es español colombiano; el modelo NLP debe estar optimizado para este contexto.
- **Restricción 1:** MIMIC-IV-ED solo es válido como preentrenamiento; el modelo final DEBE incluir datos colombianos (sin esto, el modelo no es clínicamente válido por sesgo geográfico).
- **Restricción 2:** Cumplimiento obligatorio de la Ley 1581 de 2012 (protección de datos personales) — anonimización antes de cualquier procesamiento.
- **Restricción 3:** La IA nunca reemplaza al profesional; toda clasificación debe ser validada por personal sanitario.
- **Restricción 4:** El sistema no es un producto productivo; es un prototipo académico para validación de viabilidad técnica y clínica.

## Glosario

| Término | Definición |
|---|---|
| **Triaje** | Proceso de clasificación inicial del paciente según gravedad clínica (Resolución 5596/2015) |
| **Multimodal** | Integración de datos estructurados (numéricos/categóricos) y no estructurados (texto libre) en un mismo modelo predictivo |
| **Early Fusion** | Concatenación de features estructuradas + embeddings de texto antes del clasificador |
| **Late Fusion** | Dos submodelos independientes (estructurado + texto) cuyas salidas se combinan |
| **XAI (eXplainable AI)** | Técnicas que permiten interpretar el comportamiento del modelo (SHAP en este proyecto) |
| **SHAP** | SHapley Additive exPlanations — método para cuantificar la contribución de cada variable a una predicción |
| **Inferencia** | Proceso mediante el cual el modelo genera una predicción a partir de variables de entrada |
| **CDSS** | Clinical Decision Support System — sistema de apoyo a la decisión clínica |
| **Deriva (Drift)** | Cambio en la distribución de los datos que puede degradar el rendimiento del modelo con el tiempo |
| **Concordancia** | Medida de acuerdo entre la clasificación sugerida por IA y la asignada por el profesional |
| **MIMIC-IV-ED** | Medical Information Mart for Intensive Care — Emergency Department, base de datos pública de admissions a urgencias (PhysioNet) |
| **BDUA** | Base de Datos Única de Afiliados (ADRES) — información de afiliación al sistema de salud colombiano |

## Resumen cuantitativo de la extracción

- **Requerimientos funcionales extraídos:** 13 (agrupados por módulo: PAC, TRI, VIT, EVA, NLP, IA, XAI, AUD, REP, MOD, SEC, INT, más las reglas de negocio RNA/RNS/RNAU/RNGD/RNQ/RNX/RNP como catálogo integrado en los RF correspondientes)
- **Requerimientos no funcionales extraídos:** 7 (RNF-001 a RNF-007: rendimiento, disponibilidad, seguridad, usabilidad, trazabilidad, metas cuantitativas, mantenibilidad)
- **Requisitos técnicos extraídos:** 7 (RT-001 a RT-007: arquitectura multimodal, stack tecnológico, fuentes de datos, desbalance de clases, pipeline de entrenamiento, explicabilidad SHAP, entorno de despliegue)
- **Información de diseño extraída:** 3 (RD-001 a RD-003: inventario de pantallas, modelo de dominio extendido, flujo de clasificación y validación)

## Vacíos y riesgos detectados

1. **Stack de la demo sin decidir (Streamlit vs. Flask).** Ambos se mencionan en los documentos fuente sin una decisión firme. Streamlit es la recomendación técnica (menor esfuerzo para prototipo), pero requiere confirmación de la directora. Ver `05-PENDIENTES-PARA-DIRECTORA.md` #1.

2. **RF-IA-003 contradictorio en el documento fuente.** `CONTEXT_TRIA.txt` describe la selección de predicción como "clase con mayor probabilidad" (argmax puro), pero la decisión técnica cerrada establece umbral optimizado por clase para Niveles I-II priorizando Recall. Esta extracción usa la versión corregida, pero el documento maestro funcional debe actualizarse antes de usarlo como entregable formal. Ver `05-PENDIENTES-PARA-DIRECTORA.md` #3.

3. **Método de combinación en late fusion no definido.** Promedio ponderado, stacking o meta-clasificador queda como decisión experimental de la Fase 3. No es una ambigüedad de contexto sino un resultado pendiente. Ver `05-PENDIENTES-PARA-DIRECTORA.md` #4.

4. **Autorización ética no reflejada en el PDF del TFM.** Según `CONTEXTO_TRIAJE.txt` v2.0 (16 jul 2026) el Comité de Ética del Hospital San Juan de Dios ya aprobó, pero el PDF del TFM (documento oficial) aún dice "requiere autorización, Art. 2.7". Actualizar el Cap. 3 antes del depósito. Ver `05-PENDIENTES-PARA-DIRECTORA.md` #2.

5. **Dos variables de alto peso predictivo ausentes en la especificación funcional original.** `ViaLlegada` y `EpisodiosPreviosUrgencias` no existían en el catálogo de entidades ni en los módulos funcionales. Fueron añadidas en `03-CATALOGO-DATOS-Y-VARIABLES.md`. Los formularios de la demo deben incluirlas.

6. **Sesgo de anclaje en la comparativa IA vs. profesional.** El diseño actual (profesional ve primero la sugerencia de IA y luego clasifica) es el flujo clínico natural pero invalida la comparativa como medida de acuerdo interobservador independiente. Documentar como limitación metodológica en el Cap. 6 del TFM. Ver `06-CAPTURA-SINTOMAS-Y-COMPARATIVA-IA-PROFESIONAL.md` §2.

7. **Pendientes normativos del TFM.** Orden alfabético de autores en portada, sección "Organización del trabajo en grupo" y herramienta anti-plagio son bloqueantes para el depósito. Ver `05-PENDIENTES-PARA-DIRECTORA.md` #5.
