# RD-003: Flujo de Interfaz — Clasificación IA y Validación del Profesional

**Tipo:** Información de diseño
**Fuente:** 06-CAPTURA-SINTOMAS-Y-COMPARATIVA-IA-PROFESIONAL.md §3, §5; 04-ESPECIFICACION-APLICACION-DEMO.md §4

## Descripción
Este diseño detalla el flujo de interacción más crítico de la aplicación: la pantalla donde se ejecuta la clasificación por IA, se muestran los resultados y el profesional registra su propia clasificación independiente. Es el punto donde confluyen el modelo de IA, la explicabilidad SHAP y el criterio clínico humano.

## Elementos de referencia

### Flujo detallado de la pantalla de clasificación

```
Paso 1. Captura de síntomas / motivo de consulta
        (texto libre + categoría estructurada desde la pantalla de Evaluación Clínica)
        ↓
Paso 2. El sistema ejecuta el modelo (RF-IA-001) usando TODAS las variables:
        signos vitales + demográficos + antecedentes + texto libre (embeddings)
        ↓
Paso 3. Se muestra al profesional:
        - Nivel sugerido por IA (I-V) [campo: NivelSugeridoIA]
        - Probabilidades por nivel (I-V) en formato visual (barras)
        - Nivel de confianza de la predicción
        - Tiempo de inferencia
        - Versión del modelo utilizado
        - Explicación SHAP (top variables + gráficos)
        ↓
Paso 4. El profesional registra SU PROPIA clasificación (I-V)
        [campo: NivelAsignadoProfesional]
        - Campo obligatorio, independiente del de la IA
        - NUNCA se autocompleta con el valor sugerido por la IA
        - NUNCA se sobrescribe con el valor de la IA
        ↓
Paso 5. El sistema calcula automáticamente:
        Concordancia = (NivelSugeridoIA == NivelAsignadoProfesional)
        - Si coinciden → Concordancia = Sí, se procede al cierre
        - Si difieren  → Concordancia = No, el sistema EXIGE:
          MotivoDiscrepancia (texto corto, catálogo de motivos predefinidos o texto libre)
        ↓
Paso 6. Cierre del evento de triaje
        Ambos valores (IA + profesional) + motivo de discrepancia (si aplica)
        se guardan de forma permanente e inmutable
```

### Captura de síntomas / motivo de consulta — diseño del formulario

- **Texto libre:** campo de texto multilínea (textarea), placeholder: "Describa el motivo de consulta del paciente...". Alimenta el módulo NLP (RF-NLP-*).
- **Categoría estructurada:** dropdown/autocomplete con catálogo controlado: Dolor torácico, Trauma, Disnea, Dolor abdominal, Fiebre, Cefalea, Convulsiones, Hemorragia, Intoxicación, Otro.
- Ambos campos se envían juntos al modelo.

### Nota metodológica para el TFM (documentar en Cap. 6 como limitación)

⚠️ **Sesgo de anclaje:** El orden del flujo (el profesional ve primero la sugerencia de la IA y luego clasifica) introduce un sesgo de anclaje — el profesional puede verse influido por la sugerencia de la IA en lugar de dar un juicio independiente. Esto reduce el valor de la concordancia como medida de "acuerdo entre dos evaluadores ciegos". Sin embargo, este diseño refleja el flujo clínico real (la IA apoya, no reemplaza) y la métrica resultante mide **utilidad clínica real** (¿el profesional confía en la IA?), que es más relevante para un CDSS que el acuerdo interobservador puro.

## Notas del analista
- El paso 4 es la pieza clave que diferencia este diseño de un sistema donde el profesional simplemente "corrige" el campo de la IA. Al ser campos independientes, ambos valores se preservan para la comparativa.
- Si en el futuro se desea una comparativa más rigurosa (sin sesgo de anclaje), se necesitaría un modo "a ciegas" donde el profesional clasifique sin ver la sugerencia de la IA. Esto quedó registrado como opción no implementada en `05-PENDIENTES-PARA-DIRECTORA.md`.
