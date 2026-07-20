# Pantalla 1 — Login

**Archivo:** `resources/diseno/mockups/p01-login.md`  
**Checkpoint Excalidraw:** `b4eedc99c5784bae9e`  
**Rol(es):** Todos  
**Ubicación en flujo:** Punto de entrada al sistema

---

## Objetivo
Autenticar al usuario con credenciales y asignar acceso según su rol (Administrador, Médico, Enfermera, Investigador, Auditor).

## Layout y Componentes

```
┌────────────────────────────────────────────┐
│              Fondo: #ECFEFF                 │
│   ┌──────────────────────────┐             │
│   │   Tarjeta Login (blanca) │             │
│   │   ┌────────────────────┐ │             │
│   │   │ Sistema de Triaje  │ │  Lexend 22px
│   │   │ Servicio Urgencias │ │  Source Sans 13px
│   │   │     · Colombia     │ │
│   │   └────────────────────┘ │             │
│   │                          │             │
│   │   Usuario                │  Label 13px │
│   │   ┌────────────────────┐ │  Input 44px │
│   │   │ enfermera.triaje@  │ │  Bg #F8FAFC │
│   │   └────────────────────┘ │             │
│   │                          │             │
│   │   Contraseña             │             │
│   │   ┌────────────────────┐ │             │
│   │   │ ••••••••            │ │             │
│   │   └────────────────────┘ │             │
│   │                          │             │
│   │   ┌────────────────────┐ │             │
│   │   │  Iniciar Sesión    │ │  Primary #0891B2
│   │   └────────────────────┘ │  Lexend 15px bold
│   │                          │             │
│   │   ¿Olvidó su contraseña? │  Link azul 12px
│   └──────────────────────────┘             │
│   TFM · UNIR · Máster en IA · v1.0 Demo    │
└────────────────────────────────────────────┘
```

## Elementos de diseño

| Elemento | Propiedad | Valor |
|---|---|---|
| Tarjeta | Ancho × Alto | 300 × 380px |
| Tarjeta | Border radius | 8px |
| Inputs | Border color | `#A5F3FC` |
| Botón Login | Background | `#0891B2` |
| Botón Login | Texto | `#FFFFFF`, Lexend 600 |
| Link recuperación | Color | `#0891B2` |

## Interacciones

| Acción | Respuesta |
|---|---|
| Click "Iniciar Sesión" | Valida credenciales → redirige según rol |
| Credenciales incorrectas | Mensaje genérico "Usuario o contraseña inválidos" |
| 5 intentos fallidos | Cuenta bloqueada 15 min |
| Click "¿Olvidó su contraseña?" | Navega a flujo de recuperación (HU-E1-03) |
| Sesión exitosa | Redirige a Pantalla 2 (Registro de Paciente) o Dashboard según rol |

## Estados

| Estado | Descripción |
|---|---|
| Default | Formulario limpio con campos vacíos |
| Error | Borde rojo en inputs + mensaje de error bajo el botón |
| Bloqueado | Mensaje "Cuenta bloqueada. Intente de nuevo en 15 minutos" |
| Cargando | Spinner en botón durante validación |
