"""
Pantalla de Gestión de Modelos IA (P09).
Mockup: resources/diseno/mockups/p09-gestion-modelos.md
Cubre: HU-E6-02 (Registro, versionado, activación/rollback de modelos).
"""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.services.inference_service import get_inference_service
from app.services.model_management_service import ModelManagementService

# Colores
NIVEL_COLORS = {"I": "#DC2626", "II": "#EA580C", "III": "#F59E0B", "IV": "#059669", "V": "#0891B2"}


def render_model_management():
    """Renderiza la pantalla P09 — Gestión de Modelos IA."""

    st.title("⚙️ Gestión de Modelos IA")
    st.caption("Registro, versionado y activación de modelos de Machine Learning")

    db_path = st.session_state.db_path

    # ------------------------------------------------------------------
    # Inicializar servicio de inferencia (forzar carga del modelo)
    # ------------------------------------------------------------------
    if "inference_service" not in st.session_state:
        with st.spinner("🔧 Inicializando motor de IA y cargando modelo..."):
            st.session_state.inference_service = get_inference_service()
    
    inference_svc = st.session_state.inference_service
    status = inference_svc.get_status()
    
    # Si no está cargado, intentar cargar
    if not status.get("modelo_cargado"):
        with st.spinner("🔧 Cargando modelo desde models/..."):
            loaded = inference_svc.load_model()
            if loaded:
                status = inference_svc.get_status()
                st.success("✅ Modelo cargado exitosamente")
                st.rerun()
    
    # ------------------------------------------------------------------
    # Estado del servicio de inferencia
    # ------------------------------------------------------------------
    with st.container(border=True):
        cols = st.columns(4)
        with cols[0]:
            if status.get("modelo_cargado"):
                st.success("✅ Modelo Activo")
            else:
                st.error("❌ Sin modelo cargado")
        with cols[1]:
            st.metric("Modelo", status.get("nombre_modelo", "N/A"))
        with cols[2]:
            st.metric("Versión", status.get("version", "N/A"))
        with cols[3]:
            st.metric("Features", status.get("n_features", 0))
        
        if status.get("error"):
            st.warning(f"⚠️ {status['error']}")
        
        # Mostrar detalles en popup expander
        with st.expander("📊 Umbrales y Detalles del Modelo Activo", expanded=False):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("**🎯 Umbrales de Clasificación**")
                thresholds = status.get("thresholds", {})
                if thresholds:
                    umbral_data = []
                    for k, v in thresholds.items():
                        # k puede ser int o str; convertir a int para indexar
                        try:
                            idx = int(k)
                            nivel = ["I", "II", "III", "IV", "V"][idx] if 0 <= idx <= 4 else str(k)
                        except (ValueError, TypeError):
                            nivel = str(k)
                        umbral_data.append({"Nivel": nivel, "Umbral": float(v)})
                    st.dataframe(umbral_data, use_container_width=True, hide_index=True)
                else:
                    st.caption("No hay umbrales configurados.")
            
            with col_d2:
                st.markdown("**📋 Información del Modelo**")
                st.markdown(f"- **Nombre:** {status.get('nombre_modelo', 'N/A')}")
                st.markdown(f"- **Versión:** {status.get('version', 'N/A')}")
                st.markdown(f"- **Features:** {status.get('n_features', 0)}")
                st.markdown(f"- **SHAP disponible:** {'✅ Sí' if status.get('shap_disponible') else '❌ No'}")
                st.markdown(f"- **Directorio:** `{status.get('models_dir', 'N/A')}`")

    st.markdown("---")

    # ==================================================================
    # MODELOS EN BASE DE DATOS (Tabla Modelo)
    # ==================================================================
    st.subheader("📋 Modelos Registrados en el Sistema")

    if "model_mgmt_service" not in st.session_state:
        st.session_state.model_mgmt_service = ModelManagementService(db_path)

    mgmt_svc = st.session_state.model_mgmt_service
    modelos_list = mgmt_svc.list_models()

    # ==================================================================
    # MODELOS SERIALIZADOS EN DISCO
    # ==================================================================
    models_dir = Path(__file__).resolve().parent.parent.parent.parent / "models"

    modelos_disco = []
    if models_dir.exists():
        for md in sorted(
            [d for d in models_dir.iterdir() if d.is_dir() and (d / "metadata.json").exists()],
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        ):
            try:
                with open(md / "metadata.json", "r", encoding="utf-8") as f:
                    meta = json.load(f)
                meta["_dir"] = str(md)
                meta["_name"] = md.name
                meta["_size_mb"] = _get_dir_size(md)
                modelos_disco.append(meta)
            except Exception:
                pass

    # ==================================================================
    # TAB: Modelos en Disco
    # ==================================================================
    tab_disco, tab_db, tab_registrar = st.tabs([
        "💾 Modelos Serializados", "🗄️ Registro BD", "➕ Registrar Modelo"
    ])

    # --- TAB 1: Modelos en disco ---
    with tab_disco:
        if not modelos_disco:
            st.info("No se encontraron modelos serializados en models/.")
            st.caption("Ejecute `python run_pipeline.py` para entrenar y serializar un modelo.")
        else:
            st.success(f"**{len(modelos_disco)}** modelo(s) encontrado(s) en disco")

            # Verificar cuál es el activo
            active_file = models_dir / "active_version.txt"
            active_version = ""
            if active_file.exists():
                with open(active_file) as f:
                    active_version = f.read().strip()

            for i, meta in enumerate(modelos_disco):
                is_active = meta["_name"] == active_version
                border_color = "#059669" if is_active else "#E2E8F0"

                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

                    with col1:
                        badge = "🟢 ACTIVO" if is_active else "⚪ Inactivo"
                        st.markdown(f"**{meta.get('model_name', meta['_name'])}** {badge}")
                        st.caption(
                            f"v{meta.get('version', '?')} · "
                            f"Features: {meta.get('n_features', '?')} · "
                            f"Tamaño: {meta.get('_size_mb', 0):.1f} MB"
                        )
                        if meta.get("description"):
                            st.caption(meta["description"][:100])

                    with col2:
                        metrics = meta.get("metrics", {})
                        f1 = metrics.get("f1_macro")
                        auc = metrics.get("auc_roc_macro")
                        if f1:
                            st.metric("F1 Macro", f"{f1:.4f}")
                        if auc:
                            st.metric("AUC-ROC", f"{auc:.4f}")

                    with col3:
                        if meta.get("thresholds"):
                            with st.expander("🎯 Umbrales"):
                                th_data = [{"Nivel": f"Nivel {k}", "Umbral": f"{v:.4f}"} for k, v in meta["thresholds"].items()]
                                st.dataframe(th_data, use_container_width=True, hide_index=True)

                    with col4:
                        if not is_active:
                            if st.button("🟢 Activar", key=f"activate_{i}", use_container_width=True):
                                try:
                                    # Actualizar active_version.txt
                                    with open(active_file, "w") as f:
                                        f.write(meta["_name"])
                                    st.success(f"✅ Modelo {meta['_name']} activado. Reinicie la app para aplicar.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

                        with st.expander("📋 Detalles"):
                            st.markdown(f"- **Nombre:** {meta.get('model_name', 'N/A')}")
                            st.markdown(f"- **Versión:** {meta.get('version', 'N/A')}")
                            st.markdown(f"- **Framework:** {meta.get('framework', 'N/A')}")
                            st.markdown(f"- **Serializado:** {str(meta.get('serialized_at', 'N/A'))[:19]}")
                            st.markdown(f"- **Features:** {meta.get('n_features', 'N/A')}")
                            if meta.get('class_labels'):
                                st.markdown(f"- **Clases:** {meta['class_labels']}")

    # --- TAB 2: Registro en BD ---
    with tab_db:
        if not modelos_list:
            st.info("No hay modelos registrados en la base de datos.")
        else:
            st.success(f"**{len(modelos_list)}** modelo(s) en la base de datos")

            for m in modelos_list:
                with st.container(border=True):
                    cols = st.columns([2, 1, 1, 1])
                    with cols[0]:
                        estado_icon = "🟢" if m.get("estado") == "Activo" else "⚪"
                        st.markdown(f"**{estado_icon} {m.get('nombre', 'N/A')}**")
                        st.caption(f"v{m.get('version', '?')} · {m.get('arquitectura', '?')} · {m.get('algoritmo', '?')}")
                    with cols[1]:
                        st.metric("F1", f"{m.get('f1_score', 0):.4f}" if m.get('f1_score') else "—")
                    with cols[2]:
                        st.metric("AUC", f"{m.get('aucroc', 0):.4f}" if m.get('aucroc') else "—")
                    with cols[3]:
                        st.markdown(f"`{m.get('estado', '?')}`")
                        st.caption(m.get("fecha_registro", "")[:10])

    # --- TAB 3: Registrar nuevo modelo ---
    with tab_registrar:
        st.subheader("➕ Registrar Nuevo Modelo en BD")

        # Autocompletar con modelos del disco
        disco_options = [""] + [m["_name"] for m in modelos_disco]
        seleccion = st.selectbox(
            "Seleccionar modelo serializado (opcional)",
            options=disco_options,
            help="Autocompleta los campos desde metadata.json",
        )

        meta_prefill = {}
        if seleccion:
            meta_prefill = next((m for m in modelos_disco if m["_name"] == seleccion), {})

        with st.form("register_model_form"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input(
                    "Nombre del Modelo *",
                    value=meta_prefill.get("model_name", ""),
                    placeholder="Ej: XGBoost Early Fusion",
                )
                version = st.text_input(
                    "Versión *",
                    value=meta_prefill.get("version", ""),
                    placeholder="v20260719_120000",
                )
                arquitectura = st.selectbox(
                    "Arquitectura *",
                    options=["Early Fusion", "Late Fusion", "Unimodal"],
                    index=0,
                )
                algoritmo = st.text_input(
                    "Algoritmo",
                    value="XGBoost",
                )
            with col2:
                estado = st.selectbox(
                    "Estado",
                    options=["EnValidacion", "Activo", "Inactivo"],
                    index=0,
                )
                f1_score = st.number_input(
                    "F1 Score",
                    min_value=0.0, max_value=1.0, step=0.0001,
                    value=float(meta_prefill.get("metrics", {}).get("f1_macro", 0)),
                    format="%.4f",
                )
                auc_roc = st.number_input(
                    "AUC-ROC",
                    min_value=0.0, max_value=1.0, step=0.0001,
                    value=float(meta_prefill.get("metrics", {}).get("auc_roc_macro", 0)),
                    format="%.4f",
                )

            hiperparametros = st.text_area(
                "Hiperparámetros (JSON)",
                value=json.dumps({
                    "n_estimators": 300,
                    "max_depth": 10,
                    "learning_rate": 0.03,
                }, indent=2),
                height=80,
            )
            dataset_info = st.text_input(
                "Dataset de Entrenamiento",
                value="MIMIC-IV-ED + San Juan de Dios + datos.gov.co",
            )

            if st.form_submit_button("Registrar Modelo", type="primary"):
                if not nombre or not version:
                    st.error("Nombre y Versión son obligatorios.")
                else:
                    try:
                        mgmt_svc.register_model(
                            nombre=nombre,
                            version=version,
                            arquitectura=arquitectura,
                            algoritmo=algoritmo,
                            hiperparametros=json.loads(hiperparametros) if hiperparametros else None,
                            dataset_entrenamiento=dataset_info,
                            f1_score=f1_score if f1_score else None,
                            auc_roc=auc_roc if auc_roc else None,
                            estado=estado,
                        )
                        st.success(f"✅ Modelo `{nombre}` v{version} registrado exitosamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ==================================================================
    # INFORMACIÓN DEL SERVICIO
    # ==================================================================
    st.markdown("---")
    with st.expander("🔧 Estado del Servicio de Inferencia"):
        cols_st = st.columns(4)
        modelo_ok = status.get("modelo_cargado", False)
        with cols_st[0]:
            if modelo_ok:
                st.success("✅ Modelo Activo")
            else:
                st.error("❌ Sin modelo")
        with cols_st[1]:
            st.metric("Modelo", status.get("nombre_modelo", "N/D"))
        with cols_st[2]:
            st.metric("Versión", status.get("version", "N/D"))
        with cols_st[3]:
            st.metric("Features", status.get("n_features", "N/D"))
        if status.get("error"):
            st.warning(f"⚠️ {status['error']}")
        if status.get("models_dir"):
            st.caption(f"📁 Directorio: `{status['models_dir']}`")
        if status.get("thresholds"):
            st.markdown("**🎯 Umbrales de clasificación:**")
            th_data = [{"Nivel": f"Nivel {k}", "Umbral": f"{v:.4f}"} for k, v in status["thresholds"].items()]
            st.dataframe(th_data, use_container_width=True, hide_index=True)


def _get_dir_size(path: Path) -> float:
    """Calcula el tamaño total de un directorio en MB."""
    total = 0
    try:
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
    except Exception:
        pass
    return total / (1024 * 1024)

