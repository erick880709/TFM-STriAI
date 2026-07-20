"""
Pantalla de Captura de Signos Vitales (P03).
Mockup: resources/diseno/mockups/p03-signos-vitales.md
Cubre: HU-E2-04 (Captura de 8 signos vitales).
"""
import streamlit as st

from app.services.triage_service import TriageService, RANGOS_VITALES, ALERTAS_VITALES
from app.services.patient_service import PatientService, SEXO_LABELS


def render_vital_signs():
    """Renderiza la pantalla P03 — Captura de Signos Vitales."""

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
    # Verificar triaje activo
    # ------------------------------------------------------------------
    id_triaje = st.session_state.get("triaje_activo")
    if not id_triaje:
        st.warning("⚠️ No hay un evento de triaje activo. Registre un paciente primero.")
        if st.button("📝 Ir a Registro de Paciente"):
            st.session_state.page = "registro_paciente"
            st.rerun()
        return

    triaje = triage_svc.get_triage_event(id_triaje)
    if not triaje:
        st.error("❌ El evento de triaje no fue encontrado.")
        return

    # ------------------------------------------------------------------
    # Cabecera con info del paciente (ampliado Épica 7)
    # ------------------------------------------------------------------
    st.title("💓 Captura de Signos Vitales")

    # Construir línea de identificación del paciente
    nombre_pac = f"{triaje.get('nombres', '')} {triaje.get('apellidos', '')}".strip()
    doc_info = f"{triaje.get('tipo_documento', '')} {triaje.get('numero_documento', '')}".strip()
    if nombre_pac:
        st.caption(f"Paso 2 de 7 · Paciente: **{nombre_pac}** ({doc_info})")
    else:
        st.caption(f"Paso 2 de 7 · Paciente: {doc_info}")

    _render_flow_indicator(2)

    # Datos del paciente en badge
    with st.container(border=True):
        cols = st.columns(4)
        with cols[0]:
            st.metric("Edad", f"{triaje.get('edad_paciente', '—')} años")
        with cols[1]:
            st.metric("Sexo", SEXO_LABELS.get(triaje.get('sexo', ''), '—'))
        with cols[2]:
            st.metric("Vía Llegada", triaje.get('via_llegada', '—'))
        with cols[3]:
            st.metric("Episodios Previos", triaje.get('episodios_previos_urgencias', 0))

    # Cargar signos existentes si los hay
    signos_existentes = triage_svc.get_vital_signs(id_triaje)

    st.markdown("---")

    # ==================================================================
    # FORMULARIO DE SIGNOS VITALES
    # ==================================================================

    # Tarjeta de Prioridad Alta (SpO₂ + FR) — variables de alto peso predictivo
    st.markdown("### 🔴 Signos de Prioridad Alta (Alto Peso Predictivo)")

    with st.container(border=True):
        col_a, col_b = st.columns(2)

        with col_a:
            spo2 = st.number_input(
                "Saturación de O₂ (%) *",
                min_value=0, max_value=100, step=1,
                value=signos_existentes.get("saturacion_o2") if signos_existentes else None,
                key="p03_spo2",
                help="Rango normal: ≥ 90%. Valor crítico: < 90%.",
            )
            # Alerta visual si SpO₂ es crítica
            if spo2 is not None and spo2 < 90:
                st.error("⚠️ **SpO₂ CRÍTICA** — Posible hipoxemia (< 90%)")

            fr = st.number_input(
                "Frecuencia Respiratoria (rpm) *",
                min_value=0, max_value=60, step=1,
                value=signos_existentes.get("frecuencia_respiratoria") if signos_existentes else None,
                key="p03_fr",
                help="Rango normal: 12-20 rpm. Elevada: > 25 rpm.",
            )
            if fr is not None and fr > 25:
                st.error("⚠️ **FR ELEVADA** — Posible dificultad respiratoria (> 25 rpm)")

        with col_b:
            fc = st.number_input(
                "Frecuencia Cardíaca (lpm) *",
                min_value=0, max_value=300, step=1,
                value=signos_existentes.get("frecuencia_cardiaca") if signos_existentes else None,
                key="p03_fc",
                help="Rango normal: 60-100 lpm. Taquicardia: > 120 lpm.",
            )
            if fc is not None and fc > 120:
                st.warning("⚠️ Taquicardia (> 120 lpm)")

            temp = st.number_input(
                "Temperatura (°C) *",
                min_value=30.0, max_value=45.0, step=0.1,
                value=signos_existentes.get("temperatura") if signos_existentes else None,
                key="p03_temp",
                help="Rango: 30-45°C. Hipotermia: < 35°C. Hipertermia: > 41°C.",
            )
            if temp is not None:
                if temp < 35:
                    st.error("⚠️ **HIPOTERMIA** (< 35°C)")
                elif temp > 41:
                    st.error("⚠️ **HIPERTERMIA** (> 41°C)")

    st.markdown("---")

    # Resto de signos vitales
    st.markdown("### Resto de Signos Vitales")

    with st.container(border=True):
        col_c, col_d = st.columns(2)

        with col_c:
            pa_sis = st.number_input(
                "Presión Sistólica (mmHg) *",
                min_value=0, max_value=300, step=1,
                value=signos_existentes.get("presion_sistolica") if signos_existentes else None,
                key="p03_pa_sis",
                help="Rango normal: 90-140 mmHg.",
            )
            if pa_sis is not None:
                if pa_sis < 90:
                    st.warning("⚠️ Hipotensión (< 90 mmHg)")
                elif pa_sis > 180:
                    st.error("⚠️ **Crisis hipertensiva** (> 180 mmHg)")

            pa_dia = st.number_input(
                "Presión Diastólica (mmHg) *",
                min_value=0, max_value=200, step=1,
                value=signos_existentes.get("presion_diastolica") if signos_existentes else None,
                key="p03_pa_dia",
                help="Rango normal: 60-90 mmHg.",
            )

            # Validar PA: sistólica > diastólica
            if pa_sis is not None and pa_dia is not None and pa_sis <= pa_dia:
                st.warning("⚠️ PA sistólica debe ser mayor que diastólica.")

        with col_d:
            peso = st.number_input(
                "Peso (kg)",
                min_value=0.5, max_value=500.0, step=0.1,
                value=signos_existentes.get("peso") if signos_existentes else None,
                key="p03_peso",
            )
            talla = st.number_input(
                "Talla (cm)",
                min_value=20.0, max_value=250.0, step=0.1,
                value=signos_existentes.get("talla") if signos_existentes else None,
                key="p03_talla",
            )

            # Calcular IMC automáticamente
            if peso and talla and talla > 0:
                talla_m = talla / 100.0
                imc = round(peso / (talla_m ** 2), 1)
                imc_color = _imc_color(imc)
                st.markdown(f"### IMC: :{imc_color}[{imc}] kg/m²")
                st.caption(_imc_label(imc))
            elif signos_existentes and signos_existentes.get("imc"):
                st.caption(f"IMC registrado: **{signos_existentes['imc']}** kg/m²")

    st.markdown("---")

    # ==================================================================
    # BOTONES DE ACCIÓN
    # ==================================================================
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("💾 Guardar y Continuar a Evaluación Clínica",
                    type="primary", use_container_width=True):
            # Validar campos obligatorios
            errores = _validar_obligatorios(spo2, fr, fc, temp, pa_sis, pa_dia)
            if errores:
                for e in errores:
                    st.error(f"❌ {e}")
            else:
                try:
                    # Guardar signos vitales
                    signos, alertas = triage_svc.save_vital_signs(
                        id_triaje=id_triaje,
                        temperatura=temp,
                        frecuencia_cardiaca=int(fc) if fc else None,
                        frecuencia_respiratoria=int(fr) if fr else None,
                        saturacion_o2=int(spo2) if spo2 else None,
                        presion_sistolica=int(pa_sis) if pa_sis else None,
                        presion_diastolica=int(pa_dia) if pa_dia else None,
                        peso=peso,
                        talla=talla,
                    )

                    # Mostrar alertas si las hay
                    alertas_error = [a for a in alertas if a["tipo"] == "error"]
                    alertas_criticas = [a for a in alertas if a["tipo"] == "critico"]

                    if alertas_error:
                        st.error("❌ Se encontraron valores fuera de rango fisiológico:")
                        for a in alertas_error:
                            st.error(f"• {a['mensaje']}")

                    if alertas_criticas and not alertas_error:
                        st.warning("⚠️ **Alertas clínicas detectadas:**")
                        for a in alertas_criticas:
                            st.warning(f"• {a['mensaje']}")

                    if not alertas_error:
                        # Transicionar estado a EnEvaluacion
                        try:
                            triage_svc.transition_state(
                                id_triaje=id_triaje,
                                nuevo_estado="EnEvaluacion",
                                usuario=st.session_state.user.get("nombre_usuario", "Sistema"),
                            )
                        except ValueError:
                            pass  # Puede que ya esté en ese estado

                        st.success("✅ Signos vitales guardados correctamente.")
                        st.info("⏩ Redirigiendo a Evaluación Clínica...")
                        st.session_state.page = "evaluacion_clinica"
                        st.rerun()

                except ValueError as ve:
                    st.error(f"❌ {ve}")

    # Botón para volver
    if st.button("⬅️ Volver a Registro de Paciente", use_container_width=True):
        st.session_state.page = "registro_paciente"
        st.rerun()


# ======================================================================
# UTILIDADES
# ======================================================================

def _validar_obligatorios(spo2, fr, fc, temp, pa_sis, pa_dia) -> list:
    """Valida que los 6 signos vitales obligatorios estén presentes."""
    errores = []
    campos = {
        "Saturación O₂": spo2,
        "Frecuencia Respiratoria": fr,
        "Frecuencia Cardíaca": fc,
        "Temperatura": temp,
        "Presión Sistólica": pa_sis,
        "Presión Diastólica": pa_dia,
    }
    for nombre, valor in campos.items():
        if valor is None:
            errores.append(f"{nombre} es obligatorio.")
    return errores


def _imc_color(imc: float) -> str:
    """Retorna color según rango de IMC."""
    if imc < 18.5:
        return "orange"
    elif imc < 25:
        return "green"
    elif imc < 30:
        return "orange"
    else:
        return "red"


def _imc_label(imc: float) -> str:
    """Retorna etiqueta según IMC."""
    if imc < 18.5:
        return "Bajo peso"
    elif imc < 25:
        return "Peso normal"
    elif imc < 30:
        return "Sobrepeso"
    else:
        return "Obesidad"


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
