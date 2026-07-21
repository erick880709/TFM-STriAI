"""
Pantalla de Comparación de Modelos (P08).
Mockup: resources/diseno/mockups/p08-comparacion-modelos.md
Cubre: HU-E4-04 (Comparar modelos early vs late fusion).
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import json

from app.services.inference_service import get_inference_service

# Colores de niveles
NIVEL_COLORS = {
    "I": "#DC2626", "II": "#EA580C", "III": "#F59E0B",
    "IV": "#059669", "V": "#0891B2",
}
NIVEL_ICONS = {"I": "🔴", "II": "🟠", "III": "🟡", "IV": "🟢", "V": "🔵"}


def render_model_comparison():
    """Renderiza la pantalla P08 — Comparación de Modelos."""

    st.title("🔬 Comparación de Modelos")
    st.caption("Análisis comparativo de arquitecturas Early vs. Late Fusion")

    # ------------------------------------------------------------------
    # Cargar modelos disponibles
    # ------------------------------------------------------------------
    models_dir = Path(__file__).resolve().parent.parent.parent.parent / "models"

    if not models_dir.exists():
        st.warning("⚠️ No se encontró el directorio de modelos.")
        st.info(
            "Ejecute primero el pipeline de entrenamiento:\n\n"
            "`python run_pipeline.py`"
        )
        return

    # Buscar modelos serializados
    model_dirs = sorted(
        [d for d in models_dir.iterdir()
         if d.is_dir() and (d / "metadata.json").exists()],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )

    if not model_dirs:
        st.warning("⚠️ No se encontraron modelos serializados en models/.")
        return

    # Cargar metadatos de todos los modelos
    modelos_info = []
    for md in model_dirs:
        try:
            with open(md / "metadata.json", "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta["_dir"] = str(md)
            meta["_name"] = md.name
            modelos_info.append(meta)
        except Exception:
            pass

    if not modelos_info:
        st.warning("No se pudieron cargar los metadatos de los modelos.")
        return

    st.success(f"**{len(modelos_info)}** modelo(s) encontrado(s) en models/")

    # ------------------------------------------------------------------
    # Selector de modelos a comparar
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📊 Comparación de Métricas")

    col1, col2 = st.columns(2)

    with col1:
        modelo_a_name = st.selectbox(
            "Modelo A",
            options=[m["_name"] for m in modelos_info],
            index=0,
            key="comp_model_a",
        )
    with col2:
        # Por defecto seleccionar otro modelo si hay más de uno
        idx_b = 1 if len(modelos_info) > 1 else 0
        modelo_b_name = st.selectbox(
            "Modelo B",
            options=[m["_name"] for m in modelos_info],
            index=idx_b,
            key="comp_model_b",
        )

    modelo_a = next((m for m in modelos_info if m["_name"] == modelo_a_name), None)
    modelo_b = next((m for m in modelos_info if m["_name"] == modelo_b_name), None)

    if not modelo_a or not modelo_b:
        return

    # ------------------------------------------------------------------
    # Tabla comparativa de métricas
    # ------------------------------------------------------------------
    st.markdown("### 📈 Métricas lado a lado")

    metrics_a = modelo_a.get("metrics", {})
    metrics_b = modelo_b.get("metrics", {})

    metric_keys = [
        ("f1_macro", "F1 Macro"),
        ("f1_weighted", "F1 Weighted"),
        ("precision_macro", "Precision Macro"),
        ("recall_macro", "Recall Macro"),
        ("accuracy", "Accuracy"),
        ("auc_roc_macro", "AUC-ROC Macro"),
        ("auprc_macro", "AUPRC Macro"),
    ]

    rows = []
    for key, label in metric_keys:
        val_a = metrics_a.get(key)
        val_b = metrics_b.get(key)

        if val_a is not None and val_b is not None:
            delta = val_a - val_b
            mejor = "✅ A" if delta > 0.001 else ("✅ B" if delta < -0.001 else "🤝 Empate")
            rows.append({
                "Métrica": label,
                f"Modelo A: {modelo_a_name}": f"{val_a:.4f}",
                f"Modelo B: {modelo_b_name}": f"{val_b:.4f}",
                "Δ": f"{delta:+.4f}",
                "Mejor": mejor,
            })

    if rows:
        df_comparacion = pd.DataFrame(rows)
        st.dataframe(df_comparacion, width='stretch', hide_index=True)

        # Determinar ganador
        a_wins = sum(1 for r in rows if "✅ A" in r["Mejor"])
        b_wins = sum(1 for r in rows if "✅ B" in r["Mejor"])

        if a_wins > b_wins:
            st.success(
                f"🏆 **Modelo A ({modelo_a_name})** gana en {a_wins} de {len(rows)} métricas "
                f"(vs {b_wins} del Modelo B)"
            )
        elif b_wins > a_wins:
            st.success(
                f"🏆 **Modelo B ({modelo_b_name})** gana en {b_wins} de {len(rows)} métricas "
                f"(vs {a_wins} del Modelo A)"
            )
        else:
            st.info(f"🤝 Empate técnico ({a_wins} métricas cada uno)")

    # ------------------------------------------------------------------
    # Comparación por clase (Recall)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📊 Recall por Nivel de Triaje")

    recall_rows = []
    for nivel in ["I", "II", "III", "IV", "V"]:
        # Reconstruir desde métricas (si no están en metadata, intentar de thresholds)
        rec_a = metrics_a.get(f"recall_{nivel}", metrics_a.get("recall_per_class", {}).get(nivel))
        rec_b = metrics_b.get(f"recall_{nivel}", metrics_b.get("recall_per_class", {}).get(nivel))

        if rec_a is not None or rec_b is not None:
            rec_a = rec_a or 0
            rec_b = rec_b or 0
            delta = (rec_a or 0) - (rec_b or 0)
            recall_rows.append({
                "Nivel": f"{NIVEL_ICONS.get(nivel, '')} {nivel}",
                f"Modelo A Recall": f"{rec_a:.4f}" if rec_a else "—",
                f"Modelo B Recall": f"{rec_b:.4f}" if rec_b else "—",
                "Δ Recall": f"{delta:+.4f}",
                "Prioridad Clínica": "🔴 Crítico" if nivel in ("I", "II") else "🟡 Importante" if nivel == "III" else "🟢 Rutinario",
            })

    if recall_rows:
        df_recall = pd.DataFrame(recall_rows)
        st.dataframe(df_recall, width='stretch', hide_index=True)

        # Destacar Recall I-II
        rec_i_a = metrics_a.get("recall_I", "—")
        rec_i_b = metrics_b.get("recall_I", "—")
        rec_ii_a = metrics_a.get("recall_II", "—")
        rec_ii_b = metrics_b.get("recall_II", "—")

        st.markdown("#### 🎯 Recall en Niveles Críticos (prioridad clínica)")
        cols = st.columns(4)
        with cols[0]:
            st.metric(f"Nivel I — {modelo_a_name}", f"{rec_i_a}" if rec_i_a != "—" else "—")
        with cols[1]:
            st.metric(f"Nivel I — {modelo_b_name}", f"{rec_i_b}" if rec_i_b != "—" else "—")
        with cols[2]:
            st.metric(f"Nivel II — {modelo_a_name}", f"{rec_ii_a}" if rec_ii_a != "—" else "—")
        with cols[3]:
            st.metric(f"Nivel II — {modelo_b_name}", f"{rec_ii_b}" if rec_ii_b != "—" else "—")

    # ------------------------------------------------------------------
    # Información técnica de cada modelo
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📋 Ficha Técnica")

    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.markdown(f"### Modelo A: {modelo_a.get('model_name', modelo_a_name)}")
            st.markdown(f"- **Versión:** {modelo_a.get('version', 'N/A')}")
            st.markdown(f"- **Features:** {modelo_a.get('n_features', 'N/A')}")
            st.markdown(f"- **Framework:** {modelo_a.get('framework', 'N/A')}")
            st.markdown(f"- **Serializado:** {modelo_a.get('serialized_at', 'N/A')[:19]}")
            if modelo_a.get("thresholds"):
                th = modelo_a["thresholds"]
                st.markdown(f"- **Umbrales:** {th}")
            st.markdown(f"- **Descripción:** {modelo_a.get('description', 'N/A')}")

    with col_b:
        with st.container(border=True):
            st.markdown(f"### Modelo B: {modelo_b.get('model_name', modelo_b_name)}")
            st.markdown(f"- **Versión:** {modelo_b.get('version', 'N/A')}")
            st.markdown(f"- **Features:** {modelo_b.get('n_features', 'N/A')}")
            st.markdown(f"- **Framework:** {modelo_b.get('framework', 'N/A')}")
            st.markdown(f"- **Serializado:** {modelo_b.get('serialized_at', 'N/A')[:19]}")
            if modelo_b.get("thresholds"):
                th = modelo_b["thresholds"]
                st.markdown(f"- **Umbrales:** {th}")
            st.markdown(f"- **Descripción:** {modelo_b.get('description', 'N/A')}")

    # ------------------------------------------------------------------
    # Estado del servicio de inferencia
    # ------------------------------------------------------------------
    st.markdown("---")
    with st.expander("🔧 Estado del Servicio de Inferencia"):
        if "inference_service" in st.session_state:
            status = st.session_state.inference_service.get_status()
            # Mostrar info formateada en lugar de JSON crudo
            cols = st.columns(4)
            modelo_cargado = status.get("modelo_cargado", False)
            with cols[0]:
                if modelo_cargado:
                    st.success("✅ Modelo activo")
                else:
                    st.error("❌ Sin modelo")
            with cols[1]:
                st.metric("Versión", status.get("model_version", "N/D"))
            with cols[2]:
                st.metric("Features", status.get("n_features", "N/D"))
            with cols[3]:
                st.metric("Framework", status.get("framework", "N/D"))
            if modelo_cargado and status.get("model_path"):
                st.caption(f"📁 Ruta: `{status['model_path']}`")
            if "thresholds" in status and status["thresholds"]:
                st.markdown("**🎯 Umbrales de clasificación:**")
                th_df = pd.DataFrame(
                    [{"Nivel": f"Nivel {k}", "Umbral": f"{v:.4f}"} for k, v in status["thresholds"].items()]
                )
                st.dataframe(th_df, width='stretch', hide_index=True)
        else:
            st.info("Servicio de inferencia no inicializado.")

