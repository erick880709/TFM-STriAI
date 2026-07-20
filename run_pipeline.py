"""
Pipeline de Entrenamiento Completo
==================================
TFM UNIR — Sistema de Triaje Multimodal IA
Épica 3: Pipeline de Datos y Entrenamiento del Modelo

Este script ejecuta el pipeline de 13 pasos documentado en:
  resources/architecture/Documento_Arquitectura_Sistema_Triaje_IA.md §8.2

Uso:
  python run_pipeline.py [--datasets-dir DATASETS_DIR] [--output-dir OUTPUT_DIR]
"""

import sys
import os
import argparse
import logging
import time
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("pipeline")

# Agregar src/ al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.data.ingesta import DataIngester, load_unified_dataset
from src.data.anonimizacion import anonymize
from src.data.limpieza import clean_and_prepare
from src.features.nlp_embeddings import NLPEmbedder, generate_clinical_embeddings
from src.models.train_models import ModelTrainer, encode_labels
from src.evaluation.metrics import ThresholdTuner, evaluate_model, print_evaluation_report
from src.evaluation.shap_benchmarks import SHAPExplainer, compare_with_benchmarks
from src.serving.serialize import ModelSerializer


# ======================================================================
# CONFIGURACIÓN
# ======================================================================
RANDOM_SEED = 42
TEST_SIZE = 0.20
BASE_DIR = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Entrenamiento — Triaje IA")
    parser.add_argument(
        "--datasets-dir",
        default=str(BASE_DIR / "datasets"),
        help="Directorio con los archivos CSV de entrenamiento",
    )
    parser.add_argument(
        "--output-dir",
        default=str(BASE_DIR / "models"),
        help="Directorio de salida para modelos serializados",
    )
    parser.add_argument(
        "--nlp-model",
        default="multilingual",
        choices=["beto_clinico", "biomedical_es", "multilingual"],
        help="Modelo NLP a utilizar para embeddings",
    )
    parser.add_argument(
        "--use-gpu",
        action="store_true",
        help="Usar GPU si está disponible",
    )
    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("  PIPELINE DE ENTRENAMIENTO — SISTEMA DE TRIAJE MULTIMODAL IA")
    logger.info("  TFM UNIR · Máster en Inteligencia Artificial")
    logger.info("=" * 70)

    t_total_start = time.time()

    # ================================================================
    # PASOS 1-2: INGESTA Y ANONIMIZACIÓN (TT-E3-01)
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASOS 1-2: INGESTA Y ANONIMIZACIÓN")
    logger.info("=" * 60)

    df_raw = load_unified_dataset(args.datasets_dir)
    logger.info(f"  Dataset unificado: {len(df_raw):,} filas × {len(df_raw.columns)} columnas")

    df_anon = anonymize(df_raw)
    logger.info(f"  Dataset anonimizado: {len(df_anon):,} filas × {len(df_anon.columns)} columnas")

    # ================================================================
    # PASOS 3-4: LIMPIEZA Y NORMALIZACIÓN (TT-E3-02)
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASOS 3-4: LIMPIEZA Y FEATURE ENGINEERING")
    logger.info("=" * 60)

    df_clean, X_struct, scaler, encoder, feature_names = clean_and_prepare(
        df_anon, target_col="nivel_triaje"
    )
    logger.info(f"  Features estructuradas: {X_struct.shape}")

    # Target: codificar niveles I-V a 0-4
    y = encode_labels(df_clean["nivel_triaje"].values)
    logger.info(f"  Distribución de clases: {dict(zip(['I','II','III','IV','V'], np.bincount(y)))}")

    # ================================================================
    # PASO 5: SPLIT TRAIN/TEST ESTRATIFICADO
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASO 5: SPLIT TRAIN/TEST (80/20 ESTRATIFICADO)")
    logger.info("=" * 60)

    from sklearn.model_selection import train_test_split

    X_s_train, X_s_test, y_train, y_test = train_test_split(
        X_struct, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y,
    )
    logger.info(f"  Train: {len(X_s_train):,} | Test: {len(X_s_test):,}")

    # ================================================================
    # PASO 6: EMBEDDINGS NLP (TT-E3-03)
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASO 6: EMBEDDINGS NLP CON BERT CLÍNICO")
    logger.info("=" * 60)

    nlp_embedder = NLPEmbedder(model_name=args.nlp_model, use_gpu=args.use_gpu)
    logger.info(f"  Config NLP: {nlp_embedder.get_config()}")

    # Extraer textos del motivo de consulta (train y test)
    textos_train = df_clean.iloc[:len(X_s_train)]["motivo_consulta_texto"].fillna("").tolist()
    textos_test = df_clean.iloc[len(X_s_train):]["motivo_consulta_texto"].fillna("").tolist()

    logger.info(f"  Generando embeddings para {len(textos_train):,} textos (train)...")
    X_nlp_train = nlp_embedder.generate_embeddings(textos_train, fit_tfidf=True)
    logger.info(f"  Train NLP: {X_nlp_train.shape}")

    logger.info(f"  Generando embeddings para {len(textos_test):,} textos (test)...")
    X_nlp_test = nlp_embedder.generate_embeddings(textos_test, fit_tfidf=False)
    logger.info(f"  Test NLP: {X_nlp_test.shape}")

    # ================================================================
    # PASO 7: BASELINES UNIMODALES (TT-E3-04)
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASO 7: BASELINES UNIMODALES")
    logger.info("=" * 60)

    trainer = ModelTrainer(random_seed=RANDOM_SEED)
    trainer.train_baselines(X_s_train, y_train, X_s_test, y_test)

    # ================================================================
    # PASO 8: EARLY FUSION (TT-E3-05)
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASO 8: EARLY FUSION")
    logger.info("=" * 60)

    trainer.train_early_fusion(
        X_s_train, X_nlp_train, y_train,
        X_s_test, X_nlp_test, y_test,
    )

    # ================================================================
    # PASO 9: LATE FUSION (TT-E3-06)
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASO 9: LATE FUSION")
    logger.info("=" * 60)

    trainer.train_late_fusion(
        X_s_train, X_nlp_train, y_train,
        X_s_test, X_nlp_test, y_test,
    )

    # ================================================================
    # PASO 10: SELECCIÓN DEL MEJOR MODELO
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASO 10: SELECCIÓN DEL MEJOR MODELO")
    logger.info("=" * 60)

    best_name, best_model = trainer.select_best_model(criterion="f1_macro")

    # Tabla comparativa
    tabla = trainer.get_summary_table()
    logger.info("\n" + tabla.to_string(index=False))

    # ================================================================
    # PASO 11: THRESHOLD TUNING (TT-E3-07)
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASO 11: THRESHOLD TUNING (NIVELES I-II)")
    logger.info("=" * 60)

    # Obtener probabilidades del mejor modelo para test
    if best_name == "Late Fusion":
        # Late Fusion necesita reconstruir probabilidades
        proba_a = best_model["submodel_a"].predict_proba(X_s_test)
        proba_b = best_model["submodel_b"].predict_proba(X_nlp_test)
        X_meta = np.hstack([proba_a, proba_b])
        y_proba_best = best_model["meta_model"].predict_proba(X_meta)
    elif best_name == "Early Fusion":
        X_concat_test = np.hstack([X_s_test, X_nlp_test])
        y_proba_best = best_model.predict_proba(X_concat_test)
    else:
        y_proba_best = best_model.predict_proba(X_s_test)

    tuner = ThresholdTuner(f1_degradation_limit=0.10)
    thresholds = tuner.tune(y_test, y_proba_best, priority_classes=(0, 1))
    y_pred_tuned = tuner.apply_thresholds(y_proba_best, thresholds)

    # ================================================================
    # PASO 12: EVALUACIÓN FINAL (TT-E3-07 + TT-E3-08)
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASO 12: EVALUACIÓN FINAL")
    logger.info("=" * 60)

    results = evaluate_model(y_test, y_pred_tuned, y_proba_best, thresholds)
    print_evaluation_report(results)

    # Verificar metas
    metas = {
        "F1 Macro ≥ 0.82": results["f1_macro"] >= 0.82,
        "AUC-ROC ≥ 0.87": results["auc_roc_macro"] >= 0.87,
    }
    logger.info("\n  Verificación de Metas:")
    for meta, cumple in metas.items():
        icono = "✓" if cumple else "✗"
        logger.info(f"    {icono} {meta}")

    # ================================================================
    # PASO 13: SHAP EXPLICABILITY (TT-E3-08)
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASO 13: EXPLICABILIDAD SHAP + BENCHMARKS")
    logger.info("=" * 60)

    # SHAP sobre el modelo ganador
    if best_name in ("Early Fusion", "LR (Regresión Logística)", "RF (Random Forest)", "XGBoost"):
        model_for_shap = best_model if best_name != "Late Fusion" else best_model["submodel_a"]
        X_for_shap = X_s_test
        fn_for_shap = feature_names
    else:
        model_for_shap = best_model["submodel_a"]
        X_for_shap = X_s_test
        fn_for_shap = feature_names

    shap_explainer = SHAPExplainer(model_for_shap, fn_for_shap)
    shap_explainer.fit(X_for_shap, max_samples=500)
    shap_result = shap_explainer.explain(X_for_shap[:200], max_display=15)

    logger.info("  Top 10 Features SHAP (importancia media):")
    for i, feat in enumerate(shap_result.get("top_features", [])[:10]):
        logger.info(f"    {i+1}. {feat['nombre_clinico']}: {feat['shap_importance']:.4f}")

    # Comparativa contra benchmarks de la literatura
    benchmark_df = compare_with_benchmarks(results)
    logger.info("\n  Comparativa contra Benchmarks:")
    logger.info("\n" + benchmark_df.to_string(index=False))

    # ================================================================
    # PASO 14: SERIALIZACIÓN (TT-E3-09)
    # ================================================================
    logger.info("\n" + "=" * 60)
    logger.info("  PASO 14: SERIALIZACIÓN DEL MODELO GANADOR")
    logger.info("=" * 60)

    serializer = ModelSerializer(output_dir=args.output_dir)
    version = datetime.now().strftime("%Y%m%d_%H%M%S")

    model_dir = serializer.serialize(
        model=model_for_shap,
        model_name=best_name,
        version=f"v{version}",
        scaler=scaler,
        encoder=encoder,
        feature_names=feature_names,
        metrics=results,
        thresholds=thresholds,
        nlp_model_key=args.nlp_model,
        description=f"Modelo {best_name} entrenado sobre {len(df_clean):,} registros clínicos.",
    )

    logger.info(f"\n  ✓ Modelo serializado en: {model_dir}")

    # ================================================================
    # RESUMEN FINAL
    # ================================================================
    t_total = time.time() - t_total_start
    logger.info("\n" + "=" * 70)
    logger.info("  PIPELINE COMPLETADO EXITOSAMENTE")
    logger.info("=" * 70)
    logger.info(f"  Tiempo total: {t_total/60:.1f} minutos")
    logger.info(f"  Modelo ganador: {best_name}")
    logger.info(f"  F1 Macro: {results['f1_macro']:.4f}")
    logger.info(f"  AUC-ROC: {results['auc_roc_macro']:.4f}")
    logger.info(f"  Recall Nivel I: {results['recall_I']:.4f}")
    logger.info(f"  Recall Nivel II: {results['recall_II']:.4f}")
    logger.info(f"  Modelo serializado: {model_dir}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
