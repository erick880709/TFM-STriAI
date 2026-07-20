# Pantalla 11 — Auditoría

**Archivo:** `resources/diseno/mockups/p11-auditoria.md`  
**Checkpoint Excalidraw:** `fa1f74713a454758a7`  
**Rol(es):** Auditor  
**Ubicación en flujo:** Soporte / Administración

---

## Objetivo
Consultar el registro inmutable de auditoría con filtros (usuario, fecha, acción, entidad), visualizar resultados paginados y exportar en CSV, Excel y PDF. Todos los accesos y modificaciones del sistema quedan registrados aquí.

## Layout y Componentes

```
┌──────────────────────────────────────────────────────────────┐
│ Auditoría                           🔍 Rol: Auditor          │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Filtros: [Usuario ▾] [2026-07-01→2026-07-19] [Acción ▾] │ │
│ │                                                [Buscar]  │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ 1,247 resultados encontrados                                 │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Fecha/Hora         Usuario    Acción              Detalle │ │
│ │ ──────────────────────────────────────────────────────── │ │
│ │ 2026-07-19 14:32  enfermera_01 CLASIFICACION_VALIDADA... │ │
│ │ 2026-07-19 14:15  medico_03    RECLASIFICACION           │ │
│ │ 2026-07-19 14:10  sistema      INFERENCIA_EJECUTADA      │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐    │
│ │📥 Exportar CSV │ │📥 Exportar Excel│ │📥 Exportar PDF │    │
│ └────────────────┘ └────────────────┘ └────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## Filtros disponibles

| Filtro | Tipo | Valores |
|---|---|---|
| Usuario | Texto / dropdown | Cualquier usuario del sistema |
| Fecha | Rango (desde-hasta) | Selector de fechas |
| Acción | Dropdown | LOGIN, INFERENCIA, CLASIFICACION, RECLASIFICACION, CIERRE, etc. |
| Entidad | Dropdown | Paciente, EventoTriaje, PrediccionIA, Modelo |
| Nivel Triaje | Dropdown | I, II, III, IV, V |

## Interacciones

| Acción | Respuesta |
|---|---|
| Aplicar filtros + "Buscar" | Resultados paginados (20 por página) |
| Click en fila | Expande detalle completo del registro de auditoría |
| Exportar CSV | Descarga datos crudos con filtros aplicados |
| Exportar Excel | Descarga formateado con columnas y auto-ajuste |
| Exportar PDF | Descarga resumen paginado con membrete |

## Estados

| Estado | Descripción |
|---|---|
| Con resultados | Tabla con filas de auditoría |
| Sin resultados | "No se encontraron registros con los filtros seleccionados" |
| Cargando | Spinner mientras se ejecuta la consulta |
