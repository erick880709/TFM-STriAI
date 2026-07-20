# Pantalla 5 — Clasificación IA

**Archivo:** `resources/diseno/mockups/p05-clasificacion-ia.md`  
**Checkpoint Excalidraw:** `e6a776c79d6042e9b8`  
**Rol(es):** Médico / Enfermera  
**Ubicación en flujo:** Paso 4 de 7 · **Pantalla más crítica del sistema**

---

## Objetivo
Ejecutar la inferencia multimodal y presentar los resultados (nivel sugerido, probabilidades, SHAP) junto con el campo independiente para que el profesional registre su propia clasificación. Esta pantalla unifica lo que originalmente eran dos pantallas separadas (resultado IA + validación).

## Layout y Componentes

```
┌──────────────────────────────────────────────────────────────────┐
│ Resultado de Clasificación IA   Paso 4 de 7 · Modelo v1.2       │
│ ┌──────────────────┐ ┌──────────────┐ ┌────────────────────────┐ │
│ │ NIVEL SUGERIDO   │ │Probabilidades│ │ 👨‍⚕️ Su Clasificación  │ │
│ │    POR IA        │ │              │ │                        │ │
│ │                  │ │ I  ▏  1%     │ │ Registre su clasif.    │ │
│ │ II — EMERGENCIA  │ │ II ████ 72%  │ │ independiente. No se   │ │
│ │                  │ │ III ██  20%  │ │ autocompleta con IA.   │ │
│ │ Atención ≤30 min │ │ IV  ▏  6%   │ │                        │ │
│ │                  │ │ V   ▏  1%   │ │ Nivel asignado *       │ │
│ │ Confianza:72%    │ │              │ │ ┌────────────────────┐ │ │
│ │ Tiempo: 2.1s     │ │              │ │ │Seleccione I-V ▾    │ │ │
│ └──────────────────┘ └──────────────┘ │ └────────────────────┘ │ │
│ ┌──────────────────────────────────────┐ ┌────────────────────┐ │ │
│ │ 🔍 Explicación SHAP — ¿Por qué II?   │ │[Confirmar y Cerrar]│ │ │
│ │                                      │ └────────────────────┘ │ │
│ │ 🟠 SpO₂ 88% — factor de mayor peso  │                        │ │
│ │ 🟠 Dolor torácico — MTS emergencia  │ ┌────────────────────┐ │ │
│ │ 🟡 FR 28 rpm — estrés respiratorio  │ │⚠ Si hay discrepanc│ │ │
│ │ 🟡 PA 145 mmHg — evento cardio      │ │  Motivo obligatorio│ │ │
│ │ ⚪ Edad 45 + HTA + Episodios 3      │ └────────────────────┘ │ │
│ │                                      │                        │ │
│ │ 📋 MTS: FR+SpO₂+Temp coinciden      │                        │ │
│ └──────────────────────────────────────┘                        │
└──────────────────────────────────────────────────────────────────┘
```

## Elementos de diseño

| Elemento | Propiedad | Valor |
|---|---|---|
| Tarjeta nivel sugerido | Background | `#FFF7ED` |
| Nivel II texto | Color | `#EA580C`, Lexend 700, 32px |
| Barra probabilidad II | Color | `#EA580C`, 170px ancho |
| Tarjeta SHAP | Ancho | 600px |
| Variables SHAP críticas | Color | `#EA580C` (🟠) |
| Variables moderadas | Color | `#164E63` (🟡) |
| Campo profesional | Border | `#EA580C`, background `#FFF7ED` |
| Botón confirmar (inactivo) | Background | `#E2E8F0` |
| Alerta discrepancia | Background | `#FEF2F2` |

## Flujo detallado (RD-003)

```
1. Sistema ejecuta modelo con TODAS las variables (estructuradas + NLP)
2. Se muestra: nivel IA + probabilidades + confianza + tiempo + SHAP
3. Profesional selecciona SU nivel en campo independiente (NUNCA autocompletado)
4. Sistema calcula Concordancia = (NivelIA == NivelProfesional)
5. Si Concordancia = No → EXIGE MotivoDiscrepancia
6. Cierre del evento
```

## Interacciones

| Acción | Respuesta |
|---|---|
| Carga de página | Spinner "Ejecutando modelo IA..." (~2s) |
| Resultados listos | Se muestran simultáneamente: nivel, barras, SHAP |
| Seleccionar nivel profesional | Se habilita botón "Confirmar y Cerrar" |
| Profesional = IA | Concordancia = Sí → cierre directo |
| Profesional ≠ IA | Se exige MotivoDiscrepancia → luego cierre |

## Estados

| Estado | Descripción |
|---|---|
| Cargando | Spinner + "Ejecutando modelo IA..." |
| Resultados | Mockup mostrado arriba |
| Error inferencia | "Modelo no disponible — continúe con clasificación manual" |
| Discrepancia | Campo MotivoDiscrepancia visible y obligatorio |
