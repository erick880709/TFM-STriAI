# RD-001: Inventario de Pantallas de la Aplicación Demo

**Tipo:** Información de diseño
**Fuente:** 04-ESPECIFICACION-APLICACION-DEMO.md §3; 06-CAPTURA-SINTOMAS-Y-COMPARATIVA-IA-PROFESIONAL.md §3, §7

## Descripción
La aplicación demo consta de 12 pantallas organizadas en dos grupos: (1) flujo clínico principal (7 pantallas secuenciales) y (2) pantallas de soporte/administración (5 pantallas independientes). Cada pantalla tiene roles de acceso definidos y se asocia a los requerimientos funcionales que implementa.

## Elementos de referencia

### Flujo clínico principal (secuencial)

| # | Pantalla | Rol(es) | Propósito | RF que implementa | Estados |
|---|---|---|---|---|---|
| 1 | Login | Todos | Autenticación | RF-SEC-001, 003, 004 | Error de credenciales |
| 2 | Registro de Paciente | Personal Administrativo | Alta de episodio, búsqueda de duplicados | RF-PAC-001 a 004 | Vacío, error de validación, paciente duplicado |
| 3 | Captura de Signos Vitales | Enfermera | Ingreso de FR, SpO₂, PA, FC, temperatura, peso/talla (IMC auto) | RF-VIT-001 a 010 | Alerta por valor fuera de rango |
| 4 | Evaluación Clínica | Enfermera / Médico | Motivo de consulta (texto libre + catálogo), dolor (0-10), Glasgow, nivel de conciencia, antecedentes, alergias, texto libre | RF-EVA-001 a 007 | — |
| 5 | Ejecutar Clasificación IA | Médico / Enfermera | Dispara la inferencia, muestra probabilidades por nivel (I-V), **y captura la clasificación independiente del profesional en el mismo flujo** | RF-IA-001 a 003, 006, 009, 010 | Cargando (async), error de inferencia |
| 6 | Explicación SHAP | Médico | Top variables, impacto +/-, gráficos interpretables, comparación con MTS | RF-XAI-001 a 006 | — |
| 7 | Validación de Triaje | Médico | Registro del nivel del profesional + motivo de discrepancia cuando difiere de la IA | RF-TRI-003, 004, 005 | Discrepancia (motivo obligatorio) |

### Pantallas de soporte / administración

| # | Pantalla | Rol(es) | Propósito | RF que implementa |
|---|---|---|---|---|
| 8 | Comparación de Modelos | Investigador | Early vs. late fusion lado a lado sobre el mismo caso/dataset | RF-IA-007, RF-MOD-* |
| 9 | Gestión de Modelos | Administrador | Registrar, versionar, activar/desactivar (rollback) modelos | RF-MOD-001 a 005 |
| 10 | Dashboard Operativo | Médico / Administrador | Indicadores, distribución de triaje, tiempos, desempeño IA, concordancia IA vs. profesional | RF-REP-001 a 005 |
| 11 | Auditoría | Auditor | Consulta y exportación (CSV/Excel/PDF) de todas las acciones | RF-AUD-001 a 006 |
| 12 | Registro de Triaje Descargable | Médico / Auditor | Resumen por evento: paciente anonimizado, fecha/hora, nivel IA vs. humano, signos vitales, motivo, SHAP top | RF-REP-006, requisito normativo |

### Flujo principal para prototipo click-through

```
Login → Registro de paciente → Captura de signos vitales → Evaluación clínica
   → Ejecutar clasificación IA → Explicación SHAP → Validación de triaje
   → (rama) Reclasificación si aplica → Cierre del evento
```

### Cambios respecto a la especificación original (04-ESPECIFICACION-APLICACION-DEMO.md)
- La pantalla "Ejecutar clasificación IA" ahora incluye la captura del `NivelAsignadoProfesional` en el mismo flujo (paso 4 del flujo detallado en `06-CAPTURA-SINTOMAS-Y-COMPARATIVA-IA-PROFESIONAL.md`), no en una pantalla separada posterior.
- La pantalla "Validación de triaje" ahora captura el `MotivoDiscrepancia` cuando la clasificación del profesional difiere de la IA.
- El Dashboard Operativo ahora tiene datos reales de concordancia IA vs. profesional (`06-...` §6).

## Notas del analista
- Este inventario es el input directo para la skill `figma-prd-mockups` — cada fila de la tabla se traduce en un mockup/wireframe.
- Las pantallas 8-12 (soporte) deben diseñarse después del flujo principal, ya que dependen de tener datos y modelos registrados.
- El flujo secuencial (1→7) es lineal por diseño; la navegación libre entre pantallas de soporte se habilita desde un menú lateral o barra de navegación.
