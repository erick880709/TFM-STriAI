# 🎨 Mockups de Mejora UX/UI — React Frontend

**Herramienta:** Excalidraw MCP  
**Directorio:** `resources/diseno/imagenes/reactUx/`  
**Fecha:** 2026-07-21

---

## Mapeo de Mockups

| # | Checkpoint Excalidraw | Pantalla(s) | Descripción |
|---|----------------------|-------------|-------------|
| 1 | `3d61f04c060a45f1bf` | Dashboard | KPIs semánticos, DateRangePicker, sidebar colapsable, gráficos accesibles |
| 2 | `609834730eec4ec1ac` | Flujo Clínico (5 pantallas) | Stepper real con estados de BD, breadcrumb, autosave 30s, navegación bloqueada |
| 3 | `a5353436c8ae446999` | Layout Responsive | Desktop (256px) / Tablet (64px iconos) / Mobile (BottomNav), targets táctiles 44px |
| 4 | `d5beecaeabae414491` | Signos Vitales | Labels en español médico, rangos de referencia visibles, auto-save, mini-historial |
| 5 | `4844ad51bdc24610a1` | Login + Sidebar | autocomplete, Enter submit, link recuperación, sidebar colapsable, atajos teclado |

---

## Resumen de mejoras por componente

### 🔐 Login
- `autocomplete="username"` / `autocomplete="current-password"`
- Submit con tecla Enter en campo contraseña
- Link "¿Olvidaste tu contraseña?"
- Footer: "Hospital Universitario · Colombia"
- Validación de expiración JWT antes de mostrar UI

### 🧭 Sidebar
- Colapsable: botón ☰ en header → 64px solo iconos
- Transición CSS: `transition-all duration-200`
- Ítems sin permiso: mostrar deshabilitados con tooltip
- `aria-label="Navegación principal"`
- Badge de notificaciones

### 📱 Responsive
- Desktop (≥1024px): sidebar 256px + contenido 2-5 cols
- Tablet (768-1023px): sidebar 64px iconos, colapsable
- Mobile (<768px): BottomNav bar, 1 columna, cards full-width
- Targets táctiles: mínimo 44x44px (WCAG AAA)

### 🩺 Flujo Clínico
- Stepper real: lee `GET /api/triages/{id}/progress`
- 5 estados: ✅ completado / 🔵 actual / ⚪ pendiente / 🔒 bloqueado
- Breadcrumb en Header con ruta clickable
- Auto-save cada 30s a localStorage + sincronización con BD
- Navegación bloqueada a pasos no alcanzados (redirect)

### 💓 Signos Vitales
- Labels en español médico (no snake_case)
- Rangos de referencia visibles: "Normal: 60-100 lpm"
- Colores semánticos: 🟢 Normal / 🟡 Atención / 🔴 Crítico
- Indicador de auto-save: "💾 Guardado hace 5s"
- Tooltips clínicos en cada campo
- Mini-historial del paciente (últimos 3 registros)

### 📊 Dashboard
- DateRangePicker con presets (Hoy, 7d, 30d, Este mes)
- KPIs con códigos de color semánticos + benchmarks
- Gráficos con aria-label y tabla oculta (sr-only)
- Tasa Cierre: "N/A" si no hay datos (no 0% en rojo)
- Botón Exportar PDF

### ⌨️ Atajos de teclado
- Ctrl+P → Pacientes
- Ctrl+D → Dashboard
- Ctrl+K → Buscador global
- Escape → Cerrar modales

---

## Archivos en este directorio

| Archivo | Descripción |
|---------|-------------|
| `auditoria-usabilidad.md` | Informe completo de usabilidad con 10 hallazgos críticos |
| `mapeo-mockups.md` | Este archivo — índice de mockups |
