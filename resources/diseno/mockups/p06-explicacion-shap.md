# Pantalla 6 — Explicación SHAP Detallada

**Archivo:** `resources/diseno/mockups/p06-explicacion-shap.md`  
**Checkpoint Excalidraw:** `4ef872d21a8a446b95`  
**Rol(es):** Médico  
**Ubicación en flujo:** Paso 5 de 7

---

## Objetivo
Mostrar en detalle la explicación SHAP de la predicción: waterfall plot con contribución de cada variable desde el valor base hasta la predicción final, ranking de top 10 variables por importancia, y comparación con criterios MTS/Manchester.

## Layout y Componentes

```
┌──────────────────────────────────────────────────────────────┐
│ Explicación SHAP — Análisis Detallado  Paso 5 de 7          │
│ ┌──────────────────────────────────────┐ ┌──────────────────┐│
│ │ Waterfall Plot — Contribución        │ │ Top 10 Variables ││
│ │                                      │ │ por Importancia  ││
│ │ Valor base: 0.20                     │ │                  ││
│ │                                      │ │ 1. ████████████  ││
│ │ SpO₂ = 88%          ██████████ +0.34│ │ 2. ██████████    ││
│ │ Dolor torácico = Sí ████████  +0.21 │ │ 3. ████████      ││
│ │ FR = 28             █████    +0.12  │ │ 4. ██████        ││
│ │ PA Sistólica = 145  ████     +0.08  │ │ 5. ████          ││
│ │ Edad = 45 años      ███      +0.04  │ │    ...           ││
│ │                                      │ │                  ││
│ │ Predicción final (Nivel II): 0.72    │ │                  ││
│ └──────────────────────────────────────┘ └──────────────────┘│
│ ┌──────────────────┐ ┌──────────────────┐                   │
│ │ 📥 Exportar SHAP │ │ Validar Triaje → │                   │
│ └──────────────────┘ └──────────────────┘                   │
└──────────────────────────────────────────────────────────────┘
```

## Elementos de diseño

| Elemento | Propiedad | Valor |
|---|---|---|
| Barras waterfall positivas | Color | `#EA580C` (🟠 contribuye a Nivel II) |
| Barras waterfall neutras | Color | `#22D3EE` |
| Ranking barras | Color | `#EA580C` graduado por importancia |
| Valor base | Color | `#64748B`, Source Sans 11px |
| Predicción final | Color | `#EA580C`, Lexend 700, 14px |
| Botón exportar | Border | `#0891B2` |

## Interacciones

| Acción | Respuesta |
|---|---|
| Hover sobre barra waterfall | Tooltip con valor SHAP exacto y descripción clínica |
| Click "Exportar SHAP" | Descarga PNG/PDF del waterfall plot |
| Click "Validar Triaje" | Navega a P7 |

## Regla de visualización

- 🟠 Naranja = variable que **aumenta** la probabilidad del nivel predicho
- 🔵 Azul = variable que **disminuye** la probabilidad
- ⚪ Gris = variable con impacto bajo o neutro
