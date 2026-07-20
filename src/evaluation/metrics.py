"""
Threshold Tuning y Evaluación Final — TT-E3-07.
Optimiza umbrales por clase para maximizar Recall en Niveles I-II,
evalúa métricas por clase, matriz de confusión, AUPRC.

Referencia: Documento de Arquitectura §12, RT-004.
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any, Optional
from sklearn.metrics import (
    confusion_matrix, classification_report,
    precision_recall_curve, average_precision_score,
    f1_score, recall_score, precision_score, roc_auc_score,
)
import logging

logger = logging.getLogger(__name__)

CLASS_LABELS = ["I", "II", "III", "IV", "V"]


class ThresholdTuner:
    """
    Ajusta umbrales de decisión por clase para priorizar Recall en Niveles I-II.
    Estrategia: bajar el umbral de las clases I y II para que el modelo
    sea más sensible (mayor Recall) sin degradar F1 macro más del 10%.
    """

    def __init__(self, f1_degradation_limit: float = 0.10):
        """
        Args:
            f1_degradation_limit: Máxima degradación permitida de F1 macro (0.10 = 10%).
        """
        self.f1_limit = f1_degradation_limit
        self.optimal_thresholds: Optional[Dict[int, float]] = None
        self.baseline_f1: float = 0.0
        self.tuned_f1: float = 0.0

    def tune(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        priority_classes: Tuple[int, ...] = (0, 1),  # Niveles I, II
    ) -> Dict[int, float]:
        """
        Busca umbrales óptimos para las clases prioritarias.
        Para cada clase prioritaria, prueba umbrales de 0.05 a 0.50
        y selecciona el que maximiza Recall sin degradar F1 > limit.

        Args:
            y_true: Etiquetas verdaderas (0-4).
            y_proba: Probabilidades (n_samples, 5).
            priority_classes: Índices de clases prioritarias.

        Returns:
            Dict[int, float]: Umbral óptimo por clase.
        """
        # F1 baseline (argmax puro)
        y_pred_baseline = np.argmax(y_proba, axis=1)
        self.baseline_f1 = f1_score(y_true, y_pred_baseline, average="macro")
        logger.info(f"F1 baseline (argmax): {self.baseline_f1:.4f}")

        thresholds = {i: 0.20 for i in range(5)}  # Default: 0.20 (umbral estándar)

        for cls in priority_classes:
            best_threshold = 0.20
            best_recall = recall_score(y_true == cls, y_pred_baseline == cls, zero_division=0)

            for th in np.arange(0.05, 0.51, 0.025):
                # Aplicar umbral: si P(cls) >= th → predice cls
                y_pred_tuned = np.argmax(y_proba, axis=1)

                # Para la clase prioritaria, si P > th, asignar esa clase
                mask_priority = y_proba[:, cls] >= th
                y_pred_tuned[mask_priority] = cls

                f1_tuned = f1_score(y_true, y_pred_tuned, average="macro")
                recall_tuned = recall_score(y_true == cls, y_pred_tuned == cls, zero_division=0)

                degradation = (self.baseline_f1 - f1_tuned) / max(self.baseline_f1, 1e-6)

                if degradation <= self.f1_limit and recall_tuned > best_recall:
                    best_recall = recall_tuned
                    best_threshold = th

            thresholds[cls] = best_threshold
            logger.info(
                f"  Clase {CLASS_LABELS[cls]}: umbral={best_threshold:.3f}, "
                f"Recall={best_recall:.4f} (F1 degradation={degradation:.1%})"
            )

        self.optimal_thresholds = thresholds
        return thresholds

    def apply_thresholds(
        self,
        y_proba: np.ndarray,
        thresholds: Optional[Dict[int, float]] = None,
    ) -> np.ndarray:
        """
        Aplica los umbrales optimizados a las probabilidades.
        """
        if thresholds is None:
            thresholds = self.optimal_thresholds or {i: 0.20 for i in range(5)}

        y_pred = np.argmax(y_proba, axis=1)

        # Para clases con umbral ajustado, si P > umbral → asignar esa clase
        for cls, th in thresholds.items():
            if th != 0.20:  # Solo modificar si el umbral fue ajustado
                mask = y_proba[:, cls] >= th
                y_pred[mask] = cls

        self.tuned_f1 = f1_score(np.zeros_like(y_pred), y_pred, average="macro")  # Se actualiza fuera
        return y_pred


# ======================================================================
# EVALUACIÓN COMPLETA
# ======================================================================

def evaluate_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray,
    thresholds: Optional[Dict[int, float]] = None,
) -> Dict[str, Any]:
    """
    Evaluación completa: métricas por clase, matriz de confusión, AUPRC,
    reporte de clasificación.
    """
    results = {}

    # Métricas globales
    results["f1_macro"] = f1_score(y_true, y_pred, average="macro")
    results["f1_weighted"] = f1_score(y_true, y_pred, average="weighted")
    results["precision_macro"] = precision_score(y_true, y_pred, average="macro", zero_division=0)
    results["recall_macro"] = recall_score(y_true, y_pred, average="macro", zero_division=0)
    results["accuracy"] = np.mean(y_true == y_pred)

    # AUC-ROC
    try:
        results["auc_roc_macro"] = roc_auc_score(y_true, y_proba, average="macro")
    except ValueError:
        results["auc_roc_macro"] = 0.0

    # AUPRC (macro)
    try:
        results["auprc_macro"] = average_precision_score(
            np.eye(5)[y_true], y_proba, average="macro"
        )
    except ValueError:
        results["auprc_macro"] = 0.0

    # Por clase
    for i, label in enumerate(CLASS_LABELS):
        mask_true = (y_true == i)
        mask_pred = (y_pred == i)

        results[f"precision_{label}"] = precision_score(mask_true, mask_pred, zero_division=0)
        results[f"recall_{label}"] = recall_score(mask_true, mask_pred, zero_division=0)
        results[f"f1_{label}"] = f1_score(mask_true, mask_pred, zero_division=0)

        # Soporte (número de muestras reales)
        results[f"support_{label}"] = int(mask_true.sum())

    # Matriz de confusión
    results["confusion_matrix"] = confusion_matrix(y_true, y_pred).tolist()

    # Reporte de clasificación
    results["classification_report"] = classification_report(
        y_true, y_pred, target_names=CLASS_LABELS, zero_division=0
    )

    # Umbrales
    if thresholds:
        results["thresholds"] = thresholds

    return results


def print_evaluation_report(results: Dict[str, Any]):
    """Imprime un reporte de evaluación formateado."""
    print("\n" + "=" * 70)
    print("  EVALUACIÓN FINAL DEL MODELO")
    print("=" * 70)

    print(f"\n  Global:")
    print(f"    F1 Macro:     {results['f1_macro']:.4f}")
    print(f"    F1 Weighted:  {results['f1_weighted']:.4f}")
    print(f"    Precision:    {results['precision_macro']:.4f}")
    print(f"    Recall:       {results['recall_macro']:.4f}")
    print(f"    Accuracy:     {results['accuracy']:.4f}")
    print(f"    AUC-ROC:      {results['auc_roc_macro']:.4f}")
    print(f"    AUPRC:        {results['auprc_macro']:.4f}")

    print(f"\n  Por Clase:")
    print(f"    {'Clase':<8} {'Precision':<10} {'Recall':<10} {'F1':<10} {'Soporte':<8}")
    print(f"    {'-'*45}")
    for label in CLASS_LABELS:
        print(
            f"    {label:<8} "
            f"{results[f'precision_{label}']:<10.4f} "
            f"{results[f'recall_{label}']:<10.4f} "
            f"{results[f'f1_{label}']:<10.4f} "
            f"{results[f'support_{label}']:<8}"
        )

    print(f"\n  Matriz de Confusión:")
    cm = np.array(results["confusion_matrix"])
    print(f"    {'':>6} {'I':>6} {'II':>6} {'III':>6} {'IV':>6} {'V':>6}")
    for i, label in enumerate(CLASS_LABELS):
        print(f"    {label:>6} " + " ".join(f"{cm[i][j]:>6}" for j in range(5)))

    print("=" * 70)
