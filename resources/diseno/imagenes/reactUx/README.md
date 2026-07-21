# 🎨 Mockups Finales — STriAI Frontend v2.0

**App:** STriAI — Sistema de Triaje Multimodal IA  
**URL:** http://localhost:8000  
**Fecha:** 2026-07-21  
**Audiencia:** Personal médico (médicos, enfermeras, administrativos)  
**Contexto:** Servicio de Urgencias · Colombia

---

## 📸 Catálogo de Pantallas

| # | Pantalla | Ruta | Descripción |
|---|----------|------|-------------|
| 01 | Login | `/login` | Autenticación con credenciales, link de recuperación |
| 02 | Registro de Paciente | `/pacientes` | Paso 1 del flujo clínico, búsqueda de duplicados |
| 03 | Signos Vitales | `/signos-vitales` | Paso 2, layout 2 columnas con prioridad alta |
| 04 | Evaluación Clínica | `/evaluacion-clinica` | Paso 3, Glasgow, dolor, comorbilidades |
| 05 | Clasificación IA | `/clasificacion-ia` | Paso 4, predicción ML + explicación SHAP |
| 06 | Validación y Cierre | `/validacion` | Paso 5, clasificación profesional + cierre |
| 07 | Dashboard Operativo | `/dashboard` | KPIs, gráficos, desempeño IA, concordancia |
| 08 | Gestión de Modelos | `/modelos` | Registro, versionado y activación de modelos ML |
| 09 | Comparar Modelos | `/comparar-modelos` | Tabla comparativa de métricas entre versiones |
| 10 | Auditoría | `/auditoria` | Registro de acciones con filtros y exportación |
| 11 | Gestión de Usuarios | `/usuarios` | CRUD de usuarios, reseteo de contraseñas |
| 12 | Control de Cambios | `/control-cambios` | Historial de modificaciones sobre datos |
| 13 | Histórico del Paciente | `/historico` | Consulta de historial de triajes por documento |

---

## 🎨 Design System — "Cian Quirúrgico"

### Paleta

| Token | Hex | Uso |
|-------|-----|-----|
| `--color-scrub` | `#0A4C5C` | Sidebar, fondos oscuros |
| `--color-teal` | `#0891B2` | Acciones primarias, links, foco |
| `--color-ether` | `#22D3EE` | Acentos, badges |
| `--color-linen` | `#F0F9FA` | Fondo general |
| `--color-snow` | `#FFFFFF` | Tarjetas, superficie |
| `--color-ink` | `#0F3D47` | Texto principal |
| `--color-slate` | `#526771` | Texto secundario |
| `--color-coral` | `#E04A3A` | Destructivo, Nivel I |
| `--color-amber` | `#D97706` | Advertencia, Nivel III |
| `--color-moss` | `#059669` | Éxito, Nivel IV |

### Tipografía

| Rol | Familia | Peso | Tamaño |
|-----|---------|------|--------|
| Display | Lexend | 600 | 24-28px |
| Heading | Lexend | 500 | 16-20px |
| Body | Source Sans 3 | 400 | 15px |
| Data | JetBrains Mono | 500 | 14px |

### Layout

```
┌──────────────────────────────────────────────┐
│  HEADER: breadcrumb + user + hospital        │ 56px
├────────┬─────────────────────────────────────┤
│  NAV   │         CONTENIDO                   │
│  256px │   ┌──────────────────────────┐      │
│        │   │  Tarjeta / Tabla / Form  │      │
│        │   └──────────────────────────┘      │
└────────┴─────────────────────────────────────┘
```

### Responsive

| Breakpoint | Sidebar | Grid |
|------------|---------|------|
| ≥ 1024px | 256px expandido | 2-5 columnas |
| 768-1023px | 56px iconos | 2 columnas |
| < 768px | BottomNav | 1 columna |

### Elementos distintivos

- **Pasos numerados (1-5)** en sidebar para flujo clínico
- **Pulso Visual** animado en signos vitales fuera de rango
- **StepIndicator** con barra de progreso en páginas clínicas
- **Breadcrumb** semántico en header
- **BottomNav** con pasos para navegación móvil
