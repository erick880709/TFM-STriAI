# Pantalla 10 — Dashboard Operativo

**Archivo:** `resources/diseno/mockups/p10-dashboard-operativo.md`  
**Checkpoint Excalidraw:** `13609941ff5e454a82`  
**Rol(es):** Médico / Administrador  
**Ubicación en flujo:** Soporte / Administración

---

## Objetivo
Panel de control con KPIs operativos del servicio de urgencias, distribución de triajes por nivel, desempeño del modelo IA con semáforo de metas, y matriz de concordancia IA vs. profesional.

## Layout y Componentes

```
┌──────────────────────────────────────────────────────────────┐
│ Dashboard Operativo                 Período: Julio 2026      │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│ │ 1,247    │ │ 4:32     │ │ 78%      │ │ 99.2%    │        │
│ │ Triajes  │ │ Tiempo   │ │ Concord. │ │ Disp. IA │        │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│ ┌─────────────────────────┐ ┌──────────────────────────────┐│
│ │ Distribución por Niveles│ │ Desempeño del Modelo IA      ││
│ │       I (2%)            │ │                              ││
│ │   ██  II (8%)           │ │ F1: 0.84 🟢  Prec: 0.86 🟢  ││
│ │  ████ III (25%)         │ │ Recall: 0.82 🟢  AUC: 0.89🟢││
│ │ ██████ IV (45%)         │ │                              ││
│ │  ████  V (20%)          │ │ 🟢 Todas las métricas        ││
│ │                         │ │    superan las metas         ││
│ └─────────────────────────┘ └──────────────────────────────┘│
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Concordancia IA vs. Profesional                          │ │
│ │ 78% Global  │ NI:92% NII:81% NIII:65% NIV:82% NV:91%   │ │
│ │ 📌 Mayor discrepancia en Nivel III (zona gris).          │ │
│ │ 22% de casos con divergencia.  [Ver 274 discrepancias →]│ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Elementos de diseño

| Elemento | Propiedad | Valor |
|---|---|---|
| KPIs | Ancho | 170px, fondo blanco |
| Valores KPI | Color | `#0891B2`, `#EA580C`, `#059669` según métrica |
| Barras distribución | Colores | I:`#DC2626` II:`#EA580C` III:`#F59E0B` IV:`#059669` V:`#64748B` |
| Semáforo metas | Color | 🟢 `#059669` = cumple |
| Tarjeta concordancia | Ancho | 910px full width |

## Indicadores del dashboard

| Indicador | Fuente | Meta |
|---|---|---|
| Total triajes | EventoTriaje (COUNT) | — |
| Tiempo promedio | FechaHoraCierre - FechaHoraIngreso | — |
| Concordancia IA | COUNT(Concordancia = Sí) / COUNT(*) | — |
| Disponibilidad IA | COUNT(Inferencia exitosa) / COUNT(Inferencia solicitada) | > 99% |
| F1-Score | Evaluación offline (E3) | ≥ 0.82 |
| Precision | Evaluación offline | ≥ 0.85 |
| Recall | Evaluación offline | ≥ 0.80 |
| AUC-ROC | Evaluación offline | ≥ 0.87 |

## Interacciones

| Acción | Respuesta |
|---|---|
| Cambiar período | Todos los KPIs y gráficos se recalculan |
| Click "Ver N discrepancias" | Navega a listado filtrado de eventos con Concordancia = No |
| Hover sobre barra de distribución | Tooltip con valor absoluto y porcentaje |
