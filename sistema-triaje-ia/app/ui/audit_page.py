"""
Pantalla de Auditoría (P11).
Mockup: resources/diseno/mockups/p11-auditoria.md
Cubre: HU-E5-01 (Consulta y exportación de auditoría).
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

from app.services.cached import get_audit_service
from app.services.audit_service import ACCIONES_AUDITABLES


def render_audit():
    """Renderiza la pantalla P11 — Consulta de Auditoría."""

    # ------------------------------------------------------------------
    # Inicialización con servicio cacheado
    # ------------------------------------------------------------------
    db_path = st.session_state.db_path
    audit_svc = get_audit_service(db_path)

    # ------------------------------------------------------------------
    # Cabecera
    # ------------------------------------------------------------------
    st.title("🔍 Auditoría del Sistema")
    st.caption("Registro inmutable de todas las acciones — Append-Only")

    # Verificar rol
    if st.session_state.user["rol"] not in ("Auditor", "Administrador"):
        st.warning("⚠️ Acceso restringido. Solo Auditores y Administradores pueden consultar auditoría.")
        return

    st.markdown("---")

    # ==================================================================
    # FILTROS
    # ==================================================================
    st.subheader("🔎 Filtros de Búsqueda")

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            # Rango de fechas
            st.caption("Período")
            fecha_desde = st.date_input(
                "Desde",
                value=datetime.now() - timedelta(days=30),
                key="audit_fecha_desde",
            )
            fecha_hasta = st.date_input(
                "Hasta",
                value=datetime.now(),
                key="audit_fecha_hasta",
            )

        with col2:
            # Tipo de acción
            acciones_disponibles = [""] + list(ACCIONES_AUDITABLES.keys())
            accion_filtro = st.selectbox(
                "Tipo de Acción",
                options=acciones_disponibles,
                format_func=lambda x: "Todas" if x == "" else ACCIONES_AUDITABLES.get(x, x),
                key="audit_accion",
            )

            # Entidad afectada
            entidad_filtro = st.selectbox(
                "Entidad Afectada",
                options=["", "Paciente", "EventoTriaje", "SignosVitales",
                        "EvaluacionClinica", "PrediccionIA", "Usuario", "Modelo"],
                key="audit_entidad",
            )

        with col3:
            # Usuario
            usuarios = audit_svc.get_usuarios_auditados()
            usuario_filtro = st.selectbox(
                "Usuario",
                options=[""] + usuarios,
                key="audit_usuario",
            )

            # Documento del paciente
            id_triaje_filtro = st.text_input(
                "Documento del Paciente o ID Triaje",
                placeholder="Ej: 1234567890 o tri-abc123...",
                key="audit_id_triaje",
                help="Busque por número de documento del paciente o ID del triaje.",
            )

        # Límite de resultados
        col_lim, col_btn = st.columns([1, 1])
        with col_lim:
            limit = st.slider("Resultados por página", 10, 200, 50, key="audit_limit")
        with col_btn:
            buscar = st.button("🔍 Buscar", type="primary", width='stretch')

    # ==================================================================
    # RESULTADOS
    # ==================================================================
    if buscar:
        page = st.session_state.get("audit_page", 0)
        offset = page * limit

        with st.spinner("Consultando registros de auditoría..."):
            resultados, total = audit_svc.query(
                usuario=usuario_filtro if usuario_filtro else None,
                accion=accion_filtro if accion_filtro else None,
                fecha_desde=f"{fecha_desde.isoformat()}T00:00:00" if fecha_desde else None,
                fecha_hasta=f"{fecha_hasta.isoformat()}T23:59:59" if fecha_hasta else None,
                entidad=entidad_filtro if entidad_filtro else None,
                id_triaje=id_triaje_filtro.strip() if id_triaje_filtro else None,
                limit=limit,
                offset=offset,
            )

        st.markdown("---")
        st.subheader(f"📋 Resultados ({total} registros encontrados)")

        if not resultados:
            st.info("No se encontraron registros con los filtros seleccionados.")
        else:
            # Paginación
            total_pages = max(1, (total + limit - 1) // limit)
            col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
            with col_pag1:
                if st.button("⬅️ Anterior", disabled=(page == 0)):
                    st.session_state.audit_page = page - 1
                    st.rerun()
            with col_pag2:
                st.caption(f"Página {page + 1} de {total_pages}")
            with col_pag3:
                if st.button("Siguiente ➡️", disabled=(page >= total_pages - 1)):
                    st.session_state.audit_page = page + 1
                    st.rerun()

            # Tabla de resultados
            rows_display = []
            for r in resultados:
                accion_label = ACCIONES_AUDITABLES.get(r.get("accion", ""), r.get("accion", ""))
                fecha = r.get("fecha_hora", "")
                if fecha and len(fecha) > 16:
                    fecha = fecha[:16].replace("T", " ")

                rows_display.append({
                    "Fecha/Hora": fecha,
                    "Usuario": r.get("usuario", ""),
                    "Acción": accion_label,
                    "Entidad": r.get("entidad_afectada", ""),
                    "ID Entidad": (r.get("id_entidad", "") or "")[:20],
                    "Observaciones": (r.get("observaciones", "") or "")[:60],
                })

            df = pd.DataFrame(rows_display)
            st.dataframe(df, width='stretch', hide_index=True, height=400)

            # ------------------------------------------------------------------
            # EXPORTACIÓN
            # ------------------------------------------------------------------
            st.markdown("---")
            st.subheader("📥 Exportar Resultados")

            col_exp1, col_exp2, col_exp3 = st.columns(3)

            with col_exp1:
                # CSV
                csv_data = audit_svc.export_csv(resultados)
                st.download_button(
                    label="📄 Descargar CSV",
                    data=csv_data,
                    file_name=f"auditoria_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    width='stretch',
                )

            with col_exp2:
                # Excel
                try:
                    df_excel = audit_svc.export_excel_dataframe(resultados)
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        df_excel.to_excel(writer, index=False, sheet_name="Auditoría")
                    excel_data = buffer.getvalue()
                    st.download_button(
                        label="📊 Descargar Excel",
                        data=excel_data,
                        file_name=f"auditoria_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width='stretch',
                    )
                except ImportError:
                    st.warning("openpyxl no instalado. `pip install openpyxl`")

            with col_exp3:
                # JSON
                import json
                json_data = json.dumps(resultados, indent=2, ensure_ascii=False, default=str)
                st.download_button(
                    label="📋 Descargar JSON",
                    data=json_data,
                    file_name=f"auditoria_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    width='stretch',
                )

            # ------------------------------------------------------------------
            # DETALLE EXPANDIBLE
            # ------------------------------------------------------------------
            st.markdown("---")
            st.subheader("🔍 Detalle de Registros")
            for i, r in enumerate(resultados[:20]):  # Mostrar máximo 20 en detalle
                accion_label = ACCIONES_AUDITABLES.get(r.get("accion", ""), r.get("accion", ""))
                with st.expander(
                    f"{r.get('fecha_hora', '')[:19]} — {accion_label} "
                    f"({r.get('usuario', 'Sistema')})"
                ):
                    cols = st.columns(2)
                    with cols[0]:
                        st.caption("ID Auditoría")
                        st.code(r.get("id_auditoria", "N/A"))
                        st.caption("Entidad Afectada")
                        st.markdown(f"`{r.get('entidad_afectada', 'N/A')}`")
                        st.caption("ID Entidad")
                        st.markdown(f"`{r.get('id_entidad', 'N/A')}`")
                    with cols[1]:
                        st.caption("Valor Anterior")
                        try:
                            va = json.loads(r.get("valor_anterior", "{}"))
                            st.json(va if va else {})
                        except (json.JSONDecodeError, TypeError):
                            st.text(str(r.get("valor_anterior", "N/A"))[:300])
                        st.caption("Valor Nuevo")
                        try:
                            vn = json.loads(r.get("valor_nuevo", "{}"))
                            st.json(vn if vn else {})
                        except (json.JSONDecodeError, TypeError):
                            st.text(str(r.get("valor_nuevo", "N/A"))[:300])


def _render_flow_indicator(paso_actual: int):
    """Indicador visual del paso actual en el flujo de triaje."""
    pasos = ["1. Registro", "2. Signos", "3. Evaluación", "4. IA", "5. Validación", "6. Cierre"]
    cols = st.columns(len(pasos))
    for i, (col, paso) in enumerate(zip(cols, pasos)):
        with col:
            if i + 1 == paso_actual:
                st.markdown(f"**:blue-background[{paso}]**")
            elif i + 1 < paso_actual:
                st.markdown(f"~~{paso}~~ ✅")
            else:
                st.caption(paso)
