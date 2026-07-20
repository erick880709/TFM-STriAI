# Handoff — Mockups Sistema de Triaje Multimodal IA

**Fecha:** 2026-07-19
**Skill:** figma-prd-mockups
**Insumos:** janus (30 archivos RF/RNF/RT/RD) + specter (36 HU/TT)

---

## Herramienta utilizada

**Excalidraw MCP** (Path B — Figma MCP no conectado en esta sesión).

Se generaron **12 vistas Excalidraw**, una por pantalla, con el sistema de diseño Healthcare App + Corporate Trust aplicado.

---

## Screen → Checkpoint Mapping

| # | Pantalla | Checkpoint ID |
|---|---|---|
| 1 | Login | `b4eedc99c5784bae9e` |
| 2 | Registro de Paciente | `77e0a5983363417ebb` |
| 3 | Captura de Signos Vitales | `caa3c5e1e02946be8f` |
| 4 | Evaluación Clínica | `81b8340f461343cea9` |
| 5 | Clasificación IA + Validación | `e6a776c79d6042e9b8` |
| 6 | Explicación SHAP Detallada | `4ef872d21a8a446b95` |
| 7 | Validación de Triaje (Cierre) | `c9f9b6dea3f141b8af` |
| 8 | Comparación de Modelos | `94a2ab14e23e420fa2` |
| 9 | Gestión de Modelos | `d00e334a7f3f4a7181` |
| 10 | Dashboard Operativo | `13609941ff5e454a82` |
| 11 | Auditoría | `fa1f74713a454758a7` |
| 12 | Registro de Triaje (PDF) | `009d205c20d04fd5aa` |

---

## Design System

**Archivo:** `.github/resources/diseno/design-system.md`

| Token | Valor |
|---|---|
| Estilo | Flat Design + Accessible & Ethical |
| Paleta | Healthcare App: Primary `#0891B2` (cyan), Accent `#059669` (green) |
| Tipografía | Corporate Trust: Lexend (headings) + Source Sans 3 (body) |
| Colores triaje | I: `#DC2626`, II: `#EA580C`, III: `#F59E0B`, IV: `#059669`, V: `#64748B` |
| Framework | Streamlit (Python) |

---

## Artefactos guardados

| Archivo | Descripción |
|---|---|
| `.github/resources/diseno/inventario-pantallas.md` | Inventario completo de 12 pantallas con checkpoints |
| `.github/resources/diseno/design-system.md` | Sistema de diseño (paleta, tipografía, espaciado, colores de triaje) |
| `.github/resources/diseno/handoff-mockups.md` | Este archivo — entrada única para downstream skills |

---

## Deferred / Pendientes

- **Figma:** No se generó archivo Figma (MCP no conectado). Si se conecta en el futuro, regenerar los mockups en Figma para obtener click-through prototype y mejor fidelidad visual.
- **Estados de error:** Diseñados los estados principales (crítico, error, vacío, carga). Estados edge (timeout de red, BD caída) se mencionan en las HU pero no tienen mockup dedicado.
- **Responsive:** Los mockups son desktop-first (1440px aprox). El diseño responsivo para tablet (estaciones de enfermería) se infiere de la estructura de formularios pero no tiene mockup separado.
- **Animaciones:** No representables en Excalidraw. Las transiciones entre pantallas y microinteracciones (spinner de carga, hover states) están documentadas en las HU pero no en los wireframes.

---

## Para el Builder / Genesis

Antes de generar código, leer:
1. `.github/resources/diseno/inventario-pantallas.md` — qué pantallas construir y en qué orden
2. `.github/resources/diseno/design-system.md` — paleta, tipografía, colores de triaje
3. `resources/functional/hu/` — 36 HU+TT con criterios de aceptación detallados
4. `resources/functional/reqs/` — 6 épicas con alcance y prioridades

**Orden de implementación recomendado:** Pantallas 1→7 (flujo clínico), luego 10→9→8→11→12 (soporte).
