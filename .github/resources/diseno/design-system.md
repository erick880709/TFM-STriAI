# Design System — Sistema de Triaje Multimodal IA

## Producto
Aplicación clínica de apoyo al triaje para servicios de urgencias colombianos.
- Tipo: Healthcare CDSS (Clinical Decision Support System)
- Industria: Salud / Hospitalario
- Audiencia: Profesionales sanitarios (médicos, enfermeras, administrativos)

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
| Nivel | Color | Hex |
|---|---|---|
| I — Resucitación | Rojo intenso | `#DC2626` |
| II — Emergencia | Naranja | `#EA580C` |
| III — Urgencia | Amarillo/ámbar | `#F59E0B` |
| IV — Menor urgencia | Verde | `#059669` |
| V — No urgencia | Azul grisáceo | `#64748B` |

## Tipografía (Corporate Trust)

| Uso | Font | Weight | Size |
|---|---|---|---|
| Títulos principales | Lexend | 600 | 28px |
| Subtítulos de sección | Lexend | 500 | 20px |
| Títulos de tarjeta | Lexend | 500 | 16px |
| Cuerpo | Source Sans 3 | 400 | 15px |
| Texto secundario / labels | Source Sans 3 | 400 | 13px |
| Datos / métricas | Lexend | 600 | 24px |

## Espaciado y Layout
- Grid: 12 columnas, gap 16px
- Padding de página: 24px
- Padding de tarjeta: 20px
- Altura de input: 44px
- Border radius: 8px (tarjetas), 6px (inputs, botones)
- Sombras: sutiles (0 1px 3px rgba(0,0,0,0.08))

## Framework
Streamlit (Python) — diseño responsivo fluido, sidebar para navegación.

## Accesibilidad
- Contraste mínimo 4.5:1 (WCAG AA)
- Focus rings visibles (3px #0891B2)
- Targets táctiles ≥ 44px
- Soporte para teclado (Tab/Enter)
- No depender solo del color (iconos + texto para niveles de triaje)
