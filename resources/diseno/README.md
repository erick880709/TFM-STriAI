# 📐 Recursos de Diseño — Sistema de Triaje Multimodal IA

**Versión:** 1.0 · **Fecha:** 2026-07-19 · **Proyecto:** TFM UNIR

---

## Estructura de `resources/diseno/`

```
resources/diseno/
├── README.md                    ← Este archivo
├── design-system.md             ← Paleta, tipografía, espaciado, colores triaje
├── mockups/                     ← Documentación detallada por pantalla
│   ├── p01-login.md
│   ├── p02-registro-paciente.md
│   ├── p03-signos-vitales.md
│   ├── p04-evaluacion-clinica.md
│   ├── p05-clasificacion-ia.md
│   ├── p06-explicacion-shap.md
│   ├── p07-validacion-triaje.md
│   ├── p08-comparacion-modelos.md
│   ├── p09-gestion-modelos.md
│   ├── p10-dashboard-operativo.md
│   ├── p11-auditoria.md
│   └── p12-registro-triaje-pdf.md
└── imagenes/                    ← Capturas de cada mockup
    ├── p01-login.png
    ├── p02-registro-paciente.png
    ├── ...
    └── p12-registro-triaje-pdf.png
```

---

## Índice de Pantallas

### Flujo Clínico Principal (1-7)

| # | Pantalla | Doc | Checkpoint | Rol |
|---|---|---|---|---|
| 1 | Login | [p01](mockups/p01-login.md) | `b4eedc99` | Todos |
| 2 | Registro de Paciente | [p02](mockups/p02-registro-paciente.md) | `77e0a598` | Administrativo |
| 3 | Captura de Signos Vitales | [p03](mockups/p03-signos-vitales.md) | `caa3c5e1` | Enfermera |
| 4 | Evaluación Clínica | [p04](mockups/p04-evaluacion-clinica.md) | `81b8340f` | Enfermera / Médico |
| 5 | Clasificación IA | [p05](mockups/p05-clasificacion-ia.md) | `e6a776c7` | Médico / Enfermera |
| 6 | Explicación SHAP | [p06](mockups/p06-explicacion-shap.md) | `4ef872d2` | Médico |
| 7 | Validación de Triaje | [p07](mockups/p07-validacion-triaje.md) | `c9f9b6de` | Médico |

### Soporte / Administración (8-12)

| # | Pantalla | Doc | Checkpoint | Rol |
|---|---|---|---|---|
| 8 | Comparación de Modelos | [p08](mockups/p08-comparacion-modelos.md) | `94a2ab14` | Investigador |
| 9 | Gestión de Modelos | [p09](mockups/p09-gestion-modelos.md) | `d00e334a` | Administrador IA |
| 10 | Dashboard Operativo | [p10](mockups/p10-dashboard-operativo.md) | `13609941` | Médico / Admin |
| 11 | Auditoría | [p11](mockups/p11-auditoria.md) | `fa1f7471` | Auditor |
| 12 | Registro de Triaje PDF | [p12](mockups/p12-registro-triaje-pdf.md) | `009d205c` | Médico / Auditor |

---

## Referencia Rápida de Diseño

| Elemento | Valor |
|---|---|
| **Color primario** | `#0891B2` (cyan) |
| **Color acento** | `#059669` (verde) |
| **Fondo** | `#ECFEFF` |
| **Tipografía títulos** | Lexend 600 |
| **Tipografía cuerpo** | Source Sans 3 400 |
| **Altura inputs** | 44px |
| **Border radius tarjetas** | 8px |
| **Nivel I** | `#DC2626` |
| **Nivel II** | `#EA580C` |
| **Nivel III** | `#F59E0B` |
| **Nivel IV** | `#059669` |
| **Nivel V** | `#64748B` |

---

## Herramientas utilizadas

| Fase | Herramienta | Artefacto |
|---|---|---|
| Extracción requerimientos | Janus | 30 archivos RF/RNF/RT/RD |
| Desglose épicas | Epicureo | 6 épicas |
| Historias de usuario | Specter | 36 HU+TT |
| Mockups visuales | Excalidraw MCP | 12 wireframes |
| Documentación | figma-prd-mockups | Este directorio `resources/diseno/` |

---

## Cómo usar esta documentación

1. **Para desarrollar una pantalla:** abre su archivo en `mockups/pNN-*.md` — contiene layout ASCII, elementos de diseño, interacciones y estados.
2. **Para consultar colores/tipografía:** abre `design-system.md`.
3. **Para ver el flujo completo:** revisa el orden de pantallas en este README.
