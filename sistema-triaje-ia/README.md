# Sistema de Triaje Multimodal IA

**TFM — Máster Universitario en Inteligencia Artificial — UNIR**

Sistema de apoyo a la decisión clínica para clasificación de pacientes en servicios de urgencias colombianos, basado en Inteligencia Artificial multimodal con explicabilidad SHAP.

## Requisitos

- Python 3.10+
- Dependencias en `requirements.txt`

## Instalación

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd sistema-triaje-ia

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar configuración
cp .env.example .env

# 5. Ejecutar la aplicación
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`.

## Usuarios de prueba

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `enfermera_01` | `admin123` | Enfermera |
| `medico_01` | `admin123` | Médico |
| `investigador_01` | `admin123` | Investigador |
| `auditor_01` | `admin123` | Auditor |

## Estructura del proyecto

```
sistema-triaje-ia/
├── app.py                    # Punto de entrada (Streamlit)
├── requirements.txt          # Dependencias
├── .env.example              # Configuración de ejemplo
├── app/
│   ├── ui/                   # Pantallas Streamlit
│   │   ├── login_page.py     # P01 — Login y recuperación
│   │   ├── user_management_page.py  # Gestión de usuarios
│   │   └── placeholders.py   # Stubs para Épicas 2-6
│   ├── services/             # Lógica de negocio
│   │   ├── auth_service.py   # Autenticación, RBAC, recuperación
│   │   └── audit_decorator.py # Decorador @auditar (stub)
│   ├── data/                 # Acceso a datos
│   │   └── database.py       # Esquema SQLite + init + seed
│   ├── ia/                   # Motor IA (Épicas 3-4)
│   └── config/               # Configuración
│       └── settings.py       # Carga .env
├── data/                     # Base de datos SQLite
├── models/                   # Modelos ML serializados
└── tests/                    # Pruebas
```

## Estado de las Épicas

| Épica | Estado |
|---|---|
| E1 · Fundación del Sistema | ✅ Implementado |
| E2 · Flujo Clínico de Triaje | 🔜 Pendiente |
| E3 · Pipeline de Entrenamiento | 🔜 Pendiente |
| E4 · Motor IA + Explicabilidad | 🔜 Pendiente |
| E5 · Auditoría y Trazabilidad | 🔜 Pendiente |
| E6 · Dashboard + Gestión Modelos | 🔜 Pendiente |
