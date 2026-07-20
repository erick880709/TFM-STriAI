# Pantalla 3 — Captura de Signos Vitales

**Archivo:** `resources/diseno/mockups/p03-signos-vitales.md`  
**Checkpoint Excalidraw:** `caa3c5e1e02946be8f`  
**Rol(es):** Enfermera  
**Ubicación en flujo:** Paso 2 de 7

---

## Objetivo
Registrar 8 signos vitales con validación automática de rangos fisiológicos. Las variables de mayor peso predictivo (SpO₂, FR, Temperatura, PA sistólica) reciben prioridad visual y alertas cuando están fuera de rango.

## Layout y Componentes

```
┌──────────────────────────────────────────────────────────────┐
│ Captura de Signos Vitales    Paso 2 de 7 · Paciente: Juan P. │
│ ┌──────────────────┐ ┌──────────────────────────────────────┐│
│ │ 🔴 Prioridad Alta│ │ Resto de Signos Vitales              ││
│ │                  │ │                                      ││
│ │ Saturación O₂ * │ │ Temperatura (°C) *  Frec Card (lpm)* ││
│ │ ┌──────┐ ⚠ Bajo │ │ ┌──────┐            ┌──────┐         ││
│ │ │  88  │ (<90%) │ │ │ 38.5 │            │ 102  │         ││
│ │ └──────┘        │ │ └──────┘            └──────┘         ││
│ │                  │ │                                      ││
│ │ Frec Resp (rpm)*│ │ Presión Sistólica *  Presión Diast *  ││
│ │ ┌──────┐ ⚠ Elev │ │ ┌──────┐            ┌──────┐         ││
│ │ │  28  │        │ │ │ 145  │            │  88  │         ││
│ │ └──────┘        │ │ └──────┘            └──────┘         ││
│ │                  │ │                                      ││
│ │                  │ │ Peso (kg)    Talla (cm)   IMC: 28.4  ││
│ │                  │ │ ┌──────┐    ┌──────┐     auto calc   ││
│ └──────────────────┘ │ │      │    │      │                 ││
│                      │ └──────┘    └──────┘                 ││
│ ┌────────────────────┐ └──────────────────────────────────────┘│
│ │ Guardar y Continuar→│                                        │
│ └────────────────────┘                                        │
└──────────────────────────────────────────────────────────────┘
```

## Elementos de diseño

| Elemento | Propiedad | Valor |
|---|---|---|
| Tarjeta prioridad (SpO₂+FR) | Border | `#DC2626` (rojo) |
| Inputs críticos (SpO₂, FR) | Background | `#FEF2F2` |
| Valores críticos | Color texto | `#DC2626`, Lexend 600, 18px |
| Alertas | Color texto | `#DC2626`, 11px |
| Inputs normales | Background | `#F8FAFC` |
| IMC calculado | Color | `#059669` (verde) |

## Reglas de validación

| Signo vital | Rango fisiológico | Alerta |
|---|---|---|
| Temperatura | 30-45 °C | Fuera de rango |
| SpO₂ | 0-100% | < 90% (crítico) |
| FC | > 0 lpm | Negativa o 0 |
| FR | > 0 rpm | > 25 (elevada) |
| PA Sistólica | > Diastólica, > 0 | > 180 o < 90 |

## Interacciones

| Acción | Respuesta |
|---|---|
| Ingresar valor fuera de rango | Borde rojo + icono ⚠ + mensaje de alerta |
| Ingresar peso + talla | IMC se calcula automáticamente |
| Click "Guardar y Continuar" | Valida todos los campos obligatorios → guarda → navega a P4 |

## Estados

| Estado | Descripción |
|---|---|
| Default | Formulario con campos vacíos |
| Valores críticos | SpO₂/FR en tarjeta roja destacada |
| Rangos normales | Todos los inputs con borde normal `#A5F3FC` |
