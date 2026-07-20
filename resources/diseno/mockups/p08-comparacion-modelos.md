# Pantalla 8 — Comparación de Modelos

**Archivo:** `resources/diseno/mockups/p08-comparacion-modelos.md`  
**Checkpoint Excalidraw:** `94a2ab14e23e420fa2`  
**Rol(es):** Investigador  
**Ubicación en flujo:** Soporte / Administración (acceso desde sidebar)

---

## Objetivo
Comparar el desempeño de dos modelos (ej. Early Fusion vs. Late Fusion) lado a lado con métricas cuantitativas (F1, Precision, Recall, AUC-ROC, Recall Nivel I), identificando al ganador según el criterio clínico definido.

## Layout y Componentes

```
┌──────────────────────────────────────────────────────────────┐
│ Comparación de Modelos              🔬 Rol: Investigador     │
│                                                              │
│ Modelo A: [XGBoost Early Fusion v1.2 ▾] vs Modelo B: [Late…│
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Métricas Comparativas                                    │ │
│ │                                                          │ │
│ │ Métrica        Early Fusion    Late Fusion     Δ         │ │
│ │ ──────────────────────────────────────────────────────── │ │
│ │ F1-Score       0.84            0.81            +0.03 ✓   │ │
│ │ Precision      0.86            0.83                      │ │
│ │ Recall         0.82            0.79                      │ │
│ │ AUC-ROC        0.89            0.86                      │ │
│ │ Recall Nivel I 0.71            0.65            +0.06 ✓   │ │
│ │                                                          │ │
│ │ 🏆 Ganador: Early Fusion — Mejor Recall Niveles I-II     │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                          ┌──────────────────┐│
│                                          │ 📥 Exportar CSV  ││
│                                          └──────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

## Elementos de diseño

| Elemento | Propiedad | Valor |
|---|---|---|
| Selector modelo A (activo) | Background | `#F0FDF4`, border `#059669` |
| Selector modelo B | Background | `#F8FAFC` |
| Métricas ganadoras | Color | `#059669`, Lexend 600 |
| Delta positivo | Color | `#059669` |
| Banner ganador | Color | `#059669`, Lexend 600, 14px |

## Interacciones

| Acción | Respuesta |
|---|---|
| Cambiar Modelo A/B | Se recalculan métricas comparativas |
| Click "Exportar CSV" | Descarga tabla de métricas en CSV para incluir en TFM |

## Estados

| Estado | Descripción |
|---|---|
| Default | Dos modelos seleccionados, métricas visibles |
| Un solo modelo | Mensaje "Seleccione un segundo modelo para comparar" |
| Sin modelos | Mensaje "No hay modelos registrados. Registre un modelo en Gestión de Modelos." |
