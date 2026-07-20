# Pantalla 9 — Gestión de Modelos

**Archivo:** `resources/diseno/mockups/p09-gestion-modelos.md`  
**Checkpoint Excalidraw:** `d00e334a7f3f4a7181`  
**Rol(es):** Administrador IA  
**Ubicación en flujo:** Soporte / Administración

---

## Objetivo
Gestionar el ciclo de vida completo de los modelos de IA: registrar nuevos modelos, versionarlos, activar un modelo para producción (solo uno a la vez) y desactivarlo (rollback) si su desempeño degrada.

## Layout y Componentes

```
┌──────────────────────────────────────────────────────────────┐
│ Gestión de Modelos                ⚙️ Rol: Administrador IA   │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Modelos Registrados                                      │ │
│ │                                                          │ │
│ │ Nombre              Versión  Arquitectura  F1   Estado   │ │
│ │ ──────────────────────────────────────────────────────── │ │
│ │ XGBoost Early Fusion v1.2    Early Fusion  0.84 ACTIVO   │ │
│ │ XGBoost Late Fusion  v1.0    Late Fusion   0.81 EN VAL.  │ │
│ │ ...                                                     │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌──────────────────────┐                                    │
│ │  + Registrar Modelo  │  Primary #0891B2                   │
│ └──────────────────────┘                                    │
└──────────────────────────────────────────────────────────────┘
```

## Elementos de diseño

| Elemento | Propiedad | Valor |
|---|---|---|
| Badge ACTIVO | Background | `#059669`, texto blanco |
| Badge EN VALIDACIÓN | Background | `#E8F1F6`, texto `#64748B` |
| Fila header tabla | Background | `#E8F1F6` |
| Botón Rollback | Background | `#DC2626`, texto blanco |
| Botón Activar | Background | `#059669`, texto blanco |

## Interacciones

| Acción | Respuesta |
|---|---|
| Click "Activar" en modelo en validación | Promueve a producción. El modelo anterior pasa a inactivo. Genera auditoría. |
| Click "Rollb." en modelo activo | Exige motivo → desactiva el modelo → revierte al anterior. |
| Click "+ Registrar Modelo" | Abre formulario: nombre, algoritmo, arquitectura, hiperparámetros, dataset, métricas |
| Click en nombre del modelo | Despliega historial de versiones con métricas comparativas |

## Estados

| Estado | Descripción |
|---|---|
| Con modelos | Tabla con filas de modelos registrados |
| Vacío | "No hay modelos registrados. Registre el primer modelo para comenzar." |
| Confirmación rollback | Modal: "¿Confirma desactivar este modelo? Ingrese el motivo." |
