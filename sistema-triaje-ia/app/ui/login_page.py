"""
Pantalla de Login (P01).
Mockup: resources/diseno/mockups/p01-login.md
Cubre: HU-E1-01 (Login), HU-E1-03 (Recuperación), HU-E1-04 (Cierre sesión).
"""
import streamlit as st
import time
from datetime import datetime
from app.services.auth_service import AuthService


def render_login(auth: AuthService):
    """Renderiza la pantalla de login según el diseño P01."""

    # ------------------------------------------------------------------
    # Verificar cierre por inactividad (HU-E1-04)
    # ------------------------------------------------------------------
    query_params = st.query_params
    if query_params.get("expired") == "1":
        st.warning("⏰ Su sesión expiró por inactividad. Ingrese nuevamente.")

    # ------------------------------------------------------------------
    # Layout centrado estilo tarjeta (P01)
    # ------------------------------------------------------------------
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Tarjeta de login
        with st.container(border=True):
            # Título
            st.markdown(
                "<h2 style='text-align:center; color:#164E63; font-family:Lexend;'>"
                "Sistema de Triaje IA</h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='text-align:center; color:#64748B; font-size:13px;'>"
                "Servicio de Urgencias · Colombia</p>",
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # Formulario de login
            username = st.text_input(
                "Usuario",
                placeholder="usuario@hospital.gov.co",
                key="login_username",
                label_visibility="collapsed",
            )
            st.caption("Usuario")  # Label visible

            password = st.text_input(
                "Contraseña",
                type="password",
                key="login_password",
                label_visibility="collapsed",
            )
            st.caption("Contraseña")

            st.markdown("<br>", unsafe_allow_html=True)

            # Botón de login
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("Iniciar Sesión", type="primary", width='stretch'):
                    user = auth.login(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.login_time = datetime.utcnow()
                        st.session_state.page = "registro_paciente"
                        st.success("✅ Sesión iniciada")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña inválidos")

            # Link de recuperación (HU-E1-03)
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("¿Olvidó su contraseña?"):
                _render_password_recovery(auth)

        # Footer
        st.markdown(
            "<p style='text-align:center; color:#94A3B8; font-size:10px; margin-top:24px;'>"
            "TFM · UNIR · Máster en Inteligencia Artificial · v1.0 Demo</p>",
            unsafe_allow_html=True,
        )

    # ------------------------------------------------------------------
    # Verificación de sesión activa (HU-E1-04)
    # ------------------------------------------------------------------
    if "user" in st.session_state and st.session_state.user is not None:
        login_time = st.session_state.get("login_time")
        timeout_config = st.session_state.get("app_config", {})
        timeout_minutes = auth.get_timeout_minutes(timeout_config)
        if not auth.check_session_timeout(login_time, timeout_minutes):
            auth.logout()
            st.session_state.user = None
            st.session_state.login_time = None
            st.session_state.page = "login"
            st.query_params["expired"] = "1"
            st.rerun()
        # Renovar timestamp de actividad
        st.session_state.login_time = datetime.utcnow()


def _render_password_recovery(auth: AuthService):
    """Flujo de recuperación de contraseña (HU-E1-03, mockup P01)."""
    if "reset_step" not in st.session_state:
        st.session_state.reset_step = "request"

    if st.session_state.reset_step == "request":
        st.markdown("**Recuperar contraseña**")
        st.caption("Ingrese su usuario o correo electrónico. Recibirá un enlace de restablecimiento.")
        recovery_input = st.text_input("Usuario o email", key="recovery_input")

        if st.button("Enviar enlace de restablecimiento", key="send_reset"):
            token = auth.generate_reset_token(recovery_input)
            if token:
                st.session_state.reset_token = token
                st.session_state.reset_step = "reset"
                st.success("✅ Se ha generado un token de restablecimiento.")
                if st.session_state.app_config.get("env") == "development":
                    st.info(f"🔑 Token (desarrollo): `{token}`")
                st.rerun()
            else:
                st.error("No se encontró un usuario con ese identificador.")

    elif st.session_state.reset_step == "reset":
        st.markdown("**Establecer nueva contraseña**")
        st.caption("La contraseña debe tener mínimo 8 caracteres, 1 mayúscula y 1 número.")

        new_pwd = st.text_input("Nueva contraseña", type="password", key="new_pwd")
        confirm_pwd = st.text_input("Confirmar contraseña", type="password", key="confirm_pwd")

        if st.button("Cambiar contraseña", key="change_pwd"):
            if new_pwd != confirm_pwd:
                st.error("Las contraseñas no coinciden.")
            elif len(new_pwd) < 8:
                st.error("La contraseña debe tener al menos 8 caracteres.")
            else:
                success = auth.reset_password(st.session_state.reset_token, new_pwd)
                if success:
                    st.success("✅ Contraseña actualizada. Inicie sesión con su nueva contraseña.")
                    st.session_state.reset_step = "request"
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("El token expiró o no es válido. Solicite uno nuevo.")
                    st.session_state.reset_step = "request"
