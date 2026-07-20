# Plan de Pruebas — Épica 1: Fundación del Sistema

**Versión:** 1.0 · **Fecha:** 2026-07-19 · **Proyecto:** TFM UNIR · **Sistema:** Triaje Multimodal IA
**Ejecutor:** QA Manual (Streamlit en navegador) · **Entorno:** `http://localhost:8501`

---

## 1. Objetivo

Verificar que los 8 ítems de la Épica 1 (Fundación del Sistema) cumplen sus criterios de aceptación:
- Autenticación segura con bloqueo por intentos
- Roles RBAC (5 niveles) con visibilidad condicional
- Recuperación de contraseña
- Cierre de sesión por inactividad
- Estructura del proyecto y base de datos funcionales

---

## 2. Alcance

### ✅ IN SCOPE
| ID | Tipo | Historia / Tarea | Prioridad |
|---|---|---|---|
| TT-E1-01 | TT | Inicializar proyecto con stack Python + Streamlit | Crítico |
| TT-E1-02 | TT | Configurar BD y modelo de dominio | Crítico |
| HU-E1-01 | HU | Login de usuarios con autenticación y bloqueo | Crítico |
| HU-E1-02 | HU | Gestión de roles y permisos RBAC | Crítico |
| HU-E1-03 | HU | Recuperación de contraseña | Alto |
| HU-E1-04 | HU | Cierre automático de sesión por inactividad | Alto |
| TT-E1-03 | TT | TLS/HTTPS y cifrado | Medio |
| TT-E1-04 | TT | Estructura modular del proyecto | Medio |

### ❌ OUT OF SCOPE
- Pruebas de carga/estrés
- Pruebas de seguridad avanzadas (pentesting)
- Épicas 2-6

---

## 3. Matriz de Escenarios

### TC-E1-01 [Crítico] — Login con credenciales válidas
- **Precondición:** BD inicializada, usuario `admin` existe
- **Pasos:**
  1. Navegar a `http://localhost:8501`
  2. Ingresar usuario `admin` y contraseña `admin123`
  3. Clic en "Iniciar Sesión"
- **Resultado esperado:** Mensaje "✅ Sesión iniciada", sidebar muestra rol Administrador
- **Datos:** `admin` / `admin123`

### TC-E1-02 [Crítico] — Login con credenciales inválidas
- **Precondición:** BD inicializada
- **Pasos:**
  1. Ingresar usuario `admin` y contraseña `wrongpassword`
  2. Clic en "Iniciar Sesión"
- **Resultado esperado:** Mensaje "Usuario o contraseña inválidos", NO se inicia sesión

### TC-E1-03 [Crítico] — Bloqueo por 5 intentos fallidos
- **Precondición:** Usuario `admin` no bloqueado
- **Pasos:**
  1. Intentar login con contraseña incorrecta 5 veces consecutivas
  2. Intentar login con contraseña correcta (`admin123`)
- **Resultado esperado:** Después del 5° intento, incluso la contraseña correcta es rechazada (cuenta bloqueada 15 min)

### TC-E1-04 [Crítico] — Sidebar con navegación según rol
- **Precondición:** Login exitoso como `admin`
- **Pasos:**
  1. Verificar sidebar muestra: Registrar Paciente, Signos Vitales, Evaluación Clínica, Clasificación IA, Dashboard, Gestión Modelos, Comparar Modelos, Auditoría, Gestión Usuarios
- **Resultado esperado:** Los 9 botones de navegación están visibles para Administrador

### TC-E1-05 [Alto] — Login como Enfermera (rol limitado)
- **Precondición:** BD inicializada
- **Pasos:**
  1. Login como `enfermera_01` / `admin123`
  2. Verificar sidebar
- **Resultado esperado:** Solo ve botones de flujo clínico (Registrar, Signos, Evaluación, Clasificación IA). NO ve Gestión Usuarios ni Dashboard.

### TC-E1-06 [Alto] — Recuperación de contraseña (flujo token)
- **Precondición:** Login page abierta
- **Pasos:**
  1. Clic en "¿Olvidó su contraseña?"
  2. Ingresar email `admin@triaje-ia.local`
  3. Solicitar token de recuperación
  4. Ingresar token y nueva contraseña `NewPass1`
- **Resultado esperado:** Token generado (30 min expiración), nueva contraseña cumple políticas (8+ chars, 1 mayús, 1 núm)

### TC-E1-07 [Alto] — Cierre de sesión manual
- **Precondición:** Sesión iniciada
- **Pasos:**
  1. Clic en "🚪 Cerrar Sesión" en sidebar
- **Resultado esperado:** Redirección a pantalla de login, sesión destruida

### TC-E1-08 [Medio] — Inicialización de BD (tablas creadas)
- **Precondición:** Archivo `triaje.db` no existe
- **Pasos:**
  1. Iniciar la app (`streamlit run app.py`)
  2. Verificar archivo `data/triaje.db` creado
- **Resultado esperado:** BD SQLite con 12 tablas, 5 usuarios demo

### TC-E1-09 [Medio] — Gestión de usuarios (crear nuevo)
- **Precondición:** Login como `admin`
- **Pasos:**
  1. Navegar a "👥 Gestión Usuarios"
  2. Crear usuario `test_user` con rol "Enfermera"
  3. Cerrar sesión y loguearse como `test_user`
- **Resultado esperado:** Usuario creado exitosamente, puede hacer login con el rol asignado

### TC-E1-10 [Medio] — Cambio de rol de usuario
- **Precondición:** Login como `admin`, usuario `enfermera_01` existe
- **Pasos:**
  1. En Gestión Usuarios, cambiar rol de `enfermera_01` a "Médico"
  2. Cerrar sesión y loguearse como `enfermera_01`
- **Resultado esperado:** Sidebar ahora muestra opciones de Médico (incluye Dashboard)

---

## 4. Estrategia de Datos

| Recurso | Valor |
|---|---|
| URL base | `http://localhost:8501` |
| Usuario admin | `admin` / `admin123` |
| Usuario enfermera | `enfermera_01` / `admin123` |
| Usuario médico | `medico_01` / `admin123` |
| BD de prueba | `data/triaje.db` (se recrea automáticamente) |

---

## 5. Requisitos de Evidencia

Por cada caso ejecutado se capturará:
- ✅ Screenshot del resultado (estado final de la pantalla)
- ✅ Estado Pass/Fail documentado
- ⚠️ Video (no aplica para Streamlit sin Playwright — se documenta con screenshots secuenciales)

---

## 6. Criterios de Entrada y Salida

| Criterio | Condición |
|---|---|
| **Entrada** | App desplegada en `localhost:8501`, BD inicializada |
| **Salida (GO)** | 100% casos críticos pass, ≥ 80% casos totales pass |
| **Salida (NO-GO)** | Algún caso crítico falla |
