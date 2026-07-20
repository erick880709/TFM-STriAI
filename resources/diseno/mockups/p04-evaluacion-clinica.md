# Pantalla 4 — Evaluación Clínica

**Archivo:** `resources/diseno/mockups/p04-evaluacion-clinica.md`  
**Checkpoint Excalidraw:** `81b8340f461343cea9`  
**Rol(es):** Enfermera / Médico  
**Ubicación en flujo:** Paso 3 de 7

---

## Objetivo
Registrar el motivo de consulta (texto libre + categoría estructurada), escala de dolor, nivel de conciencia, antecedentes clínicos, alergias y observaciones. Estos datos combinados con los signos vitales constituyen la entrada completa al modelo multimodal.

## Layout y Componentes

```
┌──────────────────────────────────────────────────────────────┐
│ Evaluación Clínica   Paso 3 de 7 · SpO₂:88% · FR:28 · FC:102│
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Motivo de Consulta                                       │ │
│ │ Categoría *                 Texto libre                  │ │
│ │ [Dolor torácico ▾        ]  ┌──────────────────────────┐ │ │
│ │                              │ Paciente refiere dolor   │ │ │
│ │                              │ torácico opresivo...     │ │ │
│ │                              └──────────────────────────┘ │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌────────────────────────┐ ┌──────────────────────────────┐ │
│ │ Evaluación             │ │ Antecedentes                 │ │
│ │                        │ │                              │ │
│ │ Escala Dolor (0-10) *  │ │ ☑ Hipertensión              │ │
│ │ [══════════●═════] 7/10│ │ ☐ Diabetes                  │ │
│ │                        │ │ ☐ Enfermedad renal          │ │
│ │ Escala de Glasgow      │ │ ☐ Cardiopatías              │ │
│ │ [15               ]    │ │ ☐ Enfermedad pulmonar       │ │
│ │                        │ │                              │ │
│ │ Nivel Conciencia *     │ │ Episodios previos urgencias  │ │
│ │ [Alerta ▾           ]  │ │ ┌────┐ ✓ Variable predictiva│ │
│ │                        │ │ │ 3  │                      │ │
│ │ Alergias               │ │ └────┘                      │ │
│ │ [Penicilina          ] │ │                              │ │
│ └────────────────────────┘ └──────────────────────────────┘ │
│ ┌──────────────────────┐                                    │
│ │   Ejecutar IA →      │  Primary #0891B2                   │
│ └──────────────────────┘                                    │
└──────────────────────────────────────────────────────────────┘
```

## Elementos de diseño

| Elemento | Propiedad | Valor |
|---|---|---|
| Textarea texto libre | Altura | 70px |
| Slider dolor | Color fill | `#EA580C` |
| Checkbox marcado | Background | `#0891B2` |
| Checkbox no marcado | Border | `#A5F3FC` |
| Episodios previos | Background | `#F0FDFA`, border `#059669` |
| Botón Ejecutar IA | Background | `#0891B2`, 48px altura |

## Variables capturadas (catálogos)

| Campo | Tipo | Valores |
|---|---|---|
| Motivo Categoría | Dropdown | Dolor torácico, Trauma, Disnea, Dolor abdominal, Fiebre, Cefalea, Convulsiones, Hemorragia, Intoxicación, Otro |
| Nivel Conciencia | Dropdown | Alerta, Somnoliento, Obnubilado, Inconsciente |
| Antecedentes | Checkboxes | Diabetes, HTA, Enf. renal, Embarazo, Cáncer, Cardiopatías, Enf. pulmonar, Cirugías recientes |

## Interacciones

| Acción | Respuesta |
|---|---|
| Seleccionar categoría | Se habilita el campo de texto libre complementario |
| Mover slider dolor | Valor numérico se actualiza en tiempo real |
| Click "Ejecutar IA" | Valida campos obligatorios → dispara inferencia → navega a P5 |

## Estados

| Estado | Descripción |
|---|---|
| Default | Formulario completo con campos vacíos |
| Parcialmente completo | Checkboxes marcados, slider en posición |
| Listo para IA | Todos los campos obligatorios completos → botón habilitado |
