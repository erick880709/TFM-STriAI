"""
Pantalla de Histórico del Paciente (P14).
Control de Cambios: búsqueda por documento y listado de visitas previas.
Acceso: todos los roles.
"""
import streamlit as st
import pandas as pd
from app.services.patient_service import PatientService
from app.services.triage_service import NIVELES_LABELS

MOTIVOS_LABELS = {
    "Dolor toracico": "Dolor torácico",
    "Trauma": "Trauma",
    "Disnea": "Disnea",
    "Dolor abdominal": "Dolor abdominal",
    "Fiebre": "Fiebre",
    "Cefalea": "Cefalea",
    "Convulsiones": "Convulsiones",
    "Hemorragia": "Hemorragia",
    "Intoxicacion": "Intoxicación",
    "Otro": "Otro",
}


def render_historico_paciente():
    """Renderiza la pantalla P14 — Histórico del Paciente."""
    st.title("📜 Histórico del Paciente")
    st.caption("Consulta de visitas previas por número de documento")

    db_path = st.session_state.db_path
    patient_svc = PatientService(db_path)

    # Búsqueda por documento
    col_doc, col_btn = st.columns([3, 1])
    with col_doc:
        documento = st.text_input(
            "Número de Documento del Paciente",
            placeholder="Ingrese el número de documento (CC, TI, CE, PA, RC)...",
            key="hist_doc",
        )
    with col_btn:
        buscar = st.button("🔍 Buscar Historial", type="primary", width='stretch')

    if not buscar:
        st.info("💡 Ingrese un número de documento y presione **Buscar** para consultar el historial de visitas del paciente.")
        return

    if not documento or not documento.strip():
        st.warning("⚠️ Ingrese un número de documento para buscar.")
        return

    # Buscar paciente
    paciente = patient_svc.get_patient_by_document(documento.strip())
    if not paciente:
        st.error("❌ No se encontró ningún paciente con ese documento.")
        return

    # Mostrar datos del paciente
    nombre_completo = f"{paciente.get('nombres', '')} {paciente.get('apellidos', '')}".strip()
    with st.container(border=True):
        st.subheader(f"👤 {nombre_completo}" if nombre_completo else "👤 Paciente")
        cols = st.columns(4)
        with cols[0]:
            st.metric("Documento", paciente.get("numero_documento", "—"))
        with cols[1]:
            st.metric("Edad", f"{paciente.get('edad', '—')} años")
        with cols[2]:
            st.metric("Sexo", paciente.get("sexo", "—"))
        with cols[3]:
            st.metric("Total Visitas", paciente.get("episodios_previos_urgencias", 0))

    # Obtener historial de triajes con motivo
    triajes = _get_triages_with_motivo(patient_svc, documento.strip())

    if not triajes:
        st.info("📭 Este paciente no tiene visitas registradas a urgencias.")
        return

    st.markdown(f"### 📋 {len(triajes)} Visita(s) a Urgencias")

    # Construir tabla
    rows = []
    for t in triajes:
        fecha = t.get("fecha_hora_ingreso", "")[:16]
        motivo_raw = t.get("motivo_categoria", "") or "No registrado"
        motivo = MOTIVOS_LABELS.get(motivo_raw, motivo_raw)
        nivel_prof = t.get("nivel_asignado_profesional") or "—"
        nivel_prof_label = NIVELES_LABELS.get(nivel_prof, nivel_prof)
        nivel_ia = t.get("nivel_sugerido_ia") or "—"
        nivel_ia_label = NIVELES_LABELS.get(nivel_ia, nivel_ia)
        estado = t.get("estado", "—")

        rows.append({
            "Fecha / Hora": fecha,
            "Motivo de Asistencia": motivo,
            "Nivel Urgencia (Profesional)": nivel_prof_label,
            "Nivel Urgencia (IA)": nivel_ia_label,
            "Estado": estado,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width='stretch', hide_index=True)

    # Exportar CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Exportar Historial a CSV",
        data=csv,
        file_name=f"historico_{documento.strip()}.csv",
        mime="text/csv",
        width='stretch',
    )


def _get_triages_with_motivo(patient_svc: PatientService, documento: str, limit: int = 100):
    """
    Obtiene triajes del paciente con el motivo de consulta (MotivoCategoria).
    Usa acceso directo a BD para incluir la EvaluacionClinica.
    """
    from app.data.database import get_connection, rows_to_dicts
    conn = get_connection(patient_svc.db_path)
    try:
        rows = conn.execute(
            """SELECT e.IdTriaje, e.FechaHoraIngreso, e.Estado,
                      e.NivelSugeridoIA, e.NivelAsignadoProfesional,
                      ec.MotivoCategoria
               FROM EventoTriaje e
               JOIN Paciente p ON e.IdPaciente = p.IdPaciente
               LEFT JOIN EvaluacionClinica ec ON e.IdTriaje = ec.IdTriaje
               WHERE p.NumeroDocumento = ?
               ORDER BY e.FechaHoraIngreso DESC
               LIMIT ?""",
            (documento, limit),
        ).fetchall()
        return rows_to_dicts(rows)
    finally:
        conn.close()
