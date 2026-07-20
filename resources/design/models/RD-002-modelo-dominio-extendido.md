# RD-002: Modelo de Dominio Extendido — Entidades y Relaciones

**Tipo:** Información de diseño
**Fuente:** CONTEXT TRIA.txt — Secciones 19-26 (ENT-001 a ENT-012); 03-CATALOGO-DATOS-Y-VARIABLES.md; 06-CAPTURA-SINTOMAS-Y-COMPARATIVA-IA-PROFESIONAL.md §4

## Descripción
El modelo de dominio define las entidades fundamentales del sistema, sus atributos, relaciones y reglas de integridad. Este modelo extiende el catálogo original (ENT-001 a ENT-012 de `CONTEXT_TRIA.txt`) con los campos añadidos por los documentos de consolidación técnica (03 y 06).

## Elementos de referencia

### Diagrama conceptual del dominio

```text
                                    Hospital
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
                  Servicio Urgencias             Profesional Salud
                        │                             │
                        ▼                             ▼
                     Paciente ───────────────► Triaje
                        │                          │
                        │                          │
                        ▼                          ▼
                Signos Vitales              Evaluación Clínica
                        │                          │
                        └──────────────┬───────────┘
                                       ▼
                                 Motor IA
                                       │
                      ┌────────────────┼────────────────┐
                      ▼                ▼                ▼
               Predicción       Explicación SHAP   Nivel Triaje
                      │
                      ▼
                  Auditoría
```

### Entidades principales (catálogo completo)

**ENT-001 — Paciente:**
Atributos originales: IdPaciente (UUID), TipoDocumento, NumeroDocumento, FechaNacimiento, Edad, Sexo, RégimenSalud, EPS, Municipio.
**Campos añadidos:** `ViaLlegada` (Catálogo: Ambulancia/Particular/Remisión, obligatorio), `EpisodiosPreviosUrgencias` (Entero, opcional).
Ambos son variables de alto peso predictivo según el estado del arte.

**ENT-002 — Evento de Triaje (extendido, reemplaza la versión original):**
| Campo | Tipo | Obligatorio | Quién lo llena |
|---|---|---|---|
| IdTriaje | UUID | Sí | Sistema |
| FechaHoraIngreso | DateTime | Sí | Sistema |
| FechaHoraClasificación | DateTime | Sí | Sistema |
| Estado | Catálogo | Sí | Sistema/Profesional |
| **NivelSugeridoIA** | Catálogo I-V | Sí (si se ejecutó inferencia) | Sistema (RF-IA-003) |
| **ProbabilidadesIA** | JSON {nivel: prob} | Sí | Sistema |
| **NivelAsignadoProfesional** | Catálogo I-V | Sí | Profesional |
| **Concordancia** | Booleano (calculado) | Sí | Sistema (`NivelSugeridoIA == NivelAsignadoProfesional`) |
| **MotivoDiscrepancia** | Texto/Catálogo | Solo si Concordancia = No | Profesional |
| **VersionModeloUsado** | Texto (ref. a ENT-009) | Sí | Sistema |
| ProfesionalResponsable | UUID | Sí | Sistema |

Estados: Registrado, En evaluación, Pendiente IA, Clasificado, Validado, Cerrado, Cancelado.

### Relaciones del dominio
| Origen | Relación | Destino | Cardinalidad |
|---|---|---|---|
| Paciente | tiene | Triaje | 1:N |
| Triaje | contiene | Signos Vitales | 1:1 |
| Triaje | contiene | Evaluación Clínica | 1:1 |
| Triaje | contiene | Texto Clínico | 1:1 |
| Triaje | genera | Predicción IA | 1:N |
| Predicción | genera | Explicación SHAP | 1:1 |
| Profesional | valida | Triaje | 1:N |
| Auditoría | registra | Todos los eventos | — |

### Principios de integridad
- Todo paciente debe tener un identificador único.
- Todo evento de triaje debe asociarse a un paciente.
- Toda predicción debe asociarse a un evento de triaje.
- Ninguna predicción puede existir sin una versión del modelo.
- Toda clasificación validada debe conservar el historial de cambios.
- Ningún dato clínico podrá modificarse sin generar un registro de auditoría.
- La explicación SHAP debe generarse para cada inferencia aceptada.
- Los datos utilizados para entrenamiento deben estar anonimizados.

## Notas del analista
- La extensión de ENT-002 con los campos de concordancia (`NivelSugeridoIA`, `NivelAsignadoProfesional`, `Concordancia`, `MotivoDiscrepancia`) es el cambio estructural más relevante respecto al modelo original. Sin estos campos no es posible la comparativa IA vs. profesional (RF-REP-005).
- `ViaLlegada` y `EpisodiosPreviosUrgencias` son adiciones críticas para el rendimiento del modelo (hallazgo #3 de la validación).
