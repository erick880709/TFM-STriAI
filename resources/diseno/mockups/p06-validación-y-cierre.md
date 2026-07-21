# p06 — Validación y Cierre

**Ruta Streamlit:** http://localhost:8501  
**Ruta React:** http://localhost:8000  

## Descripción

Paso 5. Clasificación profesional, concordancia IA vs profesional, cierre del triaje.

## Layout

Ver mockups.html para el diseño visual completo.

## Dimensiones

| Elemento | Valor |
|----------|-------|
| Sidebar | 256px (Desktop), 64px (Tablet), BottomNav (Mobile) |
| Header | 56px con breadcrumb |
| Contenido | max-width 1440px, centrado |
| Inputs | 38px alto, border-radius 6px, bg #F8FAFC |
| Cards | bg white, border 1px solid #A5F3FC, padding 16px |
| Labels | 12px, Source Sans 3, 500 |
| Body text | 13px, Source Sans 3, 400 |
| Headings | 18px, Lexend, 600 |

## Estados

- **Default:** Pantalla con datos cargados
- **Empty:** Sin datos disponibles
- **Loading:** Spinner durante carga
- **Error:** Mensaje de error con opción de reintentar

## Design Tokens

| Token | Hex |
|-------|-----|
| Primary | #0891B2 |
| Accent | #059669 |
| Background | #ECFEFF |
| Text | #164E63 |
| Muted | #64748B |
| Border | #A5F3FC |
| Destructive | #DC2626 |
