# Pantalla 7 — Validación de Triaje (Cierre)

**Archivo:** `resources/diseno/mockups/p07-validacion-triaje.md`  
**Checkpoint Excalidraw:** `c9f9b6dea3f141b8af`  
**Rol(es):** Médico  
**Ubicación en flujo:** Paso 6 de 7 (último paso del flujo clínico)

---

## Objetivo
Cerrar formalmente el evento de triaje cuando la clasificación está completa. Si hay concordancia (IA == profesional), el cierre es directo. Si hay discrepancia, se exige motivo antes de permitir el cierre.

## Layout y Componentes

```
┌──────────────────────────────────────────────────────────────┐
│ Validación de Triaje    Paso 6 de 7 · Evento: TRI-2026-...  │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Resumen del Evento                                       │ │
│ │                                                          │ │
│ │ 🤖 IA sugiere: Nivel II — Emergencia (Confianza: 72%)    │ │
│ │ 👨‍⚕️ Profesional asignó: Nivel II — Emergencia             │ │
│ │                                      ✓ CONCORDANCIA      │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ ✓ Clasificación Confirmada                               │ │
│ │                                                          │ │
│ │ El nivel asignado por el profesional coincide con la     │ │
│ │ sugerencia de la IA. No se requiere motivo de            │ │
│ │ discrepancia. El evento puede cerrarse.                  │ │
│ │                                                          │ │
│ │ ☑ Clasificación IA registrada                            │ │
│ │ ☑ Clasificación profesional registrada                   │ │
│ │ ☑ Auditoría generada                                     │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌──────────────────┐ ┌──────────────────────┐               │
│ │ ✓ Cerrar Evento  │ │ 📄 Descargar Registro│               │
│ └──────────────────┘ └──────────────────────┘               │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 💡 Si hubiera discrepancia, se exigiría motivo antes     │ │
│ │    del cierre. Ambos valores quedan registrados.         │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Elementos de diseño

| Elemento | Propiedad | Valor |
|---|---|---|
| Tarjeta concordancia | Background | `#F0FDF4`, border `#059669` |
| Icono check | Color | `#059669`, Lexend 700, 32px |
| Checklist items | Color | `#059669` |
| Botón "Cerrar Evento" | Background | `#059669` |
| Botón "Descargar Registro" | Border | `#0891B2` |
| Nota informativa | Background | `#FFF7ED`, border `#EA580C` |

## Interacciones

| Acción | Respuesta |
|---|---|
| Click "Cerrar Evento" | Estado → Cerrado, timestamp de cierre, evento inmutable |
| Click "Descargar Registro" | Genera PDF (Pantalla 12) con todos los datos del evento |
| Discrepancia (flujo alternativo) | Se exige campo MotivoDiscrepancia → luego se habilita "Cerrar Evento" |

## Estados

| Estado | Descripción |
|---|---|
| Concordancia | Mockup mostrado arriba — fondo verde, check, cierre directo |
| Discrepancia | Fondo naranja, campo MotivoDiscrepancia visible y obligatorio, botón de cierre deshabilitado hasta completar |
