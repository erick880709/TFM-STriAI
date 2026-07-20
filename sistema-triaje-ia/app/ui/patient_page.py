"""
Pantalla de Registro de Paciente (P02).
Mockup: resources/diseno/mockups/p02-registro-paciente.md
Cubre: HU-E2-01 (Registro), HU-E2-02 (Búsqueda), HU-E2-03 (Historial).
HU-E8-06: Bloqueo de triaje activo.
"""
import streamlit as st

from app.services.patient_service import (
    PatientService, DuplicatePatientError,
    TIPOS_DOCUMENTO, TIPOS_DOC_LABELS, VIAS_LLEGADA,
    REGIMENES_SALUD, SEXOS, SEXO_LABELS,
    DEPARTAMENTOS_COLOMBIA, CIUDADES_POR_DEPARTAMENTO,
)
from app.services.triage_service import TriageService, NIVELES_LABELS


def _verificar_triaje_activo(triage_svc: TriageService, id_paciente: str):
    """
    Verifica si el paciente tiene un triaje activo (no cerrado ni cancelado).
    Retorna (bloqueado: bool, triaje_activo: dict | None).
    """
    activo = triage_svc.get_active_triage_for_patient(id_paciente)
    if activo:
        return True, activo
    return False, None


def render_patient_registration():
    """Renderiza la pantalla P02 — Registro de Paciente con búsqueda e historial."""

    # ------------------------------------------------------------------
    # Inicialización de servicios
    # ------------------------------------------------------------------
    db_path = st.session_state.db_path
    if "patient_service" not in st.session_state:
        st.session_state.patient_service = PatientService(db_path)
    if "triage_service" not in st.session_state:
        st.session_state.triage_service = TriageService(db_path)

    patient_svc: PatientService = st.session_state.patient_service
    triage_svc: TriageService = st.session_state.triage_service

    # ------------------------------------------------------------------
    # Cabecera
    # ------------------------------------------------------------------
    st.title("📝 Registro de Paciente")
    st.caption("Paso 1 de 7 · Flujo de Triaje")

    # Indicador de paso activo en el flujo
    _render_flow_indicator(1)

    # ------------------------------------------------------------------
    # Pestañas: Nuevo Paciente | Buscar Paciente
    # ------------------------------------------------------------------
    tab_nuevo, tab_buscar = st.tabs(["🆕 Nuevo Paciente", "🔍 Buscar Paciente"])

    # ==================================================================
    # TAB 1: NUEVO PACIENTE (HU-E2-01)
    # ==================================================================
    with tab_nuevo:
        _render_new_patient_form(patient_svc, triage_svc)

    # ==================================================================
    # TAB 2: BUSCAR PACIENTE (HU-E2-02 + HU-E2-03)
    # ==================================================================
    with tab_buscar:
        _render_patient_search(patient_svc, triage_svc)


# ======================================================================
# FORMULARIO NUEVO PACIENTE (HU-E2-01)
# ======================================================================

def _render_new_patient_form(patient_svc: PatientService, triage_svc: TriageService):
    """Formulario de registro de nuevo paciente (HU-E2-01, ampliado Épica 7)."""

    with st.container(border=True):
        # ================================================================
        # SECCIÓN 1: DATOS PERSONALES
        # ================================================================
        st.subheader("👤 Datos Personales")

        col1, col2 = st.columns(2)
        with col1:
            tipo_doc = st.selectbox(
                "Tipo Documento *",
                options=TIPOS_DOCUMENTO,
                format_func=lambda x: TIPOS_DOC_LABELS.get(x, x),
                key="p02_tipo_doc",
            )
            num_doc = st.text_input(
                "Número de Documento *",
                placeholder="Ingrese sin puntos ni guiones",
                key="p02_num_doc",
            )
            nombres = st.text_input(
                "Nombres",
                placeholder="Ej: Juan Carlos",
                key="p02_nombres",
                help="Nombres completos del paciente.",
            )
            apellidos = st.text_input(
                "Apellidos",
                placeholder="Ej: García López",
                key="p02_apellidos",
                help="Apellidos completos del paciente.",
            )

        with col2:
            fecha_nac = st.text_input(
                "Fecha de Nacimiento *",
                placeholder="YYYY-MM-DD",
                key="p02_fecha_nac",
                help="Formato: AAAA-MM-DD. Ej: 1985-03-15",
            )
            sexo = st.selectbox(
                "Sexo *",
                options=SEXOS,
                format_func=lambda x: SEXO_LABELS.get(x, x),
                key="p02_sexo",
            )
            # Mostrar edad calculada si hay fecha válida
            if fecha_nac:
                try:
                    edad_calc = PatientService._calcular_edad(fecha_nac)
                    if 0 <= edad_calc <= 120:
                        st.caption(f"🎂 Edad calculada: **{edad_calc} años**")
                except (ValueError, TypeError):
                    pass

        st.markdown("---")

        # ================================================================
        # SECCIÓN 2: CONTACTO
        # ================================================================
        st.subheader("📞 Información de Contacto")

        col_tel, col_correo = st.columns(2)
        with col_tel:
            telefono = st.text_input(
                "Teléfono",
                placeholder="Ej: 3101234567",
                key="p02_telefono",
                help="Número de contacto (mín. 10 dígitos).",
            )
        with col_correo:
            correo = st.text_input(
                "Correo Electrónico",
                placeholder="Ej: paciente@correo.com",
                key="p02_correo",
                help="Dirección de correo electrónico.",
            )

        st.markdown("---")

        # ================================================================
        # SECCIÓN 3: CONTACTO DE EMERGENCIA
        # ================================================================
        st.subheader("🆘 Contacto de Emergencia")

        col_emerg_name, col_emerg_tel = st.columns(2)
        with col_emerg_name:
            contacto_emergencia = st.text_input(
                "Nombre del Contacto",
                placeholder="Ej: María García (familiar)",
                key="p02_contacto_emergencia",
                help="Nombre y parentesco del contacto de emergencia.",
            )
        with col_emerg_tel:
            numero_contacto_emergencia = st.text_input(
                "Teléfono del Contacto",
                placeholder="Ej: 3119876543",
                key="p02_num_contacto_emergencia",
                help="Número del contacto de emergencia (mín. 10 dígitos).",
            )

        st.markdown("---")

        # ================================================================
        # SECCIÓN 4: RESIDENCIA (Épica 7 — geografía colombiana)
        # ================================================================
        st.subheader("🏠 Lugar de Residencia")

        col_depto, col_ciudad = st.columns(2)
        with col_depto:
            departamento = st.selectbox(
                "Departamento",
                options=[""] + DEPARTAMENTOS_COLOMBIA,
                key="p02_departamento",
                help="Departamento de residencia.",
            )
        with col_ciudad:
            # Ciudad dependiente del departamento seleccionado
            ciudades_disponibles = (
                CIUDADES_POR_DEPARTAMENTO.get(departamento, [])
                if departamento else []
            )
            ciudad = st.selectbox(
                "Ciudad",
                options=[""] + ciudades_disponibles,
                key="p02_ciudad",
                help="Ciudad de residencia.",
                disabled=not departamento,
            )

        direccion_residencia = st.text_input(
            "Dirección de Residencia",
            placeholder="Ej: Calle 100 # 15-20, Barrio El Poblado",
            key="p02_direccion",
            help="Dirección completa del domicilio.",
        )

        st.markdown("---")

        # ================================================================
        # SECCIÓN 5: DATOS CLÍNICOS
        # ================================================================
        st.subheader("🏥 Datos Clínicos de Ingreso")

        col_clin1, col_clin2 = st.columns(2)
        with col_clin1:
            via_llegada = st.selectbox(
                "Vía de Llegada * ⚠ Variable predictiva",
                options=VIAS_LLEGADA,
                key="p02_via_llegada",
            )
            regimen = st.selectbox(
                "Régimen de Salud",
                options=[""] + REGIMENES_SALUD,
                key="p02_regimen",
            )
        with col_clin2:
            eps = st.text_input("EPS", placeholder="Nombre de la EPS", key="p02_eps")
            episodios = st.number_input(
                "Episodios Previos en Urgencias ⚠ Variable predictiva",
                min_value=0, max_value=99, value=0, step=1,
                key="p02_episodios",
                help="Número de visitas a urgencias en los últimos 12 meses.",
            )

        st.markdown("---")

        # ================================================================
        # BOTÓN DE REGISTRO
        # ================================================================
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("Registrar Paciente y Crear Triaje", type="primary",
                         use_container_width=True, key="p02_btn_register"):
                errores = []

                # Validaciones básicas
                if not num_doc or not num_doc.strip():
                    errores.append("Número de documento es obligatorio.")
                if not fecha_nac:
                    errores.append("Fecha de nacimiento es obligatoria.")
                if num_doc and fecha_nac:
                    try:
                        edad_v = PatientService._calcular_edad(fecha_nac)
                        if edad_v < 0 or edad_v > 120:
                            errores.append(f"Edad fuera de rango ({edad_v} años).")
                    except (ValueError, TypeError):
                        errores.append("Fecha de nacimiento inválida. Use YYYY-MM-DD.")

                # Validaciones Épica 7
                if telefono:
                    digitos_tel = ''.join(c for c in telefono if c.isdigit())
                    if len(digitos_tel) < 10:
                        errores.append("El teléfono debe tener al menos 10 dígitos.")
                if correo and ("@" not in correo or "." not in correo.split("@")[-1]):
                    errores.append("Formato de correo electrónico inválido.")
                if numero_contacto_emergencia:
                    digitos_ce = ''.join(c for c in numero_contacto_emergencia if c.isdigit())
                    if len(digitos_ce) < 10:
                        errores.append("El teléfono del contacto de emergencia debe tener al menos 10 dígitos.")
                if ciudad and departamento and ciudad not in CIUDADES_POR_DEPARTAMENTO.get(departamento, []):
                    errores.append(f"La ciudad '{ciudad}' no pertenece al departamento '{departamento}'.")

                if errores:
                    for e in errores:
                        st.error(f"❌ {e}")
                else:
                    try:
                        # 1. Registrar paciente con todos los campos ampliados
                        paciente = patient_svc.register_patient(
                            tipo_documento=tipo_doc,
                            numero_documento=num_doc.strip(),
                            fecha_nacimiento=fecha_nac.strip(),
                            sexo=sexo,
                            via_llegada=via_llegada,
                            regimen_salud=regimen if regimen else None,
                            eps=eps.strip() if eps else None,
                            episodios_previos=episodios,
                            nombres=nombres.strip(),
                            apellidos=apellidos.strip(),
                            telefono=telefono.strip(),
                            correo=correo.strip() if correo and correo.strip() else None,
                            contacto_emergencia=contacto_emergencia.strip(),
                            numero_contacto_emergencia=numero_contacto_emergencia.strip(),
                            departamento=departamento,
                            ciudad=ciudad,
                            direccion_residencia=direccion_residencia.strip(),
                        )
                        # Mostrar nombre completo si está disponible
                        nombre_mostrar = (
                            f"{paciente.get('nombres','')} {paciente.get('apellidos','')}".strip()
                            or paciente['numero_documento']
                        )
                        st.success(
                            f"✅ Paciente registrado: **{nombre_mostrar}** "
                            f"({paciente['edad']} años, {SEXO_LABELS.get(paciente['sexo'], paciente['sexo'])})"
                        )

                        # 2. Verificar triaje activo (HU-E8-06)
                        bloqueado, triaje_activo = _verificar_triaje_activo(
                            triage_svc, paciente["id_paciente"]
                        )
                        if bloqueado:
                            st.warning(
                                f"⚠️ Este paciente ya tiene un triaje en curso "
                                f"(Estado: **{triaje_activo.get('estado', 'N/A')}** — "
                                f"`{triaje_activo.get('id_triaje', '')}`). "
                                f"Debe cerrarlo o cancelarlo antes de crear uno nuevo."
                            )
                            st.stop()

                        # 3. Crear evento de triaje asociado
                        usuario = st.session_state.user.get("nombre_usuario", "Sistema")
                        triaje = triage_svc.create_triage_event(
                            id_paciente=paciente["id_paciente"],
                            profesional_responsable=usuario,
                        )
                        st.success(
                            f"📋 Evento de triaje creado: `{triaje['id_triaje']}` "
                            f"— Estado: **Registrado**"
                        )

                        # Guardar en sesión y navegar a Signos Vitales
                        st.session_state.triaje_activo = triaje["id_triaje"]
                        st.session_state.paciente_activo = paciente["id_paciente"]

                        st.info("⏩ Redirigiendo a Captura de Signos Vitales...")
                        st.session_state.page = "signos_vitales"
                        st.rerun()

                    except DuplicatePatientError as dup:
                        st.warning("⚠️ **Paciente ya registrado**")
                        existente = dup.paciente_existente

                        with st.container(border=True):
                            st.markdown("### 📂 Paciente Existente")
                            cols = st.columns(2)
                            with cols[0]:
                                st.markdown(
                                    f"**Documento:** {existente.get('numero_documento')}"
                                )
                                # Mostrar nombres si existen
                                nombres_ex = existente.get('nombres', '')
                                apellidos_ex = existente.get('apellidos', '')
                                nombre_ex = f"{nombres_ex} {apellidos_ex}".strip()
                                if nombre_ex:
                                    st.markdown(f"**Nombre:** {nombre_ex}")
                                st.markdown(
                                    f"**Registrado:** {existente.get('fecha_registro', 'N/A')[:10]}"
                                )
                            with cols[1]:
                                st.markdown(f"**Episodios previos:** {dup.total_episodios}")
                                if dup.ultimo_triaje:
                                    ult = dup.ultimo_triaje
                                    st.markdown(
                                        f"**Último triaje:** {ult.get('fecha_hora_ingreso', 'N/A')[:10]}"
                                    )
                                    st.markdown(f"**Estado:** `{ult.get('estado', 'N/A')}`")

                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("📋 Usar este paciente (nuevo triaje)",
                                            type="primary", use_container_width=True,
                                            key="dup_new_triage"):
                                    # Verificar triaje activo (HU-E8-06)
                                    bloqueado_d, ta_d = _verificar_triaje_activo(triage_svc, existente["id_paciente"])
                                    if bloqueado_d:
                                        st.warning(f"⚠️ Triaje en curso: `{ta_d.get('id_triaje','')}` (Estado: {ta_d.get('estado','')}). Ciérrelo primero.")
                                        st.stop()
                                    usuario_n = st.session_state.user.get("nombre_usuario", "Sistema")
                                    triaje_n = triage_svc.create_triage_event(
                                        id_paciente=existente["id_paciente"],
                                        profesional_responsable=usuario_n,
                                    )
                                    st.session_state.triaje_activo = triaje_n["id_triaje"]
                                    st.session_state.paciente_activo = existente["id_paciente"]
                                    st.success(f"✅ Nuevo triaje: `{triaje_n['id_triaje']}`")
                                    st.session_state.page = "signos_vitales"
                                    st.rerun()
                            with col_b:
                                if st.button("📜 Ver historial completo",
                                            use_container_width=True, key="dup_hist"):
                                    st.session_state.paciente_consulta = existente["id_paciente"]
                                    st.session_state.paciente_consulta_doc = existente.get(
                                        "numero_documento"
                                    )
                                    st.rerun()

                    except ValueError as ve:
                        st.error(f"❌ Error de validación: {ve}")


# ======================================================================
# BÚSQUEDA DE PACIENTES (HU-E2-02)
# ======================================================================

def _render_patient_search(patient_svc: PatientService, triage_svc: TriageService):
    """Búsqueda de pacientes por documento o nombre (HU-E2-02, HU-E2-03)."""

    st.subheader("🔍 Buscar Paciente")

    col_q, col_filtro, col_btn = st.columns([3, 2, 1])
    with col_q:
        query = st.text_input(
            "Documento, Nombres o Apellidos",
            placeholder="Buscar por CC, nombre o apellido...",
            key="p02_search_query",
            label_visibility="collapsed",
            help="Busque por número de documento, nombres o apellidos del paciente.",
        )
    with col_filtro:
        tipo_filtro = st.selectbox(
            "Tipo doc.",
            options=[""] + TIPOS_DOCUMENTO,
            format_func=lambda x: "Todos" if x == "" else TIPOS_DOC_LABELS.get(x, x),
            key="p02_search_tipo",
            label_visibility="collapsed",
        )
    with col_btn:
        buscar = st.button("Buscar", type="primary", use_container_width=True,
                          key="p02_btn_search")

    st.caption("💡 **Tip:** Busque por documento, nombres o apellidos del paciente.")

    # Si hay paciente en consulta por historial, mostrarlo directamente
    if "paciente_consulta" in st.session_state and st.session_state.paciente_consulta:
        paciente = patient_svc.get_patient_by_id(st.session_state.paciente_consulta)
        if paciente:
            _render_patient_detail(paciente, patient_svc, triage_svc)
        st.session_state.pop("paciente_consulta", None)
        return

    if buscar and query.strip():
        # Buscar pacientes por documento
        resultados = patient_svc.search_patients(
            query=query.strip(),
            tipo_documento=tipo_filtro if tipo_filtro else None,
        )
        # También buscar triajes por documento (para pacientes ya registrados)
        triajes_encontrados = patient_svc.search_triages_by_documento(
            query.strip(), limit=5
        )
    elif buscar:
        st.warning("Ingrese un número de documento para buscar.")
        return
    else:
        return

    if not resultados:
        st.info("🔍 No se encontraron pacientes con ese documento.")
        # Sugerir registrar nuevo paciente
        if st.button("📝 ¿Registrar nuevo paciente con este documento?", use_container_width=True):
            st.session_state.page = "registro_paciente"
            st.rerun()
        return

    st.success(f"**{len(resultados)}** paciente(s) encontrado(s)")

    # Mostrar también triajes activos encontrados por documento
    if triajes_encontrados:
        activos = [t for t in triajes_encontrados if t.get("estado") not in ("Cerrado", "Cancelado")]
        if activos:
            st.warning(f"⚠️ Este paciente tiene **{len(activos)}** triaje(s) activo(s) sin cerrar.")

    for p in resultados:
        _render_patient_card(p, patient_svc, triage_svc)


def _render_patient_card(paciente: dict, patient_svc: PatientService,
                         triage_svc: TriageService):
    """Tarjeta resumen de paciente en resultados de búsqueda (ampliado Épica 7)."""
    with st.container(border=True):
        cols = st.columns([3, 1, 1])
        with cols[0]:
            doc_label = TIPOS_DOC_LABELS.get(
                paciente["tipo_documento"], paciente["tipo_documento"]
            )
            # Construir nombre completo si está disponible
            nombre_completo = (
                f"{paciente.get('nombres', '')} {paciente.get('apellidos', '')}".strip()
            )
            if nombre_completo:
                st.markdown(f"**{nombre_completo}**")

            st.markdown(
                f"**{doc_label}:** {paciente['numero_documento']}  |  "
                f"Edad: {paciente['edad']}  |  "
                f"Sexo: {SEXO_LABELS.get(paciente['sexo'], paciente['sexo'])}"
            )
            extras = []
            if paciente.get('departamento'):
                extras.append(f"📍 {paciente['departamento']}" + 
                             (f" / {paciente['ciudad']}" if paciente.get('ciudad') else ""))
            if paciente.get('telefono'):
                extras.append(f"📞 {paciente['telefono']}")
            st.caption(
                f"Vía: {paciente.get('via_llegada', 'N/A')}  ·  "
                f"Registrado: {paciente.get('fecha_registro', 'N/A')[:10]}  ·  "
                f"Episodios previos: {paciente.get('episodios_previos_urgencias', 0)}"
            )
            if extras:
                st.caption("  ·  ".join(extras))
            if paciente.get("ultimo_triaje"):
                st.caption(f"Último triaje: {paciente['ultimo_triaje'][:10]}")

        with cols[1]:
            st.metric("Triajes", paciente.get("total_triages", 0))
        with cols[2]:
            # Verificar triaje activo (HU-E8-06)
            bloqueado_card, ta_card = _verificar_triaje_activo(triage_svc, paciente["id_paciente"])
            if bloqueado_card:
                st.caption(f"⚠️ Triaje activo: `{ta_card.get('id_triaje','')}`")
                st.caption(f"Estado: **{ta_card.get('estado','')}**")
            else:
                if st.button("📋 Nuevo Triaje", key=f"nt_{paciente['id_paciente']}",
                        use_container_width=True):
                    usuario = st.session_state.user.get("nombre_usuario", "Sistema")
                    triaje = triage_svc.create_triage_event(
                        id_paciente=paciente["id_paciente"],
                        profesional_responsable=usuario,
                    )
                    st.session_state.triaje_activo = triaje["id_triaje"]
                    st.session_state.paciente_activo = paciente["id_paciente"]
                    st.success(f"✅ Triaje creado: `{triaje['id_triaje']}`")
                    st.session_state.page = "signos_vitales"
                    st.rerun()

            if st.button("📜 Historial", key=f"hs_{paciente['id_paciente']}",
                        use_container_width=True):
                st.session_state.paciente_consulta = paciente["id_paciente"]
                st.rerun()


# ======================================================================
# HISTORIAL DE TRIAJES (HU-E2-03)
# ======================================================================

def _render_patient_detail(paciente: dict, patient_svc: PatientService,
                           triage_svc: TriageService):
    """Vista detallada de paciente + historial de triajes (HU-E2-03, ampliado Épica 7)."""
    st.subheader("📂 Historial del Paciente")

    nombre_completo = (
        f"{paciente.get('nombres', '')} {paciente.get('apellidos', '')}".strip()
    )
    if nombre_completo:
        st.markdown(f"### {nombre_completo}")

    st.markdown(
        f"**{TIPOS_DOC_LABELS.get(paciente['tipo_documento'], paciente['tipo_documento'])}:** "
        f"{paciente['numero_documento']}  |  "
        f"Edad: {paciente['edad']} años  |  "
        f"Sexo: {SEXO_LABELS.get(paciente['sexo'], paciente['sexo'])}"
    )
    # Datos de residencia
    if paciente.get('departamento'):
        residencia = f"📍 {paciente['departamento']}"
        if paciente.get('ciudad'):
            residencia += f", {paciente['ciudad']}"
        if paciente.get('direccion_residencia'):
            residencia += f" — {paciente['direccion_residencia']}"
        st.caption(residencia)
    if paciente.get('telefono'):
        st.caption(f"📞 {paciente['telefono']}" + 
                  (f"  |  📧 {paciente['correo']}" if paciente.get('correo') else ""))

    col_a, _ = st.columns([1, 3])
    with col_a:
        # Verificar triaje activo (HU-E8-06)
        bloqueado_det, ta_det = _verificar_triaje_activo(triage_svc, paciente["id_paciente"])
        if bloqueado_det:
            st.warning(f"⚠️ Triaje activo: `{ta_det.get('id_triaje','')}` (Estado: {ta_det.get('estado','')})")
        else:
            if st.button("📋 Nuevo Triaje", type="primary", use_container_width=True):
                usuario = st.session_state.user.get("nombre_usuario", "Sistema")
                triaje = triage_svc.create_triage_event(
                    id_paciente=paciente["id_paciente"],
                    profesional_responsable=usuario,
                )
                st.session_state.triaje_activo = triaje["id_triaje"]
                st.session_state.paciente_activo = paciente["id_paciente"]
                st.session_state.page = "signos_vitales"
                st.rerun()

    st.markdown("---")

    historial = patient_svc.get_patient_triage_history(paciente["id_paciente"])

    if not historial:
        st.info("📭 Este paciente no tiene eventos de triaje registrados.")
        return

    st.markdown(f"### 📊 {len(historial)} Evento(s) de Triaje")

    for i, t in enumerate(historial):
        estado = t.get("estado", "N/A")
        estado_color = _estado_color(estado)

        with st.container(border=True):
            cols = st.columns([2, 1, 1, 1])
            with cols[0]:
                st.markdown(f"**Evento:** `{t['id_triaje']}`")
                st.caption(f"Ingreso: {t.get('fecha_hora_ingreso', 'N/A')[:19]}")
            with cols[1]:
                st.markdown(f"Estado: :{estado_color}[`{estado}`]")
            with cols[2]:
                nivel_ia = t.get("nivel_sugerido_ia") or "—"
                nivel_pro = t.get("nivel_asignado_profesional") or "—"
                st.caption(f"IA: {nivel_ia} | Prof: {nivel_pro}")
            with cols[3]:
                with st.expander("📋 Detalles"):
                    if t.get("motivo_categoria"):
                        st.caption(f"Motivo: {t['motivo_categoria']}")
                    if t.get("temperatura"):
                        st.caption(
                            f"Temp: {t['temperatura']}°C | "
                            f"FC: {t.get('frecuencia_cardiaca', '—')} | "
                            f"SpO₂: {t.get('saturacion_o2', '—')}%"
                        )
                    if t.get("imc"):
                        st.caption(f"IMC: {t['imc']}")
                    if t.get("glasgow"):
                        st.caption(
                            f"Glasgow: {t['glasgow']} | "
                            f"Dolor: {t.get('escala_dolor', '—')}/10"
                        )


# ======================================================================
# UTILIDADES VISUALES
# ======================================================================

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


def _estado_color(estado: str) -> str:
    """Retorna el color para un estado del triaje."""
    colores = {
        "Registrado": "gray",
        "EnEvaluacion": "blue",
        "PendienteIA": "orange",
        "Clasificado": "violet",
        "Validado": "green",
        "Cerrado": "green",
        "Cancelado": "red",
    }
    return colores.get(estado, "gray")
