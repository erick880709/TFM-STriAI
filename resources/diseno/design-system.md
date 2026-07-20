# Design System — Sistema de Triaje Multimodal IA

**Ubicación:** `resources/diseno/` · **Versión:** 1.0 · **Fecha:** 2026-07-19

---

## Producto
Aplicación clínica de apoyo al triaje para servicios de urgencias colombianos.
- **Tipo:** Healthcare CDSS (Clinical Decision Support System)
- **Industria:** Salud / Hospitalario
- **Audiencia:** Profesionales sanitarios (médicos, enfermeras, administrativos)
- **Framework:** Streamlit (Python)

---

## Paleta de Colores (Healthcare App)

| Token | Hex | Uso |
|---|---|---|
| Primary | `#0891B2` | Botones principales, links, encabezados de sección |
| On Primary | `#FFFFFF` | Texto sobre primary |
| Secondary | `#22D3EE` | Elementos secundarios, badges, highlights |
| Accent | `#059669` | CTAs positivos, confirmación, checks |
| Background | `#ECFEFF` | Fondo general de la app |
| Foreground | `#164E63` | Texto principal |
| Card | `#FFFFFF` | Tarjetas, paneles |
| Card Foreground | `#164E63` | Texto en tarjetas |
| Muted | `#E8F1F6` | Fondos secundarios, filas alternas |
| Muted Foreground | `#64748B` | Texto secundario, placeholders |
| Border | `#A5F3FC` | Bordes de inputs, separadores |
| Destructive | `#DC2626` | Errores, alertas críticas, Nivel I |
| On Destructive | `#FFFFFF` | Texto sobre destructive |

### Colores semánticos para niveles de triaje

| Nivel | Color | Hex | Tiempo máx. atención |
|---|---|---|---|
| I — Resucitación | Rojo intenso | `#DC2626` | Inmediata |
| II — Emergencia | Naranja | `#EA580C` | ≤ 30 min |
| III — Urgencia | Amarillo ámbar | `#F59E0B` | 2-4 h |
| IV — Menor urgencia | Verde | `#059669` | 4-12 h |
| V — No urgencia | Azul grisáceo | `#64748B` | 12-24 h |

---

## Tipografía (Corporate Trust)

| Uso | Font | Weight | Size | Ejemplo |
|---|---|---|---|---|
| Títulos principales | Lexend | 600 | 28px | `Registro de Paciente` |
| Subtítulos de sección | Lexend | 500 | 20px | `Datos del Paciente` |
| Títulos de tarjeta | Lexend | 500 | 16px | `Signos Vitales` |
| Cuerpo | Source Sans 3 | 400 | 15px | Texto de formularios |
| Texto secundario | Source Sans 3 | 400 | 13px | Labels, placeholders |
| Datos / métricas | Lexend | 600 | 24px | `1,247` · `0.84` |

---

## Espaciado y Layout

| Propiedad | Valor |
|---|---|
| Grid | 12 columnas, gap 16px |
| Padding de página | 24px |
| Padding de tarjeta | 20px |
| Altura de input | 44px |
| Border radius (tarjetas) | 8px |
| Border radius (inputs, botones) | 6px |
| Sombras | `0 1px 3px rgba(0,0,0,0.08)` |

---

## Accesibilidad
- Contraste mínimo 4.5:1 (WCAG AA)
- Focus rings visibles: 3px `#0891B2`
- Targets táctiles ≥ 44px (entorno clínico con tablets)
- Navegación completa por teclado (Tab/Enter)
- Niveles de triaje usan color + icono + texto (no solo color)
