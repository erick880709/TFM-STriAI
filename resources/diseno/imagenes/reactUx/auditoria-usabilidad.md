# 📋 Auditoría de Usabilidad — React Frontend v2.0

**App:** STriAI — Sistema de Triaje Multimodal IA  
**URL:** http://localhost:8000  
**Fecha:** 2026-07-21  
**Audiencia:** Personal médico (médicos, enfermeras, administrativos)  
**Contexto:** Servicio de Urgencias · Colombia

---

## 🔴 Hallazgos críticos de usabilidad médica

| # | Pantalla | Issue | Impacto clínico |
|---|----------|-------|-----------------|
| 1 | **Sidebar** | 256px fijo, no colapsable. En tablets verticales (768px) ocupa 33% del ancho | Alto — reduce espacio para datos clínicos |
| 2 | **Flujo clínico** | Sin indicador de progreso visible (stepper). El médico no sabe en qué paso está | Alto — riesgo de saltar pasos del triaje |
| 3 | **Signos Vitales** | Labels en inglés técnico (`frecuencia_cardiaca`) sin tooltips clínicos | Medio — confusión con terminología |
| 4 | **Clasificación IA** | Sin indicador de confianza visual (solo números). El médico necesita ver si la IA está "segura" | Alto — decisiones clínicas basadas en IA |
| 5 | **Dashboard** | KPIs sin códigos de color semánticos. "Tasa Cierre 0%" es rojo aunque no es malo | Medio — falsa alarma visual |
| 6 | **Tablas** | Sin ordenamiento por columna. El médico no puede ordenar triajes por fecha/gravedad | Alto — pérdida de tiempo en urgencias |
| 7 | **Formularios** | Sin guardado automático. Si el navegador crashea, se pierden los signos vitales | Alto — riesgo de repetir trabajo clínico |
| 8 | **Responsive** | Sidebar no se oculta en móvil. La app es inusable en tablet 768px | Crítico — urgencias usa tablets |
| 9 | **Botones** | Tamaño < 44px en algunos botones de acción. Difícil de tocar en pantalla táctil | Alto — errores de tap en entorno rápido |
| 10 | **Contraste** | Texto secundario (#64748B) sobre fondo cyan (#ECFEFF) = ratio 3.2:1. No cumple WCAG AA (4.5:1) | Medio — fatiga visual en turnos largos |

---

## 🟠 Issues de UX por pantalla

### P01 — Login
- ❌ Sin tecla Enter en campo contraseña para submit inmediato
- ❌ Footer dice "v2.0" — irrelevante para médico
- ✅ Propuesta: Agregar "Entrar con tecla Enter", footer con nombre del hospital

### P02 — Registro de Paciente
- ❌ Formulario muy largo sin secciones colapsables
- ❌ Select de 32 departamentos sin búsqueda
- ❌ Sin validación en tiempo real del número de documento
- ✅ Propuesta: Secciones colapsables, búsqueda en selects, validación async de documento duplicado

### P03 — Signos Vitales
- ❌ Sin valores de referencia visibles junto al input
- ❌ Labels en snake_case visible (`frecuencia_cardiaca`)
- ❌ Sin histórico de signos del paciente actual
- ✅ Propuesta: Rangos normales como placeholder, labels en español médico, mini-historial

### P04 — Evaluación Clínica
- ❌ Escala de Glasgow sin ayuda visual de los criterios
- ❌ Slider de dolor sin caras de Wong-Baker
- ❌ Sin guardado automático parcial
- ✅ Propuesta: Tooltips con criterios Glasgow, escala visual de dolor, autosave cada 30s

### P05 — Clasificación IA
- ❌ Sin indicador visual de "confianza" del modelo
- ❌ SHAP terms técnicos sin glosario
- ❌ Sin comparativa visual IA vs criterios del médico
- ✅ Propuesta: Barra de confianza coloreada, tooltips en features SHAP, columna "Tu decisión"

### P06 — Validación y Cierre
- ❌ Stepper falso (no verifica pasos reales)
- ❌ Sin resumen de todo el triaje antes de cerrar
- ✅ Propuesta: Stepper real con validación, resumen pre-cierre

### P07 — Dashboard
- ❌ Sin selector de rango de fechas
- ❌ KPIs sin benchmarks ("vs. mes anterior")
- ✅ Propuesta: DateRangePicker, comparativas, exportar PDF

### P08-P12 — Soporte
- ❌ Tablas sin ordenamiento/filtrado avanzado
- ❌ Sin atajos de teclado (Ej: Ctrl+B para buscar paciente)
- ✅ Propuesta: Columnas ordenables, filtros rápidos, atajos de teclado

---

## 📱 Plan de Responsive Design

| Breakpoint | Layout | Sidebar | Grid |
|------------|--------|---------|------|
| ≥ 1024px (Desktop) | Sidebar + Main | 256px fijo | 2-5 columnas |
| 768-1023px (Tablet H) | Sidebar colapsable | Iconos 64px | 2 columnas |
| < 768px (Tablet V / Móvil) | Bottom nav | Hidden, hamburger menu | 1 columna |

---

## 🎯 Prioridades para entorno médico

| Prioridad | Acción | Esfuerzo |
|-----------|--------|----------|
| P0 | Sidebar colapsable + responsive | Alto |
| P0 | Stepper real en flujo clínico | Medio |
| P0 | Validación async de documento duplicado | Bajo |
| P1 | Guardado automático en formularios | Alto |
| P1 | Labels en español médico | Bajo |
| P1 | Ordenamiento en tablas | Medio |
| P2 | Atajos de teclado | Medio |
| P2 | Escala de dolor visual (Wong-Baker) | Bajo |
