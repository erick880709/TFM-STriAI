# Pantalla 2 — Registro de Paciente

**Archivo:** `resources/diseno/mockups/p02-registro-paciente.md`  
**Checkpoint Excalidraw:** `77e0a5983363417ebb`  
**Rol(es):** Personal Administrativo  
**Ubicación en flujo:** Paso 1 de 7

---

## Objetivo
Registrar un nuevo paciente en el sistema, con búsqueda automática de duplicados y captura de variables de alto peso predictivo (ViaLlegada, EpisodiosPreviosUrgencias).

## Layout y Componentes

```
┌──────────────────────────────────────────────────────────┐
│ Registro de Paciente          Paso 1 de 7 · Flujo Triaje │
│ ┌────────────────────────────┐ ┌────────────────────────┐│
│ │ Datos del Paciente         │ │ ⚠ Paciente Existente   ││
│ │                            │ │ Este documento ya está  ││
│ │ Tipo Documento *  Núm Doc │ │ registrado.             ││
│ │ [Cédula Ciudadanía ▾] [12…│ │ Último triaje: 2026-06  ││
│ │                            │ │ Nivel III · Episodios:3 ││
│ │ Fecha Nacimiento *  Sexo * │ └────────────────────────┘│
│ │ [YYYY-MM-DD      ] [Masc…│                            │
│ │                            │                            │
│ │ Vía Llegada * ⚠ Variable  │                            │
│ │ [Particular ▾            ] │                            │
│ │ ⚠ Variable de alto peso   │                            │
│ │   predictivo               │                            │
│ │                            │                            │
│ │ Régimen Salud    EPS       │                            │
│ │ [            ]  [        ] │                            │
│ └────────────────────────────┘                            │
│ ┌──────────────┐                                          │
│ │ Continuar →  │  Primary #0891B2                         │
│ └──────────────┘                                          │
└──────────────────────────────────────────────────────────┘
```

## Elementos de diseño

| Elemento | Propiedad | Valor |
|---|---|---|
| Tarjeta datos | Ancho | 520px |
| Inputs obligatorios | Border | `#A5F3FC` |
| ViaLlegada | Background | `#FFF7ED` (destacado) |
| ViaLlegada | Border | `#EA580C` (alerta naranja) |
| Alerta duplicado | Background | `#FFF7ED` |
| Edad auto-calculada | Color | `#059669` (verde) |

## Interacciones

| Acción | Respuesta |
|---|---|
| Perder foco en Número Documento | Búsqueda automática de duplicados |
| Documento ya existe | Panel lateral naranja con datos del paciente existente |
| Completar Fecha Nacimiento | Edad se calcula automáticamente |
| Click "Continuar" | Valida campos obligatorios → crea evento de triaje → navega a P3 |

## Estados

| Estado | Descripción |
|---|---|
| Default | Formulario limpio |
| Paciente existente | Panel de alerta + datos precargados del paciente |
| Error validación | Campos con borde rojo + mensaje bajo el campo |
