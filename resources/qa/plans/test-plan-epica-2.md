# Plan de Pruebas — Épica 2: Flujo Clínico de Triaje

**Versión:** 1.0 · **Fecha:** 2026-07-19 · **Run ID:** run-001
**Proyecto:** TFM UNIR · **Sistema:** Triaje Multimodal IA
**Entorno:** `http://localhost:8501` · **Tipo:** QA Manual + Código

---

## 1. Objetivo

Verificar los 8 ítems de la Épica 2 (Flujo Clínico de Triaje):
- Registro de pacientes con detección de duplicados ( HU-E2-01)
- Búsqueda de pacientes (HU-E2-02)
- Historial de triajes (HU-E2-03)
- Captura de 8 signos vitales con validación y alertas (HU-E2-04)
- Evaluación clínica completa (HU-E2-05)
- Máquina de 7 estados del triaje (HU-E2-06)
- Reclasificación con motivo obligatorio (HU-E2-07)
- Cierre de evento con validación de concordancia (HU-E2-08)

---

## 2. Alcance

### ✅ IN SCOPE (16 escenarios)

| ID | HU | Escenario | Prioridad | Tipo |
|---|---|---|---|---|
| TC-E2-01 | HU-E2-01 | Registrar nuevo paciente con datos válidos | 🔴 Crítico | E2E |
| TC-E2-02 | HU-E2-01 | Detección de documento duplicado | 🔴 Crítico | E2E |
| TC-E2-03 | HU-E2-01 | Validación de campos obligatorios | 🟠 Alto | Unitario |
| TC-E2-04 | HU-E2-02 | Buscar paciente por número de documento | 🟠 Alto | E2E |
| TC-E2-05 | HU-E2-02 | Buscar paciente sin resultados | 🟡 Medio | E2E |
| TC-E2-06 | HU-E2-03 | Consultar historial de triajes de un paciente | 🟠 Alto | E2E |
| TC-E2-07 | HU-E2-04 | Captura de signos vitales con valores normales | 🔴 Crítico | E2E |
| TC-E2-08 | HU-E2-04 | Alerta visual por SpO₂ crítica (< 90%) | 🔴 Crítico | E2E |
| TC-E2-09 | HU-E2-04 | Cálculo automático de IMC | 🟡 Medio | E2E |
| TC-E2-10 | HU-E2-05 | Evaluación clínica completa (todos los campos) | 🔴 Crítico | E2E |
| TC-E2-11 | HU-E2-06 | Transición de estados Registrado → EnEvaluación → PendienteIA | 🔴 Crítico | Integración |
| TC-E2-12 | HU-E2-06 | Intento de transición inválida (Cerrado → Registrado) | 🟠 Alto | Unitario |
| TC-E2-13 | HU-E2-07 | Reclasificación con motivo obligatorio | 🟠 Alto | E2E |
| TC-E2-14 | HU-E2-07 | Reclasificación sin motivo (debe fallar) | 🟡 Medio | Unitario |
| TC-E2-15 | HU-E2-08 | Cierre de evento con concordancia IA = Profesional | 🔴 Crítico | E2E |
| TC-E2-16 | HU-E2-08 | Cierre bloqueado por discrepancia sin motivo | 🟠 Alto | E2E |

### ❌ OUT OF SCOPE
- Pruebas de carga/estrés sobre el flujo clínico
- Integración con HCE (Historia Clínica Electrónica)
- Ejecución real del modelo IA (es Épica 4)

---

## 3. Matriz de Escenarios Detallada

### TC-E2-01 [Crítico] — Registrar nuevo paciente con datos válidos
- **HU:** HU-E2-01
- **Precondición:** Login como `enfermera_01`, BD inicializada
- **Pasos:**
  1. Navegar a "📝 Registrar Paciente"
  2. Seleccionar Tipo Documento: "Cédula de Ciudadanía"
  3. Ingresar Número Documento: `1234567890`
  4. Ingresar Fecha Nacimiento: `1985-06-15`
  5. Seleccionar Sexo: "Masculino"
  6. Seleccionar Vía Llegada: "Particular"
  7. Clic en "Registrar Paciente y Crear Triaje"
- **Resultado esperado:**
  - Mensaje "✅ Paciente registrado"
  - Mensaje "📋 Evento de triaje creado: tri-xxxx — Estado: Registrado"
  - Redirección automática a Signos Vitales
- **Datos:** Doc=1234567890, FNac=1985-06-15, Sexo=M, Via=Particular

### TC-E2-02 [Crítico] — Detección de documento duplicado
- **HU:** HU-E2-01
- **Precondición:** Paciente con documento `1234567890` ya existe (de TC-E2-01)
- **Pasos:**
  1. Intentar registrar paciente con el mismo Número Documento `1234567890`
  2. Completar el resto de campos
  3. Clic en "Registrar"
- **Resultado esperado:**
  - Panel naranja "⚠️ Paciente ya registrado"
  - Muestra datos del paciente existente
  - Botón "📋 Usar este paciente (nuevo triaje)" disponible
  - Botón "📜 Ver historial completo" disponible

### TC-E2-03 [Alto] — Validación de campos obligatorios
- **HU:** HU-E2-01
- **Precondición:** Formulario de registro abierto
- **Pasos:**
  1. Dejar Número Documento vacío
  2. Dejar Fecha Nacimiento vacía
  3. Clic en "Registrar"
- **Resultado esperado:**
  - Mensaje "❌ Número de documento es obligatorio"
  - Mensaje "❌ Fecha de nacimiento es obligatoria"
  - No se crea el paciente

### TC-E2-04 [Alto] — Buscar paciente por documento
- **HU:** HU-E2-02
- **Precondición:** Al menos un paciente registrado (TC-E2-01)
- **Pasos:**
  1. Ir a pestaña "🔍 Buscar Paciente"
  2. Ingresar `1234567890` en el campo de búsqueda
  3. Clic en "Buscar"
- **Resultado esperado:**
  - "1 paciente(s) encontrado(s)"
  - Tarjeta con datos del paciente: tipo doc, número, edad, sexo, vía llegada
  - Botones "📋 Nuevo Triaje" y "📜 Historial"

### TC-E2-05 [Medio] — Buscar sin resultados
- **HU:** HU-E2-02
- **Precondición:** BD con pacientes
- **Pasos:**
  1. Buscar documento `9999999999`
- **Resultado esperado:** "🔍 No se encontraron pacientes con ese criterio."

### TC-E2-06 [Alto] — Historial de triajes
- **HU:** HU-E2-03
- **Precondición:** Paciente con al menos un triaje
- **Pasos:**
  1. Buscar paciente existente
  2. Clic en "📜 Historial"
- **Resultado esperado:**
  - "📂 Historial del Paciente" con datos demográficos
  - Lista de eventos de triaje: ID, fecha ingreso, estado, nivel IA/prof
  - Expander "📋 Detalles" con signos vitales y evaluación

### TC-E2-07 [Crítico] — Signos vitales con valores normales
- **HU:** HU-E2-04
- **Precondición:** Evento de triaje activo
- **Pasos:**
  1. Ingresar SpO₂: 98, FR: 16, FC: 72, Temp: 36.5
  2. Ingresar PA sistólica: 120, PA diastólica: 80
  3. Ingresar Peso: 70, Talla: 170
  4. Clic en "💾 Guardar y Continuar"
- **Resultado esperado:**
  - IMC calculado: 24.2 (Peso normal, verde)
  - Sin alertas rojas
  - "✅ Signos vitales guardados correctamente"
  - Redirección a Evaluación Clínica

### TC-E2-08 [Crítico] — Alerta SpO₂ crítica
- **HU:** HU-E2-04
- **Precondición:** Evento de triaje activo
- **Pasos:**
  1. Ingresar SpO₂: 88
  2. Ingresar resto de signos normales
  3. Observar alertas
- **Resultado esperado:**
  - Alerta roja "⚠️ SpO₂ CRÍTICA — Posible hipoxemia (< 90%)"
  - Tarjeta de prioridad alta resaltada

### TC-E2-09 [Medio] — Cálculo automático IMC
- **HU:** HU-E2-04
- **Precondición:** Evento activo
- **Pasos:**
  1. Ingresar Peso: 95, Talla: 165
  2. Verificar IMC calculado
- **Resultado esperado:** IMC: 34.9 (Obesidad, rojo)

### TC-E2-10 [Crítico] — Evaluación clínica completa
- **HU:** HU-E2-05
- **Precondición:** Signos vitales guardados
- **Pasos:**
  1. Seleccionar Motivo Categoría: "Dolor torácico"
  2. Ingresar texto libre: "Paciente refiere dolor opresivo..."
  3. Ajustar slider dolor a 7
  4. Ingresar Glasgow: 15
  5. Seleccionar Nivel Conciencia: "Alerta"
  6. Marcar antecedentes: HTA, Diabetes
  7. Ingresar Episodios Previos: 3
  8. Ingresar Alergias: "Penicilina"
  9. Clic en "🧠 Guardar y Ejecutar IA"
- **Resultado esperado:**
  - "✅ Evaluación clínica guardada correctamente"
  - Redirección a Clasificación IA

### TC-E2-11 [Crítico] — Transiciones de estado
- **HU:** HU-E2-06
- **Precondición:** Flujo completo ejecutado
- **Pasos:**
  1. Verificar estado inicial después de registro: "Registrado"
  2. Después de guardar signos vitales: "EnEvaluación"
  3. Después de guardar evaluación clínica: "PendienteIA"
- **Resultado esperado:** Las 3 transiciones ocurren correctamente

### TC-E2-12 [Alto] — Transición inválida
- **HU:** HU-E2-06
- **Precondición:** N/A (verificación código)
- **Pasos:**
  1. Verificar `TRANSICIONES_VALIDAS` en `triage_service.py`
- **Resultado esperado:**
  - "Cerrado" no tiene destinos (estado terminal)
  - "Registrado" solo puede ir a "EnEvaluacion" o "Cancelado"

### TC-E2-13 [Alto] — Reclasificación con motivo
- **HU:** HU-E2-07
- **Precondición:** Evento en estado "Validado"
- **Pasos:**
  1. En pantalla de Validación, seleccionar nuevo nivel en "Reclasificar"
  2. Ingresar motivo: "El paciente presenta deterioro respiratorio"
  3. Clic en "🔄 Reclasificar"
- **Resultado esperado:**
  - "✅ Paciente reclasificado a Nivel X"
  - Nivel anterior preservado en historial
  - Evento vuelve a estado "Clasificado"

### TC-E2-14 [Medio] — Reclasificación sin motivo (falla)
- **HU:** HU-E2-07
- **Precondición:** Evento en estado "Validado"
- **Pasos:**
  1. Seleccionar nuevo nivel sin escribir motivo
  2. Intentar reclasificar
- **Resultado esperado:** Botón deshabilitado o error "El motivo es obligatorio"

### TC-E2-15 [Crítico] — Cierre con concordancia
- **HU:** HU-E2-08
- **Precondición:** Evento con clasificación IA y profesional
- **Pasos:**
  1. En Validación, verificar concordancia (IA == Profesional)
  2. Clic en "✅ Cerrar Evento de Triaje"
- **Resultado esperado:**
  - "🎉 Evento cerrado exitosamente" + balloons
  - Estado → "Cerrado"
  - Botón "📄 Descargar Registro de Triaje (HTML)" disponible
  - Botón "📝 Iniciar Nuevo Triaje"

### TC-E2-16 [Alto] — Cierre bloqueado por discrepancia
- **HU:** HU-E2-08
- **Precondición:** IA sugiere Nivel II, profesional asigna Nivel III
- **Pasos:**
  1. Verificar que hay discrepancia
  2. No ingresar motivo
  3. Intentar cerrar
- **Resultado esperado:** Botón "Cerrar Evento" deshabilitado o error exigiendo motivo

---

## 4. Estrategia de Datos

| Recurso | Valor |
|---|---|
| URL base | `http://localhost:8501` |
| Usuario prueba | `enfermera_01` / `admin123` |
| Paciente prueba 1 | Doc=1234567890, FNac=1985-06-15, Sexo=M, Via=Particular |
| Paciente prueba 2 | Doc=9876543210, FNac=1990-03-22, Sexo=F, Via=Ambulancia |
| Signos normales | SpO₂=98, FR=16, FC=72, Temp=36.5, PA=120/80, Peso=70, Talla=170 |
| Signos críticos | SpO₂=88, FR=28, FC=102, Temp=38.5, PA=145/88 |
| BD prueba | `data/triaje.db` |

---

## 5. Requisitos de Evidencia

| Tipo | Coverage |
|---|---|
| Screenshots | Todos los casos críticos y alto (12/16) |
| Código fuente | Casos unitarios/de integración (4/16) |
| Video | No aplica (Streamlit WebSocket — ver nota) |

> **Nota sobre videos:** Streamlit usa WebSockets para comunicación cliente-servidor. Las herramientas
> de grabación tradicionales (Playwright) no pueden interactuar con widgets Streamlit
> (st.text_input, st.button, etc.) porque no son elementos HTML estándar sino componentes
> React renderizados vía WebSocket. Para videos futuros se recomienda `streamlit.testing` (v1.28+).

---

## 6. Criterios de Entrada/Salida

| Criterio | Condición |
|---|---|
| **Entrada** | App en `localhost:8501`, BD inicializada, usuario autenticado |
| **Salida GO** | 100% casos críticos pass, ≥ 80% total pass |
| **Salida NO-GO** | Algún caso crítico falla |
