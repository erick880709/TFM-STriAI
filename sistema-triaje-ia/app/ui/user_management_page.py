"""
Pantalla de Gestión de Usuarios (P12).
Cubre: HU-E8-01 (Visualizar), HU-E8-02 (Crear), HU-E8-03 (Actualizar), HU-E8-04 (Restablecer).
Solo accesible para Administrador.
"""
import streamlit as st
from app.services.auth_service import AuthService


ROLES_DISPONIBLES = ["Enfermera", "Medico", "Investigador", "Auditor"]

ROLES_LABELS = {
    "Enfermera": "Enfermera",
    "Medico": "Médico",
    "Investigador": "Investigador",
    "Auditor": "Auditor",
    "Administrador": "Administrador",
}


def render_user_management(auth: AuthService):
    """Renderiza la pantalla P12 — Gestión de Usuarios (solo Admin)."""
    if st.session_state.user.get("rol") != "Administrador":
        st.error("⛔ Acceso denegado. Solo el Administrador puede gestionar usuarios.")
        return

    admin_user = st.session_state.user
    users = auth.list_users()

    st.title("👥 Gestión de Usuarios")
    st.caption(f"Administración de cuentas del sistema · {len(users)} usuarios")

    tab_lista, tab_nuevo = st.tabs(["📋 Lista de Usuarios", "🆕 Nuevo Usuario"])

    with tab_lista:
        if not users:
            st.info("No hay usuarios registrados.")
        else:
            for u in users:
                _render_user_row(auth, admin_user, u)

    with tab_nuevo:
        _render_new_user_form(auth, admin_user)


def _render_user_row(auth: AuthService, admin_user: dict, u: dict):
    """Fila de usuario con datos + panel de edición expandible."""
    activo = u.get("activo") == 1
    estado_badge = "🟢 Activo" if activo else "⚫ Inactivo"
    ultimo = u.get("ultimo_acceso", "") or "Nunca"
    if ultimo != "Nunca":
        ultimo = ultimo[:16]
    uid = u["id_usuario"]
    es_admin_mismo = uid == admin_user["id_usuario"]

    with st.container(border=True):
        col_info, col_btn = st.columns([4, 1])

        with col_info:
            st.markdown(
                f"**{u['nombre_usuario']}**  |  {u.get('email', '—')}  |  "
                f"{ROLES_LABELS.get(u.get('rol', ''), u.get('rol', '—'))}  |  "
                f"{estado_badge}"
            )
            st.caption(
                f"Creado: {u.get('fecha_creacion', '')[:10]}  ·  Último acceso: {ultimo}"
            )

        with col_btn:
            if es_admin_mismo:
                st.caption("👤 _Tu cuenta_")
            else:
                with st.expander("⚙️ Editar"):
                    _render_edit_panel(auth, admin_user, u)


def _render_edit_panel(auth: AuthService, admin_user: dict, u: dict):
    """Panel de edición: email, rol, activo, reset password."""
    uid = u["id_usuario"]
    activo_actual = u.get("activo") == 1

    new_email = st.text_input(
        "Email", value=u.get("email", ""), key=f"em_{uid}"
    )
    new_rol = st.selectbox(
        "Rol", options=ROLES_DISPONIBLES,
        index=ROLES_DISPONIBLES.index(u["rol"]) if u["rol"] in ROLES_DISPONIBLES else 0,
        format_func=lambda x: ROLES_LABELS.get(x, x),
        key=f"rol_{uid}",
    )
    new_activo = st.checkbox(
        "Usuario Activo", value=activo_actual, key=f"act_{uid}",
        help="Desmarcar = no podrá iniciar sesión."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Guardar", key=f"sv_{uid}", use_container_width=True):
            ok = auth.update_user(
                admin_user_id=admin_user["id_usuario"],
                target_user_id=uid,
                email=new_email if new_email != u.get("email") else None,
                rol=new_rol if new_rol != u.get("rol") else None,
                activo=1 if new_activo else 0,
            )
            if ok:
                st.success("✅ Actualizado")
                st.rerun()
            else:
                st.error("❌ Error al actualizar")

    with col2:
        if st.button("🔑 Reset Password", key=f"rp_{uid}", use_container_width=True):
            nueva = auth.reset_password(admin_user["id_usuario"], uid)
            if nueva:
                st.success(
                    f"🔑 Nueva contraseña: **`{nueva}`**\n\n"
                    f"⚠️ Entréguela de forma segura. No se volverá a mostrar."
                )
            else:
                st.error("❌ Error al restablecer")


def _render_new_user_form(auth: AuthService, admin_user: dict):
    """Formulario para crear un nuevo usuario (HU-E8-02)."""
    with st.container(border=True):
        st.subheader("🆕 Registrar Nuevo Usuario")

        c1, c2 = st.columns(2)
        with c1:
            username = st.text_input("Nombre de Usuario *", placeholder="sin espacios", key="nu_name")
            email = st.text_input("Email *", placeholder="usuario@hospital.gov.co", key="nu_email")
        with c2:
            password = st.text_input("Contraseña *", type="password", placeholder="Mín. 6 caracteres", key="nu_pass")
            rol = st.selectbox("Rol *", options=ROLES_DISPONIBLES, format_func=lambda x: ROLES_LABELS.get(x, x), key="nu_rol")

        st.caption("💡 El rol Administrador solo se asigna por BD por seguridad.")

        if st.button("➕ Crear Usuario", type="primary", use_container_width=True):
            errs = []
            if not username or not username.strip():
                errs.append("Nombre de usuario obligatorio.")
            elif " " in username:
                errs.append("El nombre no puede tener espacios.")
            if not email or not email.strip():
                errs.append("Email obligatorio.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                errs.append("Formato de email inválido.")
            if not password or len(password) < 6:
                errs.append("Contraseña: mínimo 6 caracteres.")
            if rol not in ROLES_DISPONIBLES:
                errs.append("Rol no válido.")

            if errs:
                for e in errs:
                    st.error(f"❌ {e}")
            else:
                uid = auth.create_user(
                    admin_user_id=admin_user["id_usuario"],
                    username=username.strip(),
                    password=password,
                    email=email.strip(),
                    rol=rol,
                )
                if uid:
                    st.success(f"✅ Usuario `{username.strip()}` creado.")
                    st.rerun()
                else:
                    st.error("❌ No se pudo crear. ¿Nombre duplicado?")
