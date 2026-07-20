"""
Sistema de Triaje Multimodal IA
TFM - Máster en Inteligencia Artificial - UNIR
Aplicación principal (Streamlit)
"""
import streamlit as st
import sys
import os
import importlib

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import load_config, get_db_path
from app.data.database import init_db

print("[APP] STARTING", file=sys.stderr, flush=True)

# Forzar recarga de módulos para evitar caché stale de Streamlit
for prefix in ("app.services.auth", "app.ui.login_page", "app.ui.patient_page",
               "app.ui.vital_signs_page", "app.ui.clinical_eval_page",
               "app.ui.triage_validation_page", "app.ui.ia_classification_page",
               "app.ui.dashboard_page", "app.ui.model_management_page",
               "app.ui.audit_page", "app.ui.user_management_page",
               "app.ui.control_cambios_page", "app.ui.historico_paciente_page"):
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith(prefix):
            del sys.modules[mod_name]

import app.services.auth_service as auth_mod
importlib.reload(auth_mod)
from app.services.auth_service import AuthService
print("[APP] modules reloaded", file=sys.stderr, flush=True)

# ---------------------------------------------------------------------------
# Configuración inicial (solo una vez por sesión)
# ---------------------------------------------------------------------------
if "app_initialized" not in st.session_state:
    cfg = load_config()
    st.session_state.app_config = cfg
    st.session_state.db_path = get_db_path(cfg)
    init_db(st.session_state.db_path)
    st.session_state.auth_service = AuthService(st.session_state.db_path)
    st.session_state.app_initialized = True

# ---------------------------------------------------------------------------
# Sidebar — Navegación y sesión
# ---------------------------------------------------------------------------
# Recrear AuthService con la clase recargada para evitar uso de clase vieja
if "db_path" in st.session_state:
    auth: AuthService = auth_mod.AuthService(st.session_state.db_path)
else:
    auth: AuthService = None

with st.sidebar:
    st.title("🏥 Triaje IA")
    st.caption("Servicio de Urgencias · Colombia")

    if "user" not in st.session_state or st.session_state.user is None:
        st.markdown("---")
    else:
        user = st.session_state.user
        st.success(f"✅ {user['nombre_usuario']}")
        st.caption(f"Rol: **{user['rol']}**")

        # Menú según rol
        roles_permitidos = auth.get_allowed_pages(user["rol"])

        st.markdown("---")
        st.subheader("📋 Flujo Clínico")

        if "RegistroPaciente" in roles_permitidos:
            if st.button("📝 Registrar Paciente", use_container_width=True):
                st.session_state.page = "registro_paciente"
        if "SignosVitales" in roles_permitidos:
            if st.button("💓 Signos Vitales", use_container_width=True):
                st.session_state.page = "signos_vitales"
        if "EvaluacionClinica" in roles_permitidos:
            if st.button("🩺 Evaluación Clínica", use_container_width=True):
                st.session_state.page = "evaluacion_clinica"
        if "ClasificacionIA" in roles_permitidos:
            if st.button("🧠 Clasificación IA", use_container_width=True):
                st.session_state.page = "clasificacion_ia"
        if "ClasificacionIA" in roles_permitidos:
            if st.button("✅ Validación y Cierre", use_container_width=True):
                st.session_state.page = "validacion_triaje"

        st.markdown("---")
        st.subheader("📊 Soporte")
        if "Dashboard" in roles_permitidos:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
        if "GestionModelos" in roles_permitidos:
            if st.button("⚙️ Gestión Modelos", use_container_width=True):
                st.session_state.page = "gestion_modelos"
        if "ComparacionModelos" in roles_permitidos:
            if st.button("🔬 Comparar Modelos", use_container_width=True):
                st.session_state.page = "comparacion_modelos"
        if "Auditoria" in roles_permitidos:
            if st.button("🔍 Auditoría", use_container_width=True):
                st.session_state.page = "auditoria"

        st.markdown("---")
        if "GestionUsuarios" in roles_permitidos:
            if st.button("👥 Gestión Usuarios", use_container_width=True):
                st.session_state.page = "gestion_usuarios"
        if "GestionUsuarios" in roles_permitidos:
            if st.button("📝 Control de Cambios", use_container_width=True):
                st.session_state.page = "control_cambios"
        st.markdown("---")
        st.subheader("📜 Consultas")
        if st.button("📜 Histórico del Paciente", use_container_width=True):
            st.session_state.page = "historico_paciente"

        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            auth.logout()
            st.rerun()

# ---------------------------------------------------------------------------
# Router de páginas
# ---------------------------------------------------------------------------
page = st.session_state.get("page", "login")

if page == "login" or "user" not in st.session_state or st.session_state.user is None:
    from app.ui.login_page import render_login
    render_login(auth)
elif page == "registro_paciente":
    from app.ui.patient_page import render_patient_registration
    render_patient_registration()
elif page == "signos_vitales":
    from app.ui.vital_signs_page import render_vital_signs
    render_vital_signs()
elif page == "evaluacion_clinica":
    from app.ui.clinical_eval_page import render_clinical_evaluation
    render_clinical_evaluation()
elif page == "clasificacion_ia":
    from app.ui.ia_classification_page import render_ia_classification
    render_ia_classification()
elif page == "validacion_triaje":
    from app.ui.triage_validation_page import render_triage_validation
    render_triage_validation()
elif page == "dashboard":
    from app.ui.dashboard_page import render_dashboard
    render_dashboard()
elif page == "gestion_modelos":
    from app.ui.model_management_page import render_model_management
    render_model_management()
elif page == "comparacion_modelos":
    from app.ui.model_comparison_page import render_model_comparison
    render_model_comparison()
elif page == "auditoria":
    from app.ui.audit_page import render_audit
    render_audit()
elif page == "gestion_usuarios":
    from app.ui.user_management_page import render_user_management
    render_user_management(auth)
elif page == "control_cambios":
    from app.ui.control_cambios_page import render_control_cambios
    render_control_cambios()
elif page == "historico_paciente":
    from app.ui.historico_paciente_page import render_historico_paciente
    render_historico_paciente()
elif page == "gestion_usuarios":
    from app.ui.user_management_page import render_user_management
    render_user_management()
else:
    st.info("Seleccione una opción del menú lateral.")
