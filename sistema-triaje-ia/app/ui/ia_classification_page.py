"""
Pantalla de Clasificación IA (P05) + Explicación SHAP (P06).
Mockups: resources/diseno/mockups/p05-clasificacion-ia.md,
         resources/diseno/mockups/p06-explicacion-shap.md
Cubre: HU-E4-01 (Inferencia), HU-E4-02 (SHAP), HU-E4-03 (Validación).
"""
import streamlit as st
import time
import json

from app.services.inference_service import InferenceService, get_inference_service
from app.services.triage_service import TriageService, NIVELES_TRIAGE, NIVELES_LABELS
from app.services.patient_service import PatientService

# Colores de niveles de triaje (Resolución 5596/2015)
NIVEL_COLORS = {
    "I": "#DC2626",   # Rojo — Atención Inmediata
    "II": "#EA580C",  # Naranja — Emergencia
    "III": "#F59E0B", # Amarillo — Urgencia
    "IV": "#059669",  # Verde — Urgencia Menor
    "V": "#0891B2",   # Azul — Consulta General
}

NIVEL_ICONS = {"I": "🔴", "II": "🟠", "III": "🟡", "IV": "🟢", "V": "🔵"}


def render_ia_classification():
    """Renderiza la pantalla P05/P06 — Clasificación IA y Explicación SHAP."""

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

    # Inicializar servicio de inferencia (singleton)
    if "inference_service" not in st.session_state:
        with st.spinner("🔧 Inicializando motor de IA..."):
            st.session_state.inference_service = get_inference_service()

    inference_svc: InferenceService = st.session_state.inference_service

    # ------------------------------------------------------------------
    # Verificar triaje activo
    # ------------------------------------------------------------------
    id_triaje = st.session_state.get("triaje_activo")
    if not id_triaje:
        st.warning("⚠️ No hay un evento de triaje activo.")
        if st.button("📝 Ir a Registro de Paciente"):
            st.session_state.page = "registro_paciente"
            st.rerun()
        return

    triaje = triage_svc.get_triage_event(id_triaje)
    if not triaje:
        st.error("❌ Evento de triaje no encontrado.")
        return

    # ------------------------------------------------------------------
    # Cabecera
    # ------------------------------------------------------------------
    st.title("🧠 Resultado de Clasificación IA")
    
    # Buscador de paciente por documento
    with st.expander("🔍 Buscar Paciente por Documento", expanded=False):
        doc_search = st.text_input("Número de Documento", placeholder="Ingrese número de identificación", key="p05_search_doc")
        if doc_search and st.button("🔍 Buscar", key="p05_search_btn"):
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
                            if st.button("📋 Cargar", key=f"p05load_{p['id_paciente'][:8]}", use_container_width=True):
                                st.session_state.triaje_activo = activo['id_triaje']
                                st.rerun()
            else:
                st.info("No se encontraron pacientes.")
    
    status = inference_svc.get_status()
    st.caption(
        f"Paso 4 de 7 · Modelo: {status['nombre_modelo']} v{status['version']}"
    )

    _render_flow_indicator(4)

    # Verificar si el modelo está disponible
    if not status["modelo_cargado"]:
        _render_degraded_mode(status, triage_svc, id_triaje)
        return

    # ------------------------------------------------------------------
    # Ejecutar inferencia (o recuperar de caché de sesión)
    # ------------------------------------------------------------------
    prediction_key = f"prediction_{id_triaje}"

    if prediction_key not in st.session_state:
        with st.spinner("🧠 Ejecutando modelo de IA..."):

            # Construir datos clínicos para inferencia
            clinical_data = {
                "edad": triaje.get("edad_paciente"),
                "sexo": triaje.get("sexo"),
                "temperatura": triaje.get("temperatura"),
                "frecuencia_cardiaca": triaje.get("frecuencia_cardiaca"),
                "frecuencia_respiratoria": triaje.get("frecuencia_respiratoria"),
                "saturacion_o2": triaje.get("saturacion_o2"),
                "presion_sistolica": triaje.get("presion_sistolica"),
                "presion_diastolica": triaje.get("presion_diastolica"),
                "peso": triaje.get("peso"),
                "talla": triaje.get("talla"),
                "imc": triaje.get("imc"),
                "glasgow": triaje.get("glasgow"),
                "escala_dolor": triaje.get("escala_dolor"),
                "nivel_conciencia": triaje.get("nivel_conciencia"),
                "via_llegada": triaje.get("via_llegada"),
                "motivo_categoria": triaje.get("motivo_categoria"),
                "diabetes": triaje.get("diabetes"),
                "hipertension": triaje.get("hipertension"),
                "enfermedad_renal": triaje.get("enfermedad_renal"),
                "embarazo": triaje.get("embarazo"),
                "cancer": triaje.get("cancer"),
                "cardiopatias": triaje.get("cardiopatias"),
                "enfermedad_pulmonar": triaje.get("enfermedad_pulmonar"),
                "cirugias_recientes": triaje.get("cirugias_recientes"),
                "episodios_previos": triaje.get("episodios_previos_urgencias"),
            }
            motivo_texto = triaje.get("motivo_texto_libre") or ""

            # Ejecutar predicción
            prediction = inference_svc.predict(clinical_data, motivo_texto)

            # Guardar en sesión
            st.session_state[prediction_key] = prediction

            # Si fue exitosa, guardar en BD
            if prediction.get("nivel_sugerido") and not prediction.get("error"):
                _save_prediction_to_db(prediction, id_triaje, db_path)

            # Transicionar estado
            try:
                triage_svc.transition_state(
                    id_triaje=id_triaje,
                    nuevo_estado="Clasificado",
                    usuario=st.session_state.user.get("nombre_usuario", "Sistema"),
                )
            except ValueError:
                pass

        st.rerun()

    prediction = st.session_state[prediction_key]

    # ------------------------------------------------------------------
    # Mostrar error si lo hay
    # ------------------------------------------------------------------
    if prediction.get("error"):
        st.error(f"❌ {prediction['error']}")
        _render_degraded_mode(status, triage_svc, id_triaje)
        return

    # ==================================================================
    # RESULTADOS: Layout de 3 columnas
    # ==================================================================
    nivel_ia = prediction["nivel_sugerido"]
    probs = prediction["probabilidades"]
    confianza = prediction["confianza"]
    tiempo = prediction["tiempo_inferencia_s"]

    col_nivel, col_probs, col_prof = st.columns([1, 1, 1])

    # --- COLUMNA 1: NIVEL SUGERIDO ---
    with col_nivel:
        with st.container(border=True):
            st.markdown("##### 🤖 Nivel Sugerido por IA")
            color = NIVEL_COLORS.get(nivel_ia, "#64748B")
            icon = NIVEL_ICONS.get(nivel_ia, "")
            st.markdown(
                f"<div style='text-align:center; font-size:48px; font-weight:700; "
                f"color:{color};'>{icon} {nivel_ia}</div>",
                unsafe_allow_html=True,
            )
            label = NIVELES_LABELS.get(nivel_ia, "")
            st.markdown(
                f"<div style='text-align:center; font-size:14px; color:{color}; "
                f"font-weight:600;'>{label}</div>",
                unsafe_allow_html=True,
            )
            st.markdown("---")
            st.metric("Confianza", f"{confianza:.0%}")
            st.metric("Tiempo", f"{tiempo:.2f}s")

    # --- COLUMNA 2: PROBABILIDADES ---
    with col_probs:
        with st.container(border=True):
            st.markdown("##### 📊 Probabilidades por Nivel")
            for nivel in ["I", "II", "III", "IV", "V"]:
                prob = probs.get(nivel, 0)
                color = NIVEL_COLORS.get(nivel, "#64748B")
                icon = NIVEL_ICONS.get(nivel, "")
                st.markdown(
                    f"{icon} **Nivel {nivel}:** "
                    f"<span style='color:{color}; font-weight:600;'>{prob:.1%}</span>",
                    unsafe_allow_html=True,
                )
                # Barra de progreso
                st.progress(min(prob, 1.0),
                           text=f"{prob:.0%}" if prob > 0.05 else "")

    # --- COLUMNA 3: CLASIFICACIÓN DEL PROFESIONAL (HU-E4-03) ---
    with col_prof:
        with st.container(border=True):
            st.markdown("##### 👨‍⚕️ Su Clasificación")
            st.caption(
                "Registre su clasificación independiente. "
                "No se autocompleta con la sugerencia de la IA."
            )

            nivel_profesional = st.selectbox(
                "Nivel asignado *",
                options=NIVELES_TRIAGE,
                format_func=lambda x: f"{NIVEL_ICONS.get(x, '')} Nivel {x} — {NIVELES_LABELS.get(x, '')}",
                key="p05_nivel_prof",
            )

            # Mostrar concordancia
            if nivel_profesional:
                if nivel_profesional == nivel_ia:
                    st.success(f"✅ **CONCORDANCIA:** Ambos coinciden en Nivel {nivel_ia}")
                else:
                    st.error(
                        f"⚠️ **DISCREPANCIA:** IA sugiere Nivel {nivel_ia}, "
                        f"usted asigna Nivel {nivel_profesional}"
                    )
                    st.text_area(
                        "Motivo de Discrepancia *",
                        placeholder="Explique por qué difiere...",
                        key="p05_motivo_disc",
                        height=80,
                    )

    st.markdown("---")

    # ==================================================================
    # EXPLICACIÓN SHAP (HU-E4-02)
    # ==================================================================
    st.markdown("### 🔍 Explicación SHAP — ¿Por qué este nivel?")

    # Generar SHAP (cacheado en sesión)
    shap_key = f"shap_{id_triaje}"
    if shap_key not in st.session_state:
        with st.spinner("🔬 Generando explicación SHAP..."):
            clinical_data_shap = {
                "edad": triaje.get("edad_paciente"),
                "sexo": triaje.get("sexo"),
                "temperatura": triaje.get("temperatura"),
                "frecuencia_cardiaca": triaje.get("frecuencia_cardiaca"),
                "frecuencia_respiratoria": triaje.get("frecuencia_respiratoria"),
                "saturacion_o2": triaje.get("saturacion_o2"),
                "presion_sistolica": triaje.get("presion_sistolica"),
                "presion_diastolica": triaje.get("presion_diastolica"),
                "glasgow": triaje.get("glasgow"),
                "escala_dolor": triaje.get("escala_dolor"),
            }
            shap_result = inference_svc.explain(
                clinical_data_shap,
                triaje.get("motivo_texto_libre"),
            )
            st.session_state[shap_key] = shap_result
        st.rerun()

    shap_result = st.session_state[shap_key]

    if shap_result.get("error"):
        st.warning(f"⚠️ {shap_result['error']}")
        # Mostrar fallback
        if "top_features_fallback" in shap_result:
            _render_fallback_importance(shap_result["top_features_fallback"])
    else:
        # Top variables SHAP
        _render_shap_explanation(shap_result, nivel_ia)

    # Comparación MTS
    if "mts_comparison" in shap_result:
        mts = shap_result["mts_comparison"]
        if mts.get("coincidencias"):
            with st.expander("📋 Comparación con criterios MTS/Manchester"):
                st.caption(f"**{mts['total']} coincidencia(s)** con criterios MTS:")
                for c in mts["coincidencias"]:
                    st.markdown(f"- {c}")

    st.markdown("---")

    # ==================================================================
    # BOTONES DE ACCIÓN
    # ==================================================================
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

    with col_btn1:
        if st.button("⬅️ Volver a Evaluación", use_container_width=True):
            st.session_state.page = "evaluacion_clinica"
            st.rerun()

    with col_btn2:
        # Re-ejecutar inferencia
        if st.button("🔄 Re-ejecutar IA", use_container_width=True):
            st.session_state.pop(prediction_key, None)
            st.session_state.pop(shap_key, None)
            st.rerun()

    with col_btn3:
        puede_continuar = nivel_profesional is not None
        discrepancia = nivel_ia != nivel_profesional if nivel_profesional else False
        motivo_ok = True
        if discrepancia:
            motivo_disc = st.session_state.get("p05_motivo_disc", "")
            motivo_ok = bool(motivo_disc and motivo_disc.strip())

        if st.button(
            "✅ Continuar a Validación →",
            type="primary",
            use_container_width=True,
            disabled=not puede_continuar or (discrepancia and not motivo_ok),
        ):
            # Guardar datos en sesión para la pantalla de validación
            st.session_state.ia_nivel = nivel_ia
            st.session_state.ia_confianza = confianza
            st.session_state.prof_nivel = nivel_profesional
            if discrepancia:
                st.session_state.motivo_discrepancia = st.session_state.get("p05_motivo_disc", "")

            # Actualizar EventoTriaje con nivel del profesional
            try:
                triage_svc.transition_state(
                    id_triaje=id_triaje,
                    nuevo_estado="Validado",
                    usuario=st.session_state.user.get("nombre_usuario", "Sistema"),
                )
            except ValueError:
                pass

            st.session_state.page = "validacion_triaje"
            st.rerun()

    if discrepancia and not motivo_ok:
        st.caption("⚠️ Debe registrar el motivo de discrepancia para continuar.")


# ======================================================================
# SUBCOMPONENTES
# ======================================================================

def _render_shap_explanation(shap_result: dict, nivel_predicho: str):
    """Renderiza la explicación SHAP en formato clínico (HU-E4-02)."""
    color = NIVEL_COLORS.get(nivel_predicho, "#EA580C")

    col_shap1, col_shap2 = st.columns([3, 2])

    with col_shap1:
        st.markdown("##### 📈 Contribución de Variables (Waterfall)")
        if "base_value" in shap_result:
            base = shap_result["base_value"]
            st.caption(f"Valor base: {base:.3f}")

        # Top contributors
        top = shap_result.get("top_contributors", [])[:8]
        if top:
            max_abs = max(abs(item.get("shap_value", 0)) for item in top) or 1
            for item in top:
                shap_val = item.get("shap_value", 0)
                nombre = item.get("nombre_clinico", item.get("feature", "?"))
                direction = item.get("direction", "neutro")

                # Normalizar ancho de barra
                bar_width = min(abs(shap_val) / max_abs, 1.0)
                bar_color = "#EA580C" if shap_val > 0 else "#0891B2" if shap_val < 0 else "#94A3B8"
                icon = "🟠" if shap_val > 0.01 else "🔵" if shap_val < -0.01 else "⚪"

                st.markdown(
                    f"{icon} **{nombre}** "
                    f"<span style='color:{bar_color}; font-weight:600;'>"
                    f"{shap_val:+.3f}</span>",
                    unsafe_allow_html=True,
                )
                st.progress(
                    bar_width,
                    text=f"{'⬆️ aumenta' if shap_val > 0 else '⬇️ disminuye' if shap_val < 0 else '➡️ neutro'}",
                )

    with col_shap2:
        if "top_features" in shap_result:
            st.markdown("##### 🏆 Top Variables por Importancia")
            top_features = shap_result.get("top_features", [])[:10]
            for i, feat in enumerate(top_features):
                nombre = feat.get("nombre_clinico", feat.get("feature", "?"))
                importance = feat.get("shap_importance", 0)
                st.markdown(
                    f"**{i+1}.** {nombre} — "
                    f"<span style='color:{color};'>{importance:.4f}</span>",
                    unsafe_allow_html=True,
                )


def _render_fallback_importance(alerts: list):
    """Fallback cuando SHAP no está disponible."""
    st.markdown("##### ⚠️ Importancia Clínica Estimada (SHAP no disponible)")
    st.caption("Basado en desviación de rangos fisiológicos normales:")
    for i, alert in enumerate(alerts[:8]):
        st.markdown(
            f"**{i+1}.** {alert.get('nombre_clinico', '?')}: "
            f"*{alert.get('mensaje', '')}* "
            f"(importancia: {alert.get('importancia_relativa', 0):.2f})"
        )


def _render_degraded_mode(status: dict, triage_svc: TriageService, id_triaje: str):
    """Modo degradado: modelo no disponible."""
    st.warning("⚠️ **Modo Degradado:** El modelo de IA no está disponible.")
    st.info(
        f"**Causa:** {status.get('error', 'Desconocida')}\n\n"
        "Puede continuar con la clasificación manual. "
        "Para habilitar la IA, ejecute el pipeline de entrenamiento:\n\n"
        "`python run_pipeline.py`"
    )

    st.markdown("---")
    st.markdown("### 📝 Clasificación Manual")

    nivel_manual = st.selectbox(
        "Nivel de Triaje asignado por el profesional *",
        options=NIVELES_TRIAGE,
        format_func=lambda x: f"{NIVEL_ICONS.get(x, '')} Nivel {x}",
        key="degraded_nivel",
    )

    if st.button("✅ Guardar y Continuar", type="primary"):
        if nivel_manual:
            st.session_state.ia_nivel = None
            st.session_state.prof_nivel = nivel_manual
            try:
                triage_svc.transition_state(
                    id_triaje=id_triaje,
                    nuevo_estado="Validado",
                    usuario=st.session_state.user.get("nombre_usuario", "Sistema"),
                )
            except ValueError:
                pass
            st.session_state.page = "validacion_triaje"
            st.rerun()


def _save_prediction_to_db(prediction: dict, id_triaje: str, db_path: str):
    """Guarda la predicción en la tabla PrediccionIA de la BD."""
    import uuid
    from app.data.database import get_connection

    try:
        conn = get_connection(db_path)
        id_pred = f"pred-{uuid.uuid4().hex[:12]}"
        conn.execute(
            """INSERT INTO PrediccionIA
               (IdPrediccion, IdTriaje, NivelPredicho, Probabilidades,
                Confianza, TiempoInferencia, FechaHora)
               VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
            (
                id_pred,
                id_triaje,
                prediction["nivel_sugerido"],
                json.dumps(prediction["probabilidades"]),
                prediction["confianza"],
                prediction["tiempo_inferencia_s"],
            ),
        )
        # Actualizar EventoTriaje
        conn.execute(
            """UPDATE EventoTriaje
               SET NivelSugeridoIA = ?, ProbabilidadesIA = ?,
                   VersionModeloUsado = ?, FechaHoraClasificacion = datetime('now')
               WHERE IdTriaje = ?""",
            (
                prediction["nivel_sugerido"],
                json.dumps(prediction["probabilidades"]),
                prediction.get("version_modelo", ""),
                id_triaje,
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        st.warning(f"⚠️ No se pudo guardar la predicción: {e}")


def _render_flow_indicator(paso_actual: int):
    """Indicador visual del paso actual en el flujo de triaje."""
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

