# Manual de Usuario — STriAI (Sistema de Triaje Multimodal IA)

**Versión:** 1.0 Demo  
**TFM — Máster en Inteligencia Artificial — UNIR**  
**Contexto:** Servicio de Urgencias · Colombia · Resolución 5596/2015

---

## 1. Introducción

STriAI es un sistema de apoyo a la decisión clínica para triaje de urgencias en hospitales colombianos. Utiliza inteligencia artificial multimodal (datos estructurados + texto clínico) para sugerir el nivel de urgencia (I a V) según la Resolución 5596/2015, asistiendo al profesional de la salud sin reemplazar su criterio.

### 1.1 Credenciales de Acceso

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `enfermera_01` | `admin123` | Enfermera |
| `medico_01` | `admin123` | Médico |
| `investigador_01` | `admin123` | Investigador |
| `auditor_01` | `admin123` | Auditor |

> **Importante:** Cambiar las contraseñas en producción. En entorno demo, todos usan `admin123`.

---

## 2. Roles y Permisos

### 2.1 Tabla de Permisos

| Funcionalidad | Administrador | Médico | Enfermera | Investigador | Auditor |
|---|---|---|---|---|---|
| Registrar Paciente | ✅ | ✅ | ✅ | ❌ | ❌ |
| Signos Vitales | ✅ | ✅ | ✅ | ❌ | ❌ |
| Evaluación Clínica | ✅ | ✅ | ✅ | ❌ | ❌ |
| Clasificación IA | ✅ | ✅ | ✅ | ❌ | ❌ |
| Validación y Cierre | ✅ | ✅ | ✅ | ❌ | ❌ |
| Dashboard | ✅ | ✅ | ❌ | ✅ | ✅ |
| Gestión Modelos | ✅ | ❌ | ❌ | ❌ | ❌ |
| Comparar Modelos | ✅ | ❌ | ❌ | ✅ | ❌ |
| Auditoría | ✅ | ❌ | ❌ | ❌ | ✅ |
| Gestión Usuarios | ✅ | ❌ | ❌ | ❌ | ❌ |
| Control de Cambios | ✅ | ❌ | ❌ | ❌ | ❌ |
| Histórico del Paciente | ✅ | ✅ | ✅ | ✅ | ✅ |

### 2.2 Descripción de Roles

- **Administrador:** Acceso total. Gestiona usuarios, modelos IA, auditoría y control de cambios. También puede ejecutar el flujo clínico completo.
- **Médico:** Flujo clínico completo + Dashboard. Responsable de validar y cerrar triajes, revisar concordancia con la IA.
- **Enfermera:** Flujo clínico completo. Registra pacientes, captura signos vitales, realiza evaluación clínica y consulta clasificación IA.
- **Investigador:** Dashboard + Comparación de Modelos. Analiza métricas de rendimiento de los modelos IA.
- **Auditor:** Auditoría + Dashboard + Histórico. Revisa trazabilidad de cambios y consulta históricos.

---

## 3. Flujo de Trabajo Clínico (Paso a Paso)

El flujo clínico completo sigue 7 pasos secuenciales. Cada paso debe completarse antes de avanzar al siguiente.

### 🔄 Orden Correcto de Funcionamiento

```
Paso 1: Registrar Paciente → Paso 2: Signos Vitales → Paso 3: Evaluación Clínica
→ Paso 4: Clasificación IA → Paso 5: Validación → Paso 6: Cierre
```

---

### 3.1 Paso 1 — 📝 Registrar Paciente

**Roles:** Administrador, Médico, Enfermera  
**Objetivo:** Registrar un nuevo paciente o buscar uno existente para iniciar un triaje.

#### Acciones:
1. Haga clic en **📝 Registrar Paciente** en el menú lateral.
2. En la pestaña **🆕 Nuevo Paciente**, complete el formulario en 5 secciones:
   - **Datos Personales:** Tipo y número de documento, nombres, apellidos, fecha de nacimiento, sexo.
   - **Contacto:** Teléfono, correo electrónico.
   - **Contacto de Emergencia:** Nombre y teléfono del contacto.
   - **Residencia:** Seleccione Departamento → Ciudad (dropdown dependiente), dirección.
   - **Datos Clínicos:** Vía de llegada, régimen de salud, EPS, episodios previos.
3. Haga clic en **Registrar Paciente y Crear Triaje**.
4. Si el paciente ya existe, el sistema lo detecta y permite usar el registro existente.
5. Se crea automáticamente un evento de triaje en estado "Registrado".
6. El sistema redirige automáticamente a **Signos Vitales**.

**⚠️ Bloqueo de Triaje Activo:** Si el paciente ya tiene un triaje en curso (no cerrado ni cancelado), el sistema bloquea la creación de uno nuevo hasta que se cierre el anterior.

#### Ejemplo:
```
Tipo Documento: CC
Número: 1234567890
Nombres: María Elena
Apellidos: Gómez Restrepo
Fecha Nacimiento: 1985-03-15
Sexo: F
Teléfono: 3101234567
Correo: maria.gomez@correo.com
Contacto Emergencia: Carlos Gómez (esposo)
Teléfono Contacto: 3119876543
Departamento: Antioquia
Ciudad: Medellín
Dirección: Calle 100 # 15-20, Barrio El Poblado
Vía de Llegada: Particular
Régimen de Salud: Contributivo
EPS: Sura
Episodios Previos: 2
```

---

### 3.2 Paso 2 — 💓 Captura de Signos Vitales

**Roles:** Administrador, Médico, Enfermera  
**Objetivo:** Registrar los 8 signos vitales del paciente.

#### Acciones:
1. Verifique el paciente en la cabecera (nombre, documento, edad, sexo, vía de llegada).
2. Complete los signos de prioridad alta (mayor peso predictivo):
   - **Saturación de Oxígeno (SpO₂):** 0–100%. Crítico si < 90%.
   - **Frecuencia Respiratoria:** respiraciones/minuto. Crítico si > 25.
3. Complete los signos complementarios:
   - **Temperatura:** °C (30–45).
   - **Frecuencia Cardíaca:** latidos/minuto.
   - **Presión Sistólica / Diastólica:** mmHg.
   - **Peso:** kg.
   - **Talla:** cm. El IMC se calcula automáticamente.
4. Haga clic en **💾 Guardar Signos Vitales**.
5. El sistema muestra alertas para valores fuera de rango.
6. Navegue manualmente a **🩺 Evaluación Clínica** desde el menú lateral.

#### Ejemplo:
```
SpO₂: 95%
Frecuencia Respiratoria: 18
Temperatura: 37.2°C
Frecuencia Cardíaca: 88
Presión Sistólica: 120
Presión Diastólica: 80
Peso: 65 kg
Talla: 160 cm → IMC calculado: 25.4
```

---

### 3.3 Paso 3 — 🩺 Evaluación Clínica

**Roles:** Administrador, Médico, Enfermera  
**Objetivo:** Registrar la evaluación clínica del paciente (motivo de consulta, antecedentes, escala de dolor).

#### Acciones:
1. Verifique el resumen de signos vitales en la cabecera.
2. Complete los campos requeridos:
   - **Motivo de Consulta:** Seleccione categoría (Dolor torácico, Trauma, Disnea, etc.).
   - **Descripción:** Texto libre del motivo (opcional).
   - **Escala de Dolor:** 0 (sin dolor) a 10 (máximo dolor).
   - **Glasgow:** 3–15 (nivel de conciencia).
   - **Nivel de Conciencia:** Alerta, Somnoliento, Obnubilado, Inconsciente.
3. Marque antecedentes relevantes:
   - Diabetes, Hipertensión, Enfermedad Renal, Embarazo, Cáncer, Cardiopatías, Enfermedad Pulmonar, Cirugías Recientes.
4. Complete campos adicionales:
   - **Medicación Relevante:** medicamentos actuales.
   - **Alergias:** alergias conocidas.
   - **Observaciones:** notas clínicas adicionales.
5. Haga clic en **💾 Guardar Evaluación Clínica**.
6. El sistema cambia el estado del triaje a "PendienteIA" automáticamente.
7. Navegue manualmente a **🧠 Clasificación IA**.

#### Ejemplo:
```
Motivo de Consulta: Dolor abdominal
Escala de Dolor: 6
Glasgow: 15
Nivel de Conciencia: Alerta
Antecedentes: Diabetes=Sí, Hipertensión=No
Medicación: Metformina 850mg
Alergias: Penicilina
```

---

### 3.4 Paso 4 — 🧠 Clasificación IA

**Roles:** Administrador, Médico, Enfermera  
**Objetivo:** Ejecutar el modelo de IA para obtener una sugerencia de nivel de triaje con explicabilidad.

#### Acciones:
1. Verifique el estado del triaje (debe estar en "PendienteIA").
2. Haga clic en **🚀 Ejecutar Clasificación IA**.
3. El sistema:
   - Carga el modelo multimodal (XGBoost + BERT-es).
   - Construye el vector de características con signos vitales + evaluación clínica.
   - Muestra el **Nivel de Triaje Sugerido por IA** (I, II, III, IV, V) con código de colores.
   - Muestra las **probabilidades** para cada nivel.
   - Genera el **gráfico SHAP** (explicabilidad): las variables que más influyeron en la predicción.
4. Revise la explicación clínica (SHAP) para entender la decisión de la IA.
5. El profesional debe registrar su **propia clasificación** (Nivel I–V).
6. Haga clic en **✅ Confirmar Clasificación**.
7. El sistema calcula automáticamente la **concordancia** entre IA y profesional.
8. El estado cambia a "Clasificado".

> **Modo Degradado:** Si el modelo no está disponible, el sistema muestra un aviso y permite continuar solo con la clasificación del profesional.

#### Ejemplo:
```
Nivel Sugerido IA: III — Urgencia (30-60 min)
Probabilidades: I: 5% | II: 15% | III: 55% | IV: 20% | V: 5%
Top variables SHAP: Escala Dolor, SpO₂, Edad, Frecuencia Cardíaca
Nivel Asignado Profesional: III
Concordancia: ✅ Sí
```

---

### 3.5 Paso 5 — ✅ Validación y Cierre

**Roles:** Administrador, Médico, Enfermera  
**Objetivo:** Revisar el triaje completo y cerrarlo formalmente.

#### Acciones:
1. Revise el resumen completo del triaje (signos vitales, evaluación, clasificación IA vs profesional).
2. Si hay discrepancia entre IA y profesional, registre el **motivo**.
3. Verifique que todos los datos sean correctos.
4. Haga clic en **🔒 Cerrar Triaje**.
5. Si necesita corregir algo, use **🔄 Reclasificar** para volver al paso de clasificación.
6. El estado cambia a "Cerrado" (estado terminal).
7. El paciente queda liberado para un nuevo triaje en el futuro.

#### Máquina de Estados del Triaje:
```
Registrado → EnEvaluación → PendienteIA → Clasificado → Validado → Cerrado
                                                           ↘ Cancelado (reactivable)
```

---

## 4. Funcionalidades de Soporte

### 4.1 📊 Dashboard

**Roles:** Administrador, Médico, Investigador, Auditor  
**Descripción:** Panel de control con indicadores clave del servicio de urgencias.

#### Acciones:
- Visualice **7 KPIs**: Total de triajes, distribución por niveles, concordancia IA-Profesional, tiempo promedio de atención.
- Gráfico de **distribución de triajes** por nivel (barras).
- **Tendencia de 7 días**: evolución de atenciones.
- **Semáforo de metas**: cumplimiento de objetivos (ej. concordancia > 85%).
- **Exportación**: CSV, Excel, JSON.

---

### 4.2 ⚙️ Gestión de Modelos

**Roles:** Administrador  
**Descripción:** Administración de los modelos de IA del sistema.

#### Acciones:
- **Pestaña Disco:** Explore modelos guardados en el sistema de archivos.
- **Pestaña BD:** Consulte modelos registrados en la base de datos.
- **Activar/Desactivar modelos:** Cambie el modelo activo para inferencia.
- **Rollback:** Restaure un modelo anterior si el nuevo tiene bajo rendimiento.
- Visualice métricas: F1-Score, Precisión, Recall, AUC-ROC, AUPRC.

---

### 4.3 🔬 Comparar Modelos

**Roles:** Administrador, Investigador  
**Descripción:** Comparación lado a lado de dos modelos de IA.

#### Acciones:
- Seleccione **Modelo A** y **Modelo B**.
- Compare métricas en tabla: F1, Precisión, Recall, AUC-ROC.
- Gráfico de barras comparativo.
- Identifique el modelo ganador para activación.

---

### 4.4 🔍 Auditoría

**Roles:** Administrador, Auditor  
**Descripción:** Registro de acciones del sistema (trazabilidad).

#### Acciones:
- Filtre por: Usuario, Acción, Entidad, Rango de fechas, Documento de paciente.
- Visualice tabla con: Fecha/Hora, Usuario, Acción, Entidad, Detalles.
- **Exportación**: CSV, Excel, JSON.
- **Reporte de triaje**: Genere documento descargable con todos los datos de un triaje específico.

---

### 4.5 👥 Gestión de Usuarios

**Roles:** Administrador  
**Descripción:** Administración de cuentas del sistema.

#### Acciones:
- **Lista de Usuarios:** Tabla con nombre, email, rol, estado (activo/inactivo), último acceso.
- **Nuevo Usuario:** Formulario con nombre, email, contraseña, rol (Enfermera/Médico/Investigador/Auditor).
- **Editar Usuario:** Modifique email, rol, active/desactive cuenta.
- **Restablecer Contraseña:** Genere contraseña temporal de 8 caracteres.
- **Validaciones:** No permite crear Admins, no permite editarse a sí mismo, contraseña mín. 6 caracteres.

---

### 4.6 📝 Control de Cambios

**Roles:** Administrador  
**Descripción:** Auditoría de modificaciones a entidades clínicas (Paciente, EventoTriaje, SignosVitales).

#### Acciones:
- Filtre por: Entidad, Usuario, Documento de paciente.
- Visualice: Fecha/Hora, Usuario, Entidad, Campo modificado, Valor anterior → Valor nuevo, Documento paciente.
- **Exportación** a CSV.

---

### 4.7 📜 Histórico del Paciente

**Roles:** Todos los roles  
**Descripción:** Consulta del historial completo de visitas a urgencias de un paciente.

#### Acciones:
1. Ingrese el número de documento del paciente.
2. Haga clic en **🔍 Buscar Historial**.
3. Visualice datos del paciente: nombre, documento, edad, sexo, total de visitas.
4. Tabla con todas las visitas:
   - Fecha / Hora de ingreso
   - Motivo de asistencia
   - Nivel de urgencia asignado por el profesional
   - Nivel de urgencia sugerido por la IA
   - Estado del triaje
5. **Exportación** a CSV.

---

## 5. Carga y Comparación de Modelos IA  ⚙️🔬

> **Rol requerido:** Administrador (carga y gestión) / Investigador (comparación).  
> Los modelos de IA son el núcleo predictivo del sistema. Esta sección explica cómo cargar, activar y comparar modelos.

---

### 5.1 ¿Qué es un modelo en STriAI?

Un modelo es un artefacto serializado que contiene:
- **Algoritmo de ML:** XGBoost con Early Fusion o Late Fusion.
- **Transformadores:** Scaler (StandardScaler), Encoder (OneHotEncoder), Tokenizer NLP (BERT-es).
- **Umbrales de decisión:** Calibrados por clase para optimizar F1.
- **Metadatos:** Versión, fecha de entrenamiento, métricas (F1, Precisión, Recall, AUC-ROC, AUPRC).

Cada modelo se guarda en `sistema-triaje-ia/models/` con una carpeta dedicada que incluye:
```
models/
└── xgboost_early_fusion_v1/
    ├── metadata.json        ← Versión, métricas, fecha, arquitectura
    ├── model.pkl             ← Modelo XGBoost serializado
    ├── scaler.pkl            ← StandardScaler
    ├── encoder.pkl           ← OneHotEncoder
    └── tokenizer/            ← Tokenizer BERT-es
```

---

### 5.2 ⚙️ Carga y Gestión de Modelos (Administrador)

#### Paso a Paso — Activar un Modelo

1. En el menú lateral, haga clic en **⚙️ Gestión Modelos** (sección 📊 Soporte).
2. La pantalla tiene **3 pestañas**:

| Pestaña | Función |
|---|---|
| **💾 Disco** | Explora los modelos guardados en el sistema de archivos (`models/`). Muestra carpetas disponibles. |
| **🗄️ BD** | Consulta los modelos registrados en la base de datos SQLite (tabla `Modelo`). |
| **📋 Registro** | Registra un nuevo modelo encontrado en disco dentro de la base de datos para que el sistema lo reconozca. |

3. **Pestaña Disco:**
   - Seleccione un directorio de modelo de la lista.
   - Vea los archivos contenidos (`model.pkl`, `scaler.pkl`, `encoder.pkl`, `tokenizer/`, `metadata.json`).
   - Si el modelo no está registrado en la BD, use **Registrar en BD**.

4. **Pestaña BD:**
   - Observe la tabla de modelos con columnas: Nombre, Versión, Arquitectura, Algoritmo, F1-Score, Precisión, Recall, AUC-ROC, Estado.
   - Estados posibles:
     - 🟢 **Activo:** Es el modelo que se usa para inferencia en el flujo clínico.
     - 🟡 **EnValidación:** Modelo registrado pero no activo (requiere pruebas).
     - ⚫ **Inactivo:** Modelo descartado o legacy.
   - Para **activar** un modelo, haga clic en el botón correspondiente.
   - Para **desactivar** (rollback), active otro modelo — solo puede haber uno activo a la vez.

5. **Pestaña Registro:**
   - Ingrese manualmente los metadatos del modelo (nombre, versión, arquitectura, algoritmo, hiperparámetros, métricas).
   - Útil cuando el modelo fue entrenado offline con `run_pipeline.py` y necesita ser registrado.

#### Ejemplo — Activar un modelo recién entrenado
```
1. Entrenó un nuevo modelo: xgboost_late_fusion_v2
2. La carpeta aparece en models/ con metadata.json:
   {
     "model_name": "xgboost_late_fusion_v2",
     "architecture": "Late Fusion",
     "algorithm": "XGBoost",
     "f1_score": 0.87,
     "precision": 0.86,
     "recall": 0.88,
     "auc_roc": 0.94,
     "auprc": 0.81
   }
3. Vaya a ⚙️ Gestión Modelos → Pestaña Disco
4. Seleccione "xgboost_late_fusion_v2" → Haga clic en "Registrar en BD"
5. Vaya a Pestaña BD → El modelo aparece con Estado "EnValidación"
6. Revise las métricas. Si F1 > modelo actual (0.85), active este.
7. Haga clic en "Activar" → El Estado cambia a "Activo"
8. El modelo anterior pasa automáticamente a "Inactivo" (rollback seguro)
9. ¡Listo! El flujo clínico ahora usa xgboost_late_fusion_v2 para inferencia.
```

---

### 5.3 🔬 Comparación de Modelos (Administrador e Investigador)

#### Objetivo
Comparar dos modelos lado a lado usando métricas estándar de clasificación para decidir cuál desplegar.

#### Paso a Paso — Comparar dos Modelos

1. En el menú lateral, haga clic en **🔬 Comparar Modelos** (sección 📊 Soporte).
2. La pantalla muestra dos selectores desplegables:
   - **Modelo A:** Seleccione el primer modelo.
   - **Modelo B:** Seleccione el segundo modelo.
3. Al seleccionar ambos, el sistema muestra automáticamente:

**a) Tabla Comparativa de Métricas**
| Métrica | Modelo A | Modelo B | Ganador |
|---|---|---|---|
| F1-Score (macro) | 0.85 | 0.87 | 🏆 B |
| Precisión (macro) | 0.84 | 0.86 | 🏆 B |
| Recall (macro) | 0.86 | 0.88 | 🏆 B |
| AUC-ROC (macro) | 0.93 | 0.94 | 🏆 B |
| AUPRC (macro) | 0.79 | 0.81 | 🏆 B |

**b) Gráfico de Barras Comparativo**
- Barras agrupadas por métrica.
- Colores: Azul (Modelo A), Naranja (Modelo B).
- Diferencia porcentual anotada sobre cada par de barras.

**c) Metadatos de Cada Modelo**
- Nombre, versión, arquitectura, algoritmo.
- Fecha de serialización.
- Hiperparámetros (si disponibles en metadata.json).

#### Interpretación de Resultados

- **F1-Score:** Balance entre precisión y recall. Ideal para datasets desbalanceados (triaje tiene más niveles III/IV que I/II). **Meta del sistema: > 0.80.**
- **AUC-ROC:** Capacidad de discriminar entre clases. > 0.90 es excelente.
- **AUPRC:** Más informativo que AUC-ROC en datos desbalanceados. Enfoque en clases minoritarias (I, II).
- **Precisión por clase:** Revise si el modelo identifica correctamente los niveles críticos (I y II).

#### Criterios de Decisión

| Escenario | Acción recomendada |
|---|---|
| Modelo B supera a A en TODAS las métricas | Active el Modelo B inmediatamente (⚙️ Gestión Modelos → Activar) |
| Modelo B gana en F1 y AUC-ROC pero pierde en precisión | Si la prioridad es no sub-triajar (no clasificar como menos urgente), prefiera mayor recall |
| Modelo B tiene mejor AUPRC | Señal de mejor manejo de clases minoritarias (niveles I/II) — recomendado activar |
| Empate técnico | Consulte el gráfico SHAP de cada modelo y las curvas de calibración antes de decidir |

#### Ejemplo Completo — Flujo de Decisión
```
Situación: Modelo actual = xgboost_early_fusion_v1 (F1=0.83)
         Modelo candidato = xgboost_late_fusion_v2 (F1=0.87)

1. 🔬 Comparar Modelos → Seleccione A=early_fusion_v1, B=late_fusion_v2
2. Resultados:
   - F1: 0.83 vs 0.87 → B gana (+4.8%)
   - AUC-ROC: 0.92 vs 0.94 → B gana (+2.2%)
   - AUPRC: 0.77 vs 0.81 → B gana (+5.2%)
   - Recall nivel I: 0.91 vs 0.93 → B gana (mejor detección de críticos)
3. Conclusión: B es superior en todas las métricas.
4. Acción: ⚙️ Gestión Modelos → Activar late_fusion_v2.
5. Verificación: Ejecute algunos triajes de prueba y revise concordancia en Dashboard.
```

---

## 6. Estados del Triaje

| Estado | Descripción | ¿Permite nuevo triaje? |
|---|---|---|
| Registrado | Paciente registrado, triaje creado | ❌ Bloquea |
| EnEvaluación | Signos vitales o evaluación clínica en curso | ❌ Bloquea |
| PendienteIA | Evaluación completada, esperando clasificación IA | ❌ Bloquea |
| Clasificado | IA y profesional clasificaron, esperando validación | ❌ Bloquea |
| Validado | Triaje validado, esperando cierre | ❌ Bloquea |
| Cerrado | Triaje finalizado (terminal) | ✅ Libera |
| Cancelado | Triaje anulado (reactivable) | ✅ Libera |

---

## 7. Niveles de Triaje (Resolución 5596/2015)

| Nivel | Nombre | Tiempo de Atención | Color |
|---|---|---|---|
| I | Atención Inmediata | Inmediato | 🔴 Rojo |
| II | Emergencia | < 30 minutos | 🟠 Naranja |
| III | Urgencia | 30–60 minutos | 🟡 Amarillo |
| IV | Urgencia Menor | 1–2 horas | 🟢 Verde |
| V | Consulta General | > 2 horas | 🔵 Azul |

---

## 8. Resolución de Problemas Comunes

### 7.1 "Usuario o contraseña inválidos"
- Verifique que el usuario y contraseña sean correctos (ver sección 1.1).
- Si la cuenta fue bloqueada por intentos fallidos, espere 15 minutos o contacte al Administrador.

### 7.2 "Este paciente ya tiene un triaje en curso"
- El paciente tiene un triaje activo (no cerrado ni cancelado).
- Cierre o cancele el triaje activo antes de crear uno nuevo.
- Use **📜 Histórico del Paciente** para localizar el triaje activo.

### 7.3 "Modelo no disponible" (Modo Degradado)
- El modelo IA no está cargado en el sistema.
- Puede continuar con la clasificación manual del profesional.
- Contacte al Administrador para activar un modelo.

### 7.4 Sesión expirada
- Por inactividad (> 15 minutos), la sesión se cierra automáticamente.
- Vuelva a iniciar sesión.

---

## 9. Notas Técnicas

- **Plataforma:** Streamlit 1.59+ (Python 3.11).
- **Base de datos:** SQLite local (11 tablas).
- **Modelo IA:** XGBoost Early/Late Fusion + embeddings BERT-es para texto clínico.
- **Seguridad:** bcrypt para contraseñas, SQLite WAL mode, sin eliminación física de registros (soft delete).
- **Explicabilidad:** SHAP (SHapley Additive exPlanations) con etiquetas en español.

---

**TFM · UNIR · Máster en Inteligencia Artificial · v1.0 Demo**
