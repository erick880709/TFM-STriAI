# 🎨 Plan de Diseño — STriAI Frontend

**Skill aplicada:** `.github/skills/front/SKILL.md`
**Sujeto:** Sistema de triaje clínico para urgencias colombianas
**Audiencia:** Médicos, enfermeras, administrativos de salud
**Trabajo del sitio:** Registrar pacientes, capturar signos vitales, clasificar con IA, validar y cerrar triajes

---

## 1. Sistema de Tokens

### Paleta — "Cian Quirúrgico"

| Token | Hex | Rol |
|-------|-----|-----|
| `--color-scrub` | `#0A4C5C` | Fondo de sidebar, profundidad quirúrgica |
| `--color-teal` | `#0891B2` | Acción primaria, links, foco |
| `--color-ether` | `#22D3EE` | Acentos, badges, brillo sutil |
| `--color-linen` | `#F0F9FA` | Fondo general (más cálido que #ECFEFF) |
| `--color-snow` | `#FFFFFF` | Tarjetas, superficie |
| `--color-ink` | `#0F3D47` | Texto principal (más oscuro, ratio 7:1) |
| `--color-slate` | `#526771` | Texto secundario (ratio 5.2:1) |
| `--color-coral` | `#E04A3A` | Destructivo, Nivel I triaje |
| `--color-amber` | `#D97706` | Advertencia, Nivel III triaje |
| `--color-moss` | `#059669` | Éxito, Nivel IV triaje |

**Riesgo estético tomado:** El sidebar usa un cyan casi-negro (#0A4C5C) en vez del típico azul oscuro de dashboards médicos. Esto evoca la profundidad de un quirófano sin ser frío, y contrasta dramáticamente con el fondo linen claro.

### Tipografía — "Precisión Clínica"

| Rol | Familia | Peso | Tamaño | Uso |
|-----|---------|------|--------|-----|
| Display | **Lexend** | 600 | 24-28px | Títulos de página, KPIs |
| Heading | **Lexend** | 500 | 16-20px | Subtítulos, labels de sección |
| Body | **Source Sans 3** | 400 | 15px | Texto de formularios, tablas |
| Caption | **Source Sans 3** | 400 | 12-13px | Labels secundarios, footnotes |
| Data | **JetBrains Mono** | 500 | 14px | Códigos, IDs, versiones de modelo |

**Decisión deliberada:** JetBrains Mono para datos técnicos (IDs de triaje, versiones de modelo) crea una separación visual clara entre contenido clínico (Source Sans 3) y contenido de sistema. Esto es un detalle que ningún template genérico incluye.

### Layout — "Flujo Vertical"

```
┌──────────────────────────────────────────────┐
│  HEADER: breadcrumb + user + hospital        │ 56px
├────────┬─────────────────────────────────────┤
│        │                                     │
│  NAV   │         CONTENIDO                   │
│  vert  │                                     │
│  240px │   ┌──────────────────────────┐      │
│        │   │  Tarjeta / Tabla / Form  │      │
│  🏥    │   │                          │      │
│  📋    │   └──────────────────────────┘      │
│  💓    │                                     │
│  🩺    │                                     │
│  🧠    │                                     │
│  ✅    │                                     │
│  ────  │                                     │
│  📊    │                                     │
│  ⚙️    │                                     │
│  🔍    │                                     │
│        │                                     │
└────────┴─────────────────────────────────────┘
```

**Regla de layout:** Todo contenido clínico vive en tarjetas blancas con borde cyan sutil (#CFFAFE). Nada flota sin contenedor. Los formularios son verticales, nunca multi-columna en pasos críticos (reduce errores de entrada).

### Firma — "El Pulso Visual"

**Elemento memorable:** Cada signo vital muestra un indicador de pulso animado sutilmente (un anillo que se expande y contrae) cuando el valor está fuera de rango normal. No es una alerta ruidosa — es un latido visual que el personal médico entrenado reconoce instintivamente. En estado normal, el indicador es un punto verde fijo. En estado crítico, el anillo pulsa en rojo.

Este elemento:
- Es específico del dominio médico (no serviría para un e-commerce)
- No interfiere con la usabilidad (es sutil, no bloquea)
- Es memorable y distintivo
- Transmite urgencia sin estridencia

---

## 2. Principios de Diseño Aplicados

### Ground it in the subject ✅
El diseño respira entorno clínico: colores de bata quirúrgica (cyan), instrumental (acero cepillado en bordes), y la precisión de una pantalla de signos vitales (datos monoespaciados).

### Typography carries personality ✅
Lexend fue diseñado específicamente para legibilidad (por Google y Thomas Jockin), ideal para entornos donde la fatiga visual es real. Source Sans 3 es la tipografía del sistema de diseño del gobierno de EE.UU. (USWDS), usada en portales de salud.

### Structure is information ✅
La navegación vertical agrupa por momento clínico: "Flujo Clínico" (lo que el médico hace ahora) vs "Soporte" (lo que consulta después). Los números de paso (1-5) son reales: representan la secuencia obligatoria del triaje.

### Restraint and self-critique ✅
La firma (pulso visual) es el único elemento animado. Todo lo demás es estático y predecible. No hay sombras exageradas, ni gradientes decorativos, ni iconografía superflua.

---

## 3. Navegación Vertical — Estructura

```
🏥 STriAI — Triaje IA
─────────────────────
📋 FLUJO CLÍNICO
  1. Registrar Paciente
  2. Signos Vitales
  3. Evaluación Clínica
  4. Clasificación IA
  5. Validación y Cierre
─────────────────────
📊 SOPORTE
  · Dashboard
  · Gestión Modelos IA
  · Comparar Modelos
  · Auditoría
  · Gestión Usuarios
  · Control de Cambios
  · Histórico del Paciente
─────────────────────
👤 Dr. García
   Administrador
   [Cerrar Sesión]
```

**Reglas de menú:**
- Colapsable a 56px (solo iconos + números de paso)
- Ítem activo: fondo teal sólido, texto blanco
- Ítem inactivo: texto cyan claro, hover suave
- Separadores visuales entre grupos
- Números de paso (1-5) siempre visibles incluso colapsado
- Avatar del médico con inicial al fondo

---

## 4. Plan Responsive

| Breakpoint | Comportamiento |
|------------|---------------|
| ≥1024px | Sidebar 240px expandido por defecto |
| 768-1023px | Sidebar 56px colapsado (iconos + números), expandible con tap |
| <768px | Sidebar oculto, bottom nav con 5 items principales + menú hamburguesa |
