"""
Pantalla de Control de Cambios (P13).
Cubre: HU-E8-05 (Consulta de historial de cambios).
Solo accesible para Administrador.
"""
import streamlit as st
import pandas as pd
from app.services.patient_service import PatientService

ENTIDADES = ["Paciente", "EventoTriaje", "SignosVitales", "EvaluacionClinica"]


def render_control_cambios():
    """Renderiza la pantalla P13 — Control de Cambios (solo Admin)."""
    if st.session_state.user.get("rol") != "Administrador":
        st.error("⛔ Acceso denegado. Solo el Administrador puede consultar el control de cambios.")
        return

    st.title("📝 Control de Cambios")
    st.caption("Historial de modificaciones sobre entidades clínicas · Solo Administrador")

    db_path = st.session_state.db_path
    patient_svc = PatientService(db_path)

    # ==================================================================
    # Filtros
    # ==================================================================
    with st.container(border=True):
        st.subheader("🔍 Filtros de Búsqueda")

        col1, col2, col3 = st.columns(3)

        with col1:
            entidad = st.selectbox(
                "Entidad",
                options=[""] + ENTIDADES,
                format_func=lambda x: "Todas" if x == "" else x,
                key="cc_entidad",
            )
        with col2:
            usuario = st.text_input("Usuario", placeholder="Nombre de usuario", key="cc_usuario")
        with col3:
            documento = st.text_input("Documento Paciente", placeholder="Número de documento", key="cc_doc")

        buscar = st.button("🔍 Buscar Cambios", type="primary", use_container_width=True)

    # ==================================================================
    # Resultados
    # ==================================================================
    if buscar:
        cambios = patient_svc.get_historial_cambios(
            entidad=entidad if entidad else None,
            numero_documento=documento.strip() if documento else None,
            limit=200,
        )

        # Filtrar por usuario manualmente (el servicio no tiene filtro por usuario)
        if usuario and usuario.strip():
            cambios = [c for c in cambios if c.get("usuario", "").lower() == usuario.strip().lower()]

        st.markdown(f"### 📋 {len(cambios)} Cambios Encontrados")

        if not cambios:
            st.info("No se encontraron cambios con los filtros seleccionados.")
        else:
            # Tabla de resultados
            rows = []
            for c in cambios:
                rows.append({
                    "Fecha/Hora": c.get("fecha_hora", "")[:19],
                    "Usuario": c.get("usuario", ""),
                    "Entidad": c.get("entidad", ""),
                    "Campo": c.get("campo_modificado", ""),
                    "Anterior → Nuevo": f"{c.get('valor_anterior', '—')} → {c.get('valor_nuevo', '—')}",
                    "Doc. Paciente": c.get("numero_documento", "—"),
                })

            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Exportar CSV
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Exportar a CSV",
                data=csv,
                file_name="control_cambios.csv",
                mime="text/csv",
                use_container_width=True,
            )
