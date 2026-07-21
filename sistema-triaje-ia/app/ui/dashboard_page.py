"""
Pantalla de Dashboard Operativo (P10).
Mockup: resources/diseno/mockups/p10-dashboard-operativo.md
Cubre: HU-E6-01 (Dashboard con KPIs), HU-E6-03 (Exportación de reportes).
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import io

from app.services.dashboard_service import DashboardService

# Colores de niveles
NIVEL_COLORS = {"I": "#DC2626", "II": "#EA580C", "III": "#F59E0B", "IV": "#059669", "V": "#0891B2"}
NIVEL_ICONS = {"I": "🔴", "II": "🟠", "III": "🟡", "IV": "🟢", "V": "🔵"}


def render_dashboard():
    """Renderiza la pantalla P10 — Dashboard Operativo."""

    st.title("📊 Dashboard Operativo")
    st.caption("Indicadores de desempeño del sistema de triaje")

    # ------------------------------------------------------------------
    # MÉTRICAS DESDE EL SERVICIO (ya no SQL directo en UI)
    # ------------------------------------------------------------------
    if "dashboard_service" not in st.session_state:
        st.session_state.dashboard_service = DashboardService(st.session_state.db_path)

    svc = st.session_state.dashboard_service
    kpis = svc.get_kpis()
    triajes_7d = svc.get_triages_7d()

    # Desempaquetar KPIs
    total_triages = kpis["total_triages"]
    total_pacientes = kpis["total_pacientes"]
    triajes_hoy = kpis["triajes_hoy"]
    tasa_concordancia = kpis["tasa_concordancia"]
    concordancia_si = kpis["concordancia_si"]
    concordancia_total = kpis["concordancia_total"]
    avg_time = kpis["tiempo_inferencia_promedio"]
    tasa_cierre = kpis["tasa_cierre"]
    cerrados = kpis["cerrados"]
    estados = kpis["triajes_por_estado"]
    niveles_ia = kpis["triajes_por_nivel_ia"]
    total_con_ia = kpis["total_con_ia"]
    hoy = datetime.now().strftime("%Y-%m-%d")

    # ==================================================================
    # KPI CARDS — Fila 1
    # ==================================================================
    st.subheader("📈 Indicadores Clave (KPIs)")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        with st.container(border=True):
            st.metric("Total Triajes", f"{total_triages:,}")
            st.caption(f"Hoy: {triajes_hoy}")

    with col2:
        with st.container(border=True):
            st.metric("Pacientes", f"{total_pacientes:,}")

    with col3:
        with st.container(border=True):
            st.metric("Tasa Concordancia", f"{tasa_concordancia:.1f}%")
            st.caption(f"{concordancia_si}/{concordancia_total} eventos")

    with col4:
        with st.container(border=True):
            st.metric("Tiempo Inf. Promedio", f"{avg_time:.2f}s")
            st.caption("Meta: < 3s" + (" ✅" if avg_time < 3 else " ⚠️"))

    with col5:
        with st.container(border=True):
            cerrados = estados.get("Cerrado", 0)
            st.metric("Tasa Cierre", f"{cerrados/max(total_triages,1)*100:.1f}%")
            st.caption(f"{cerrados} cerrados")

    st.markdown("---")

    # ==================================================================
    # GRÁFICOS — Fila 2
    # ==================================================================
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Distribución por Nivel de Triaje (IA)")
        if total_con_ia > 0:
            # Crear gráfico de barras con Streamlit nativo
            for nivel in ["I", "II", "III", "IV", "V"]:
                count = niveles_ia.get(nivel, 0)
                pct = count / total_con_ia * 100
                color = NIVEL_COLORS.get(nivel, "#64748B")
                icon = NIVEL_ICONS.get(nivel, "")
                st.markdown(
                    f"{icon} **Nivel {nivel}:** {count} ({pct:.1f}%)",
                    unsafe_allow_html=True,
                )
                st.progress(pct / 100, text=f"{count} triajes")
        else:
            st.info("No hay datos de clasificación IA aún.")

    with col_b:
        st.subheader("📊 Estado de los Eventos")
        if estados:
            estado_colors = {
                "Registrado": "#94A3B8", "EnEvaluacion": "#3B82F6",
                "PendienteIA": "#F59E0B", "Clasificado": "#8B5CF6",
                "Validado": "#10B981", "Cerrado": "#059669",
                "Cancelado": "#EF4444",
            }
            for estado, color in estado_colors.items():
                count = estados.get(estado, 0)
                if count > 0:
                    st.markdown(
                        f"<span style='color:{color}; font-weight:600;'>●</span> "
                        f"**{estado}:** {count}",
                        unsafe_allow_html=True,
                    )

    st.markdown("---")

    # ==================================================================
    # CONCORDANCIA IA vs PROFESIONAL
    # ==================================================================
    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("🤖 vs 👨‍⚕️ Concordancia IA-Profesional")
        if concordancia_total > 0:
            concordancia_no = concordancia_total - concordancia_si
            concord_data = pd.DataFrame({
                "Resultado": ["Concordancia", "Discrepancia"],
                "Eventos": [concordancia_si, concordancia_no],
            })
            st.dataframe(
                concord_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Eventos": st.column_config.ProgressColumn(
                        "Eventos",
                        format="%d",
                        min_value=0,
                        max_value=concordancia_total,
                    ),
                },
            )

            if tasa_concordancia >= 80:
                st.success(f"✅ {tasa_concordancia:.1f}% de concordancia — Meta superada (≥ 80%)")
            elif tasa_concordancia >= 60:
                st.warning(f"⚠️ {tasa_concordancia:.1f}% de concordancia — Aceptable")
            else:
                st.error(f"❌ {tasa_concordancia:.1f}% de concordancia — Requiere revisión")
        else:
            st.info("No hay eventos con concordancia registrada.")

    with col_d:
        st.subheader("📅 Tendencia de Triajes (7 días)")
        if triajes_7d:
            df_tendencia = pd.DataFrame(triages_7d)
            if "dia" in df_tendencia.columns and "cnt" in df_tendencia.columns:
                st.line_chart(df_tendencia.set_index("dia")["cnt"], use_container_width=True)
            else:
                st.info("Datos insuficientes para mostrar tendencia.")
        else:
            st.info("Sin datos en los últimos 7 días.")

    st.markdown("---")

    # ==================================================================
    # EXPORTACIÓN (HU-E6-03)
    # ==================================================================
    st.subheader("📥 Exportar Reportes")

    col_exp1, col_exp2, col_exp3 = st.columns(3)

    with col_exp1:
        if st.button("📊 Exportar Dashboard (CSV)", use_container_width=True):
            export_data = {
                "Métrica": [
                    "Total Triajes", "Total Pacientes", "Tasa Concordancia",
                    "Tiempo Inferencia Promedio", "Triajes Hoy",
                ],
                "Valor": [
                    total_triages, total_pacientes, f"{tasa_concordancia:.1f}%",
                    f"{avg_time:.2f}s", triajes_hoy,
                ],
            }
            df_exp = pd.DataFrame(export_data)
            csv = df_exp.to_csv(index=False)
            st.download_button(
                "⬇️ Descargar CSV",
                csv,
                f"dashboard_{hoy}.csv",
                "text/csv",
                use_container_width=True,
            )

    with col_exp2:
        if st.button("📋 Exportar Resumen (Excel)", use_container_width=True):
            # Crear Excel con múltiples hojas
            buffer = io.BytesIO()
            try:
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    pd.DataFrame({
                        "Nivel": ["I", "II", "III", "IV", "V"],
                        "Triajes IA": [niveles_ia.get(n, 0) for n in ["I", "II", "III", "IV", "V"]],
                    }).to_excel(writer, sheet_name="Distribucion_Niveles", index=False)

                    pd.DataFrame({
                        "Estado": list(estados.keys()),
                        "Cantidad": list(estados.values()),
                    }).to_excel(writer, sheet_name="Estado_Eventos", index=False)

                    pd.DataFrame({
                        "Métrica": ["Concordancia", "Discrepancia"],
                        "Cantidad": [concordancia_si, concordancia_total - concordancia_si],
                    }).to_excel(writer, sheet_name="Concordancia", index=False)

                st.download_button(
                    "⬇️ Descargar Excel",
                    buffer.getvalue(),
                    f"reporte_triaje_{hoy}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except ImportError:
                st.warning("openpyxl necesario: `pip install openpyxl`")

    with col_exp3:
        if st.button("📄 Exportar Datos (JSON)", use_container_width=True):
            report_data = {
                "fecha_generacion": hoy,
                "total_triages": total_triages,
                "total_pacientes": total_pacientes,
                "tasa_concordancia": round(tasa_concordancia, 1),
                "tiempo_inferencia_promedio": round(avg_time, 3),
                "distribucion_niveles": niveles_ia,
                "estados": estados,
                "concordancia": {"si": concordancia_si, "no": concordancia_total - concordancia_si},
            }
            st.download_button(
                "⬇️ Descargar JSON",
                json.dumps(report_data, indent=2, ensure_ascii=False),
                f"dashboard_{hoy}.json",
                "application/json",
                use_container_width=True,
            )

    # ==================================================================
    # SEMÁFORO DE METAS
    # ==================================================================
    st.markdown("---")
    st.subheader("🚦 Semáforo de Metas del Sistema")

    metas = [
        ("F1 Macro ≥ 0.82", "Pendiente (requiere ejecutar pipeline)", "🟡"),
        ("AUC-ROC ≥ 0.87", "Pendiente (requiere ejecutar pipeline)", "🟡"),
        ("Tiempo Inferencia < 3s", f"{avg_time:.2f}s {'✅' if avg_time < 3 else '⚠️'}", "🟢" if avg_time < 3 else "🟡"),
        ("Tasa Concordancia ≥ 80%", f"{tasa_concordancia:.1f}% {'✅' if tasa_concordancia >= 80 else '⚠️'}", "🟢" if tasa_concordancia >= 80 else "🟡"),
        ("Cobertura Auditoría 100%", "✅ Registro inmutable implementado", "🟢"),
        ("Exportación CSV/Excel/JSON", "✅ 3 formatos disponibles", "🟢"),
    ]

    for meta, estado, semaforo in metas:
        col_s1, col_s2, col_s3 = st.columns([1, 3, 1])
        with col_s1:
            st.markdown(f"### {semaforo}")
        with col_s2:
            st.markdown(f"**{meta}**")
            st.caption(estado)
        with col_s3:
            pass

