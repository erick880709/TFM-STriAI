"""
Pantalla de Validación de Triaje y Cierre (P07).
Mockup: resources/diseno/mockups/p07-validacion-triaje.md
Cubre: HU-E2-06 (Flujo de estados), HU-E2-07 (Reclasificación),
       HU-E2-08 (Cierre de evento).
"""
import streamlit as st

from app.services.triage_service import (
    TriageService, NIVELES_TRIAGE, NIVELES_LABELS, ESTADOS_TRIAGE,
)
from app.services.patient_service import PatientService


def render_triage_validation():
    """Renderiza la pantalla P07 — Validación y Cierre del Triaje."""

    # ------------------------------------------------------------------
    # Inicialización de servicios
    # ------------------------------------------------------------------
    db_path = st.session_state.db_path
    if "triage_service" not in st.session_state:
        st.session_state.triage_service = TriageService(db_path)
    if "patient_service" not in st.session_state:
        st.session_state.patient_service = PatientService(db_path)

    triage_svc: TriageService = st.session_state.triage_service
    patient_svc: PatientService = st.session_state.patient_service

    # ------------------------------------------------------------------
    # Título y buscador de paciente (SIEMPRE visible)
    # ------------------------------------------------------------------
    st.title("✅ Validación de Triaje")

    # Buscador de paciente por documento — permite retomar triajes pendientes
    with st.expander("🔍 Buscar Paciente por Documento", expanded=False):
        doc_search = st.text_input("Número de Documento", placeholder="Ingrese número de identificación", key="p07_search_doc")
        if doc_search and st.button("🔍 Buscar", key="p07_search_btn"):
            pacientes = patient_svc.search_patients(doc_search, None, limit=10)
            if pacientes:
                for p in pacientes:
                    nombre = f"{p.get('nombres','')} {p.get('apellidos','')}".strip() or p.get('numero_documento','')
                    activo = triage_svc.get_active_triage_for_patient(p['id_paciente'])
                    badge = "🟢 Triaje activo" if activo else "⚪ Sin triaje"
                    col_p1, col_p2 = st.columns([3,1])
                    with col_p1:
                        st.markdown(f"**{nombre}** · {p.get('tipo_documento','')} {p.get('numero_documento','')} · {badge}")
                    with col_p2:
                        if activo:
                            if st.button("📋 Cargar", key=f"p07load_{p['id_paciente'][:8]}", width='stretch'):
                                st.session_state.triaje_activo = activo['id_triaje']
                                st.rerun()
            else:
                st.info("No se encontraron pacientes.")

    # ------------------------------------------------------------------
    # Verificar triaje activo
    # ------------------------------------------------------------------
    id_triaje = st.session_state.get("triaje_activo")
    if not id_triaje:
        st.warning("⚠️ No hay un evento de triaje activo. Use el buscador 🔍 arriba para encontrar un paciente con triaje pendiente, o registre uno nuevo.")
        if st.button("📝 Ir a Registro de Paciente"):
            st.session_state.page = "registro_paciente"
            st.rerun()
        return

    triaje = triage_svc.get_triage_event(id_triaje)
    if not triaje:
        st.error("❌ El evento de triaje no fue encontrado.")
        return

    estado_actual = triaje.get("estado", "N/A")

    # ------------------------------------------------------------------
    # Cabecera — con nombre del paciente (ampliado Épica 7)
    # ------------------------------------------------------------------
    num_doc = triaje.get("numero_documento", "")
    tipo_doc = triaje.get("tipo_documento", "")
    nombre_pac = f"{triaje.get('nombres', '')} {triaje.get('apellidos', '')}".strip()
    if nombre_pac:
        st.caption(
            f"Paciente: **{nombre_pac}** ({tipo_doc} {num_doc}) · "
            f"Evento: `{id_triaje}` · Estado: `{estado_actual}`"
        )
    else:
        st.caption(
            f"Paciente: **{tipo_doc} {num_doc}** · "
            f"Evento: `{id_triaje}` · Estado: `{estado_actual}`"
        )

    _render_flow_indicator(5)

    st.markdown("---")

    # ==================================================================
    # INDICADOR DE ESTADO ACTUAL (HU-E2-06)
    # ==================================================================
    _render_estado_actual(estado_actual)

    st.markdown("---")

    # ==================================================================
    # RESUMEN DEL EVENTO
    # ==================================================================
    with st.container(border=True):
        st.subheader("📋 Resumen del Evento")

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.markdown("**🤖 Clasificación IA**")
            nivel_ia = triaje.get("nivel_sugerido_ia")
            if nivel_ia:
                st.markdown(
                    f"### :orange[Nivel {nivel_ia}] — "
                    f"{NIVELES_LABELS.get(nivel_ia, '')}"
                )
                if triaje.get("probabilidades_ia"):
                    st.caption(f"Confianza: {_extraer_confianza(triaje.get('probabilidades_ia', ''))}")
            else:
                st.info("IA no ejecutada (Épica 4)")
        with col_r2:
            st.markdown("**👨‍⚕️ Clasificación Profesional**")
            nivel_pro = triaje.get("nivel_asignado_profesional")
            if nivel_pro:
                st.markdown(
                    f"### :green[Nivel {nivel_pro}] — "
                    f"{NIVELES_LABELS.get(nivel_pro, '')}"
                )
            else:
                st.warning("Pendiente de asignar")
        with col_r3:
            st.markdown("**Concordancia**")
            concordancia = triaje.get("concordancia")
            if concordancia is not None:
                if concordancia == 1:
                    st.success("✅ CONCORDANCIA")
                else:
                    st.error("⚠️ DISCREPANCIA")
            else:
                st.caption("—")

    st.markdown("---")

    # ==================================================================
    # ASIGNACIÓN DEL PROFESIONAL
    # ==================================================================
    st.markdown("### 👨‍⚕️ Clasificación del Profesional")

    with st.container(border=True):
        nivel_profesional = st.selectbox(
            "Nivel de Triaje asignado por el profesional *",
            options=NIVELES_TRIAGE,
            format_func=lambda x: NIVELES_LABELS.get(x, x),
            index=_find_index(NIVELES_TRIAGE, triaje.get("nivel_asignado_profesional")),
            key="p07_nivel_pro",
        )

        # Mostrar si hay concordancia
        if nivel_ia and nivel_profesional:
            if nivel_ia == nivel_profesional:
                st.success(
                    f"✅ **CONCORDANCIA:** La IA también sugiere Nivel {nivel_ia}. "
                    f"No se requiere motivo de discrepancia."
                )
            else:
                st.error(
                    f"⚠️ **DISCREPANCIA:** La IA sugiere Nivel {nivel_ia}, "
                    f"usted asigna Nivel {nivel_profesional}. "
                    f"**Debe registrar el motivo.**"
                )
                motivo_discrepancia = st.text_area(
                    "Motivo de Discrepancia *",
                    placeholder="Explique por qué difiere de la sugerencia de la IA...",
                    key="p07_motivo_disc",
                    height=80,
                )

    st.markdown("---")

    # ==================================================================
    # ACCIONES: Cierre y Reclasificación
    # ==================================================================
    col_acc1, col_acc2 = st.columns(2)

    # --- COLUMNA 1: CERRAR EVENTO (HU-E2-08) ---
    with col_acc1:
        st.markdown("### 🔒 Cerrar Evento")
        with st.container(border=True):
            st.markdown(
                "El cierre formaliza el triaje. El evento pasa a estado **Cerrado** "
                "y se vuelve inmutable."
            )

            # Checklist de prerequisitos
            st.caption("Prerrequisitos:")
            checks = []
            checks.append(("☑" if triaje.get("saturacion_o2") is not None else "☐")
                         + " Signos vitales registrados")
            checks.append(("☑" if triaje.get("motivo_categoria") is not None else "☐")
                         + " Evaluación clínica registrada")
            checks.append(("☑" if nivel_profesional else "☐")
                         + " Clasificación profesional asignada")

            for c in checks:
                st.caption(c)

            # Validar si se puede cerrar
            puede_cerrar = (
                triaje.get("saturacion_o2") is not None and
                triaje.get("motivo_categoria") is not None and
                nivel_profesional is not None
            )

            # Si hay discrepancia, requiere motivo
            if nivel_ia and nivel_profesional and nivel_ia != nivel_profesional:
                motivo_disc = st.session_state.get("p07_motivo_disc", "")
                if not motivo_disc or not motivo_disc.strip():
                    puede_cerrar = False

            if not puede_cerrar:
                st.warning("⚠️ Complete todos los prerrequisitos para cerrar el evento.")

            if st.button("✅ Cerrar Evento de Triaje", type="primary",
                        width='stretch',
                        disabled=not puede_cerrar,
                        key="p07_btn_cerrar"):
                try:
                    motivo = None
                    if nivel_ia and nivel_profesional and nivel_ia != nivel_profesional:
                        motivo = st.session_state.get("p07_motivo_disc", "")

                    resultado = triage_svc.close_event(
                        id_triaje=id_triaje,
                        nivel_profesional=nivel_profesional,
                        usuario=st.session_state.user.get("nombre_usuario", "Sistema"),
                        motivo_discrepancia=motivo,
                    )

                    st.success("🎉 **Evento cerrado exitosamente**")
                    st.balloons()

                    # Registrar en control de cambios
                    try:
                        usuario_cc = st.session_state.user.get("nombre_usuario", "Sistema")
                        num_doc_cc = triaje.get("numero_documento", "")
                        patient_svc.registrar_cambio(
                            entidad="EventoTriaje",
                            id_entidad=id_triaje,
                            campo="Estado",
                            valor_anterior=estado_actual,
                            valor_nuevo="Cerrado",
                            usuario=usuario_cc,
                            numero_documento=num_doc_cc,
                            motivo="Cierre de evento de triaje",
                        )
                    except Exception:
                        pass  # Non-blocking

                    # Mostrar resumen de cierre
                    with st.container(border=True):
                        st.markdown("### 📊 Resumen de Cierre")
                        cols = st.columns(3)
                        with cols[0]:
                            st.metric("Nivel Asignado", f"Nivel {nivel_profesional}")
                        with cols[1]:
                            conc = resultado.get("concordancia")
                            st.metric("Concordancia",
                                     "✅ Sí" if conc == 1 else ("⚠️ No" if conc == 0 else "N/A"))
                        with cols[2]:
                            st.metric("Estado Final", "Cerrado")

                    # Botón de descarga de registro PDF (HU-E5-02)
                    st.markdown("---")
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        try:
                            from app.services.report_service import ReportService
                            report_svc = ReportService(st.session_state.db_path)
                            html_bytes = report_svc.get_triage_html_bytes(id_triaje)
                            st.download_button(
                                label="📄 Descargar Registro de Triaje (HTML)",
                                data=html_bytes,
                                file_name=f"registro_triaje_{id_triaje}.html",
                                mime="text/html",
                                width='stretch',
                            )
                        except Exception as e:
                            st.caption(f"⚠️ No se pudo generar el reporte: {e}")
                    with col_dl2:
                        if st.button("📝 Iniciar Nuevo Triaje", type="primary",
                                    width='stretch'):
                            st.session_state.pop("triaje_activo", None)
                            st.session_state.pop("paciente_activo", None)
                            st.session_state.page = "registro_paciente"
                            st.rerun()

                except ValueError as ve:
                    st.error(f"❌ {ve}")

    # --- COLUMNA 2: RECLASIFICAR (HU-E2-07) ---
    with col_acc2:
        st.markdown("### 🔄 Reclasificar Paciente")
        with st.container(border=True):
            st.markdown(
                "Utilice esta opción si la condición del paciente cambia y requiere "
                "asignar un nuevo nivel de triaje."
            )

            st.caption(f"Nivel actual asignado: "
                      f"**{triaje.get('nivel_asignado_profesional', 'No asignado')}**")

            nuevo_nivel = st.selectbox(
                "Nuevo nivel de triaje",
                options=NIVELES_TRIAGE,
                format_func=lambda x: NIVELES_LABELS.get(x, x),
                key="p07_reclasif_nivel",
            )

            motivo_reclasif = st.text_area(
                "Motivo de Reclasificación *",
                placeholder="Describa el cambio en la condición del paciente que justifica la reclasificación...",
                key="p07_reclasif_motivo",
                height=80,
            )

            puede_reclasificar = (
                estado_actual in ("Validado", "Clasificado") and
                motivo_reclasif.strip() != ""
            )

            if not puede_reclasificar and estado_actual not in ("Validado", "Clasificado"):
                st.caption(
                    f"⚠️ Solo disponible desde estado 'Validado' o 'Clasificado'. "
                    f"Actual: `{estado_actual}`."
                )

            if st.button("🔄 Reclasificar", width='stretch',
                        disabled=not puede_reclasificar,
                        key="p07_btn_reclasif"):
                try:
                    resultado = triage_svc.reclassify(
                        id_triaje=id_triaje,
                        nuevo_nivel=nuevo_nivel,
                        motivo=motivo_reclasif.strip(),
                        usuario=st.session_state.user.get("nombre_usuario", "Sistema"),
                    )

                    st.success(
                        f"✅ Paciente reclasificado a Nivel {nuevo_nivel}. "
                        f"El nivel anterior ({resultado['nivel_anterior']}) "
                        f"queda registrado en el historial."
                    )
                    st.info("📋 Regrese a la sección de Cierre para finalizar el evento.")
                    st.rerun()

                except ValueError as ve:
                    st.error(f"❌ {ve}")

    st.markdown("---")

    # ==================================================================
    # DATOS CLÍNICOS COMPLETOS (referencia)
    # ==================================================================
    with st.expander("📊 Ver todos los datos clínicos del evento"):
        _render_datos_clinicos(triaje)


# ======================================================================
# SUBCOMPONENTES
# ======================================================================

def _render_estado_actual(estado: str):
    """Renderiza el indicador de estado actual con badges (HU-E2-06)."""
    estados_badge = {
        "Registrado":    ("📝", "gray", "Paciente registrado, esperando evaluación."),
        "EnEvaluacion":  ("🔍", "blue", "Signos vitales y evaluación clínica en curso."),
        "PendienteIA":   ("🧠", "orange", "Datos clínicos completos. Esperando clasificación IA."),
        "Clasificado":   ("🏷️", "violet", "Clasificación generada. Pendiente de validación."),
        "Validado":      ("✅", "green", "Clasificación validada por el profesional."),
        "Cerrado":       ("🔒", "green", "Evento cerrado formalmente."),
        "Cancelado":     ("❌", "red", "Evento cancelado."),
    }

    icono, color, descripcion = estados_badge.get(estado, ("❓", "gray", "Estado desconocido."))

    st.markdown(
        f"### {icono} Estado Actual: :{color}[`{estado}`]"
    )
    st.caption(descripcion)

    # Barra de progreso de estados
    todos_estados = ["Registrado", "EnEvaluacion", "PendienteIA", "Clasificado", "Validado", "Cerrado"]
    if estado in todos_estados:
        idx = todos_estados.index(estado)
    elif estado == "Cancelado":
        idx = -1
    else:
        idx = 0

    cols = st.columns(len(todos_estados))
    for i, (col, est) in enumerate(zip(cols, todos_estados)):
        with col:
            if i < idx:
                st.markdown(f"~~{est}~~ ✅")
            elif i == idx:
                st.markdown(f"**:blue-background[{est}]**")
            else:
                st.caption(est)


def _render_datos_clinicos(triaje: dict):
    """Muestra todos los datos clínicos del triaje en formato legible."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Signos Vitales**")
        st.markdown(f"- Temperatura: {triaje.get('temperatura', '—')} °C")
        st.markdown(f"- FC: {triaje.get('frecuencia_cardiaca', '—')} lpm")
        st.markdown(f"- FR: {triaje.get('frecuencia_respiratoria', '—')} rpm")
        st.markdown(f"- SpO₂: {triaje.get('saturacion_o2', '—')}%")
        st.markdown(f"- PA: {triaje.get('presion_sistolica', '—')}/{triaje.get('presion_diastolica', '—')} mmHg")
        st.markdown(f"- IMC: {triaje.get('imc', '—')}")

    with col2:
        st.markdown("**Evaluación Clínica**")
        st.markdown(f"- Motivo: {triaje.get('motivo_categoria', '—')}")
        st.markdown(f"- Dolor: {triaje.get('escala_dolor', '—')}/10")
        st.markdown(f"- Glasgow: {triaje.get('glasgow', '—')}")
        st.markdown(f"- Conciencia: {triaje.get('nivel_conciencia', '—')}")
        st.markdown(f"- Alergias: {triaje.get('alergias', '—') or 'Ninguna'}")

        antecedentes = []
        if triaje.get('diabetes'): antecedentes.append('Diabetes')
        if triaje.get('hipertension'): antecedentes.append('HTA')
        if triaje.get('enfermedad_renal'): antecedentes.append('Enf. Renal')
        if triaje.get('embarazo'): antecedentes.append('Embarazo')
        if triaje.get('cancer'): antecedentes.append('Cáncer')
        if triaje.get('cardiopatias'): antecedentes.append('Cardiopatías')
        if triaje.get('enfermedad_pulmonar'): antecedentes.append('Enf. Pulmonar')
        if triaje.get('cirugias_recientes'): antecedentes.append('Cirugías Recientes')
        st.markdown(f"- Antecedentes: {', '.join(antecedentes) if antecedentes else 'Ninguno'}")


def _extraer_confianza(probs_json: str) -> str:
    """Extrae la confianza más alta de un JSON de probabilidades."""
    import json
    try:
        probs = json.loads(probs_json)
        max_prob = max(probs.values())
        return f"{max_prob:.0%}"
    except (json.JSONDecodeError, AttributeError, ValueError):
        return "N/A"


def _find_index(options: list, value) -> int:
    """Encuentra el índice de un valor en una lista. Retorna 0 si no está."""
    if value is None:
        return 0
    try:
        return options.index(value)
    except ValueError:
        return 0


def _render_flow_indicator(paso_actual: int):
    """Indicador visual del paso actual en el flujo de triaje (HU-E2-06)."""
    pasos = [
        "1. Registro", "2. Signos", "3. Evaluación",
        "4. IA", "5. Validación", "6. Cierre",
    ]
    cols = st.columns(len(pasos))
    for i, (col, paso) in enumerate(zip(cols, pasos)):
        with col:
            if i + 1 == paso_actual:
                st.markdown(f"**:blue-background[{paso}]**")
            elif i + 1 < paso_actual:
                st.markdown(f"~~{paso}~~ ✅")
            else:
                st.caption(paso)
