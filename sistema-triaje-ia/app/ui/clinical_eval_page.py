"""
Pantalla de Evaluación Clínica (P04).
Mockup: resources/diseno/mockups/p04-evaluacion-clinica.md
Cubre: HU-E2-05 (Evaluación clínica completa).
"""
import streamlit as st

from app.services.triage_service import (
    TriageService, MOTIVOS_CATEGORIA, MOTIVOS_CATEGORIA_LABELS,
    NIVELES_CONCIENCIA,
)
from app.services.patient_service import PatientService


def render_clinical_evaluation():
    """Renderiza la pantalla P04 — Evaluación Clínica."""

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
    st.title("🩺 Evaluación Clínica")

    # Buscador de paciente por documento — permite retomar triajes pendientes
    with st.expander("🔍 Buscar Paciente por Documento", expanded=False):
        doc_search = st.text_input("Número de Documento", placeholder="Ingrese número de identificación", key="p04_search_doc")
        if doc_search and st.button("🔍 Buscar", key="p04_search_btn"):
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
                            if st.button("📋 Cargar", key=f"p04load_{p['id_paciente'][:8]}", width='stretch'):
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

    # Cargar evaluación existente
    eval_existente = triage_svc.get_clinical_evaluation(id_triaje)

    # ------------------------------------------------------------------
    # Cabecera con resumen de signos vitales
    # ------------------------------------------------------------------
    # Resumen compacto de signos vitales + documento del paciente (ampliado Épica 7)
    signos_parts = []
    num_doc = triaje.get("numero_documento", "")
    tipo_doc = triaje.get("tipo_documento", "")
    nombre_pac = f"{triaje.get('nombres', '')} {triaje.get('apellidos', '')}".strip()
    if nombre_pac:
        signos_parts.append(f"Paciente: **{nombre_pac}** ({tipo_doc} {num_doc})")
    elif num_doc:
        signos_parts.append(f"Paciente: {tipo_doc} {num_doc}")
    if triaje.get("saturacion_o2") is not None:
        spo2 = triaje["saturacion_o2"]
        spo2_str = f"SpO₂: {spo2}%{' ⚠️' if spo2 < 90 else ''}"
        signos_parts.append(spo2_str)
    if triaje.get("frecuencia_respiratoria") is not None:
        fr = triaje["frecuencia_respiratoria"]
        fr_str = f"FR: {fr}{' ⚠️' if fr > 25 else ''}"
        signos_parts.append(fr_str)
    if triaje.get("frecuencia_cardiaca") is not None:
        signos_parts.append(f"FC: {triaje['frecuencia_cardiaca']}")
    if triaje.get("temperatura") is not None:
        signos_parts.append(f"Temp: {triaje['temperatura']}°C")

    st.caption(f"Paso 3 de 7 · {' · '.join(signos_parts) if signos_parts else 'Sin signos vitales'}")

    _render_flow_indicator(3)

    st.markdown("---")

    # ==================================================================
    # FORMULARIO DE EVALUACIÓN CLÍNICA
    # ==================================================================

    # --- Sección: Motivo de Consulta ---
    st.markdown("### 📋 Motivo de Consulta")

    with st.container(border=True):
        col_cat, col_texto = st.columns(2)

        with col_cat:
            motivo_cat = st.selectbox(
                "Categoría *",
                options=MOTIVOS_CATEGORIA,
                format_func=lambda x: MOTIVOS_CATEGORIA_LABELS.get(x, x),
                index=_find_index(
                    MOTIVOS_CATEGORIA,
                    eval_existente.get("motivo_categoria") if eval_existente else None,
                ),
                key="p04_motivo_cat",
            )
        with col_texto:
            motivo_texto = st.text_area(
                "Texto libre (máx. 500 caracteres)",
                value=eval_existente.get("motivo_texto_libre") if eval_existente else "",
                max_chars=500,
                height=70,
                placeholder="Describa el motivo de consulta del paciente...",
                key="p04_motivo_texto",
            )

    st.markdown("---")

    # --- Sección: Evaluación + Antecedentes (2 columnas) ---
    col_izq, col_der = st.columns(2)

    # COLUMNA IZQUIERDA: Evaluación
    with col_izq:
        st.markdown("### 🔍 Evaluación")

        with st.container(border=True):
            # Escala de dolor (slider)
            st.markdown("**Escala de Dolor (0-10) ***")
            dolor = st.slider(
                "Nivel de dolor",
                min_value=0, max_value=10,
                value=eval_existente.get("escala_dolor") if eval_existente else 0,
                key="p04_dolor",
                label_visibility="collapsed",
            )
            # Mostrar valor grande
            st.markdown(
                f"<span style='font-size:32px; font-weight:700; color:#EA580C;'>{dolor}/10</span>",
                unsafe_allow_html=True,
            )

            # Etiqueta semántica del dolor
            if dolor == 0:
                st.caption("Sin dolor")
            elif dolor <= 3:
                st.caption("Dolor leve")
            elif dolor <= 6:
                st.caption("Dolor moderado")
            elif dolor <= 8:
                st.caption("Dolor intenso")
            else:
                st.caption("🔴 Dolor máximo")

            st.markdown("---")

            # Glasgow
            glasgow = st.number_input(
                "Escala de Glasgow (3-15)",
                min_value=3, max_value=15, step=1,
                value=eval_existente.get("glasgow") if eval_existente else 15,
                key="p04_glasgow",
            )

            # Nivel de conciencia
            nivel_conciencia = st.selectbox(
                "Nivel de Conciencia *",
                options=NIVELES_CONCIENCIA,
                index=_find_index(
                    NIVELES_CONCIENCIA,
                    eval_existente.get("nivel_conciencia") if eval_existente else None,
                ),
                key="p04_conciencia",
            )

            # Alergias
            alergias = st.text_input(
                "Alergias conocidas",
                value=eval_existente.get("alergias") if eval_existente else "",
                placeholder="Ej: Penicilina, AINEs, Látex...",
                key="p04_alergias",
            )

    # COLUMNA DERECHA: Antecedentes
    with col_der:
        st.markdown("### 🏥 Antecedentes Clínicos")

        with st.container(border=True):
            st.caption("Seleccione todos los que apliquen:")

            antecedentes_def = eval_existente if eval_existente else {}

            diabetes = st.checkbox(
                "Diabetes",
                value=bool(antecedentes_def.get("diabetes", 0)),
                key="p04_diabetes",
            )
            hipertension = st.checkbox(
                "Hipertensión Arterial",
                value=bool(antecedentes_def.get("hipertension", 0)),
                key="p04_hta",
            )
            enf_renal = st.checkbox(
                "Enfermedad Renal Crónica",
                value=bool(antecedentes_def.get("enfermedad_renal", 0)),
                key="p04_renal",
            )
            embarazo = st.checkbox(
                "Embarazo",
                value=bool(antecedentes_def.get("embarazo", 0)),
                key="p04_embarazo",
            )
            cancer = st.checkbox(
                "Cáncer",
                value=bool(antecedentes_def.get("cancer", 0)),
                key="p04_cancer",
            )
            cardiopatias = st.checkbox(
                "Cardiopatías",
                value=bool(antecedentes_def.get("cardiopatias", 0)),
                key="p04_cardio",
            )
            enf_pulmonar = st.checkbox(
                "Enfermedad Pulmonar (EPOC, Asma)",
                value=bool(antecedentes_def.get("enfermedad_pulmonar", 0)),
                key="p04_pulmonar",
            )
            cirugias = st.checkbox(
                "Cirugías Recientes (< 30 días)",
                value=bool(antecedentes_def.get("cirugias_recientes", 0)),
                key="p04_cirugias",
            )

            st.markdown("---")

            # Episodios previos (campo predictivo)
            episodios_previos = st.number_input(
                "Episodios Previos en Urgencias ⚠ Predictivo",
                min_value=0, max_value=99, step=1,
                value=eval_existente.get("episodios_previos_urgencias")
                if eval_existente and eval_existente.get("episodios_previos_urgencias") is not None
                else (triaje.get("episodios_previos_urgencias", 0)),
                key="p04_episodios",
            )

    st.markdown("---")

    # --- Sección: Observaciones adicionales ---
    st.markdown("### 📝 Observaciones")

    with st.container(border=True):
        col_obs1, col_obs2 = st.columns(2)

        with col_obs1:
            medicacion = st.text_area(
                "Medicación Relevante",
                value=eval_existente.get("medicacion_relevante") if eval_existente else "",
                height=70,
                placeholder="Ej: Metformina 850mg c/12h, Enalapril 10mg/día...",
                key="p04_medicacion",
            )
        with col_obs2:
            observaciones = st.text_area(
                "Observaciones Adicionales",
                value=eval_existente.get("observaciones") if eval_existente else "",
                height=70,
                placeholder="Notas clínicas relevantes...",
                key="p04_obs",
            )

    st.markdown("---")

    # ==================================================================
    # BOTONES DE ACCIÓN
    # ==================================================================
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        # Verificar si todos los campos obligatorios están listos
        listo_para_ia = (
            motivo_cat is not None and
            nivel_conciencia is not None
        )

        if not listo_para_ia:
            st.caption("⚠️ Complete Motivo de Consulta y Nivel de Conciencia para habilitar.")

        if st.button(
            "🧠 Guardar y Ejecutar IA",
            type="primary",
            width='stretch',
            disabled=not listo_para_ia,
        ):
            try:
                # Guardar evaluación clínica
                triage_svc.save_clinical_evaluation(
                    id_triaje=id_triaje,
                    motivo_categoria=motivo_cat,
                    motivo_texto_libre=motivo_texto.strip() if motivo_texto else None,
                    escala_dolor=dolor,
                    glasgow=glasgow,
                    nivel_conciencia=nivel_conciencia,
                    diabetes=diabetes,
                    hipertension=hipertension,
                    enfermedad_renal=enf_renal,
                    embarazo=embarazo,
                    cancer=cancer,
                    cardiopatias=cardiopatias,
                    enfermedad_pulmonar=enf_pulmonar,
                    cirugias_recientes=cirugias,
                    medicacion_relevante=medicacion.strip() if medicacion else None,
                    alergias=alergias.strip() if alergias else None,
                    observaciones=observaciones.strip() if observaciones else None,
                    episodios_previos=episodios_previos,
                )

                # Transicionar a PendienteIA
                try:
                    triage_svc.transition_state(
                        id_triaje=id_triaje,
                        nuevo_estado="PendienteIA",
                        usuario=st.session_state.user.get("nombre_usuario", "Sistema"),
                    )
                except ValueError:
                    pass

                st.success("✅ Evaluación clínica guardada correctamente.")

                # Placeholder: La IA se ejecutará en Épica 4
                st.info(
                    "🧠 **Motor de IA:** La inferencia se ejecutará cuando el modelo esté "
                    "disponible (Épica 4). Por ahora, puede continuar con la validación manual."
                )

                st.session_state.page = "clasificacion_ia"
                st.rerun()

            except ValueError as ve:
                st.error(f"❌ {ve}")

    # Botones secundarios
    col_back1, col_back2, _ = st.columns([1, 1, 2])
    with col_back1:
        if st.button("⬅️ Volver a Signos Vitales", width='stretch'):
            st.session_state.page = "signos_vitales"
            st.rerun()
    with col_back2:
        # Permitir saltar directamente a validación (modo demo sin IA)
        if st.button("⏭️ Saltar a Validación (sin IA)", width='stretch'):
            try:
                triage_svc.save_clinical_evaluation(
                    id_triaje=id_triaje,
                    motivo_categoria=motivo_cat,
                    motivo_texto_libre=motivo_texto.strip() if motivo_texto else None,
                    escala_dolor=dolor,
                    glasgow=glasgow,
                    nivel_conciencia=nivel_conciencia,
                    diabetes=diabetes,
                    hipertension=hipertension,
                    enfermedad_renal=enf_renal,
                    embarazo=embarazo,
                    cancer=cancer,
                    cardiopatias=cardiopatias,
                    enfermedad_pulmonar=enf_pulmonar,
                    cirugias_recientes=cirugias,
                    medicacion_relevante=medicacion.strip() if medicacion else None,
                    alergias=alergias.strip() if alergias else None,
                    observaciones=observaciones.strip() if observaciones else None,
                    episodios_previos=episodios_previos,
                )
                triage_svc.transition_state(
                    id_triaje=id_triaje,
                    nuevo_estado="PendienteIA",
                    usuario=st.session_state.user.get("nombre_usuario", "Sistema"),
                )
                st.session_state.page = "validacion_triaje"
                st.rerun()
            except ValueError as ve:
                st.error(f"❌ {ve}")


# ======================================================================
# UTILIDADES
# ======================================================================

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
