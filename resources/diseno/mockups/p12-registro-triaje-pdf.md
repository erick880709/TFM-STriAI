# Pantalla 12 — Registro de Triaje Descargable (PDF)

**Archivo:** `resources/diseno/mockups/p12-registro-triaje-pdf.md`  
**Checkpoint Excalidraw:** `009d205c20d04fd5aa`  
**Rol(es):** Médico / Auditor  
**Ubicación en flujo:** Generado desde P7 (Validación) o P11 (Auditoría)

---

## Objetivo
Generar un documento PDF descargable que cumpla con los requisitos de registro de triaje de la normativa colombiana (Resolución 5596/2015). El documento anonimiza al paciente e incluye: clasificación IA vs. profesional, signos vitales, motivo de consulta, top 5 variables SHAP y metadatos del modelo.

## Layout y Componentes (formato PDF)

```
┌──────────────────────────────────────────────────────────────┐
│        REGISTRO DE TRIAJE — Resolución 5596 de 2015          │
│   Sistema de Triaje Multimodal IA · Servicio de Urgencias    │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│ DATOS DEL EVENTO                                             │
│ ID: TRI-2026-0719-0042                                       │
│ Fecha/Hora Ingreso: 2026-07-19 14:05:00 COT                  │
│ Profesional: Dr. Carlos Martínez (Médico)                    │
│ Paciente: [ANONIMIZADO] · Edad: 45 años · Sexo: M · RC      │
│                                                              │
│ CLASIFICACIÓN DE TRIAJE                                      │
│ ┌──────────────────────┐ ┌─────────────────────────────────┐ │
│ │ 🤖 Sugerencia IA     │ │ 👨‍⚕️ Clasificación Profesional  │ │
│ │ NIVEL II — EMERGENCIA│ │ NIVEL II — EMERGENCIA           │ │
│ │ Confianza: 72%       │ │ ✓ Concordancia                  │ │
│ └──────────────────────┘ └─────────────────────────────────┘ │
│                                                              │
│ SIGNOS VITALES                                               │
│ Temp: 38.5°C · FC: 102 lpm · FR: 28 rpm · SpO₂: 88%         │
│ PA: 145/88 mmHg · IMC: 28.4 kg/m² · Dolor: 7/10             │
│                                                              │
│ MOTIVO DE CONSULTA                                           │
│ Dolor torácico — Paciente refiere dolor opresivo iniciado    │
│ hace 20 minutos, irradiado a brazo izquierdo. Diaforesis.   │
│                                                              │
│ FACTORES DE MAYOR INFLUENCIA (SHAP)                          │
│ 1. SpO₂ baja (88%) — principal factor Nivel II               │
│ 2. Dolor torácico opresivo — compatible MTS emergencia       │
│ 3. FR elevada (28 rpm) — estrés respiratorio                 │
│ 4. PA sistólica elevada (145 mmHg) — evento cardiovascular   │
│ 5. Edad 45 + HTA + Episodios previos (3) — perfil de riesgo │
│                                                              │
│ METADATOS DEL MODELO                                         │
│ Modelo: XGBoost Early Fusion v1.2 · Tiempo: 2.1s             │
│ ─────────────────────────────────────────────────────────── │
│ Documento generado automáticamente. Complemento de la HCE.   │
└──────────────────────────────────────────────────────────────┘
```

## Elementos de diseño

| Elemento | Propiedad | Valor |
|---|---|---|
| Título PDF | Color | `#164E63`, Lexend 700, 18px |
| Secciones | Color título | `#0891B2`, Lexend 600, 14px |
| Divider horizontal | Color | `#0891B2` |
| Tarjeta IA | Background | `#FFF7ED`, border `#EA580C` |
| Tarjeta Profesional | Background | `#F0FDF4`, border `#059669` |
| Footer | Color | `#94A3B8`, Source Sans 10px italic |

## Contenido del PDF

| Sección | Campos incluidos |
|---|---|
| Datos del Evento | ID, fecha/hora ingreso, profesional, paciente anonimizado (edad, sexo, régimen) |
| Clasificación | Nivel IA + confianza + Nivel profesional + concordancia |
| Signos Vitales | 8 variables registradas + IMC + dolor |
| Motivo Consulta | Texto libre completo |
| SHAP Top 5 | Variables + descripción clínica + dirección del impacto |
| Metadatos | Modelo, versión, tiempo de inferencia, fecha predicción |

## Interacciones

| Acción | Respuesta |
|---|---|
| Click "Descargar Registro" (desde P7) | Genera y descarga PDF en < 5 segundos |
| Click "Exportar PDF" (desde P11) | Genera PDF del evento seleccionado |

## Notas
- El PDF **anonimiza automáticamente** al paciente (sin nombre, sin número de documento)
- Incluye numeración de página y fecha de generación
- Formato profesional con membrete del sistema
