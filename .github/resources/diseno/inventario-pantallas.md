# Inventario de Pantallas — Sistema de Triaje Multimodal IA

**Fecha:** 2026-07-19 · **Proyecto:** TFM UNIR · **Framework:** Streamlit (recomendado)

## Flujo Clínico Principal (7 pantallas secuenciales)

| # | Pantalla | Checkpoint Excalidraw | Propósito | Rol(es) | Estados diseñados |
|---|---|---|---|---|---|
| 1 | Login | `b4eedc99c5784bae9e` | Autenticación con usuario/contraseña, bloqueo por intentos, enlace de recuperación | Todos | Default, Error credenciales |
| 2 | Registro de Paciente | `77e0a5983363417ebb` | Alta de episodio, búsqueda de duplicados, campos obligatorios + ViaLlegada + Edad auto | Personal Administrativo | Default, Paciente existente (alerta), Campos con error |
| 3 | Captura de Signos Vitales | `caa3c5e1e02946be8f` | 8 signos vitales con validación de rangos, IMC auto, alertas visuales por valores críticos | Enfermera | Default, Valores críticos (alerta roja), Rangos normales |
| 4 | Evaluación Clínica | `81b8340f461343cea9` | Motivo consulta (texto libre + catálogo), dolor 0-10, Glasgow, conciencia, antecedentes, alergias | Enfermera / Médico | Default, Formulario completo |
| 5 | Clasificación IA | `e6a776c79d6042e9b8` | Inferencia + probabilidades I-V + explicación SHAP + campo independiente del profesional | Médico / Enfermera | Cargando (spinner), Resultados, Error inferencia, Discrepancia |
| 6 | Explicación SHAP | `4ef872d21a8a446b95` | Waterfall plot + ranking top 10 variables + comparación MTS + exportación | Médico | Default |
| 7 | Validación de Triaje | `c9f9b6dea3f141b8af` | Confirmación de concordancia o captura de motivo de discrepancia + cierre de evento + descarga | Médico | Concordancia (éxito verde), Discrepancia (alerta naranja) |

## Pantallas de Soporte / Administración (5)

| # | Pantalla | Checkpoint Excalidraw | Propósito | Rol(es) |
|---|---|---|---|---|
| 8 | Comparación de Modelos | `94a2ab14e23e420fa2` | Early vs. Late Fusion lado a lado con métricas (F1, Prec, Recall, AUC, Recall Nivel I) | Investigador |
| 9 | Gestión de Modelos | `d00e334a7f3f4a7181` | CRUD de modelos, versionado, activación/rollback, historial con métricas | Administrador IA |
| 10 | Dashboard Operativo | `13609941ff5e454a82` | KPIs (triajes, tiempo, concordancia, disponibilidad) + distribución I-V + desempeño IA + matriz concordancia | Médico / Administrador |
| 11 | Auditoría | `fa1f74713a454758a7` | Consulta con filtros (usuario, fecha, acción, entidad) + resultados paginados + exportación CSV/Excel/PDF | Auditor |
| 12 | Registro de Triaje (PDF) | `009d205c20d04fd5aa` | Documento descargable con: evento anonimizado, clasificación IA vs Profesional, signos vitales, SHAP top, metadatos | Médico / Auditor |

## Navegación

```
Login → Registro → Signos Vitales → Evaluación Clínica → Clasificación IA → SHAP → Validación → Cierre
                                                                                              ↓
                                                                                    Registro Descargable (PDF)
```

Pantallas 8-12 accesibles desde menú lateral/sidebar según rol.
