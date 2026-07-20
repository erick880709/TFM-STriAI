"""
Módulo de Entrenamiento — TT-E3-04, TT-E3-05, TT-E3-06.
Entrena 3 baselines unimodales + Early Fusion + Late Fusion.
Referencia: Documento de Arquitectura §11.
"""
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple, Any
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
import xgboost as xgb
import logging
import time

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
N_CLASSES = 5
CLASS_LABELS = ["I", "II", "III", "IV", "V"]
RANDOM_SEED = 42
N_CV_FOLDS = 10

# Niveles de triaje (target)
LEVEL_MAP = {"I": 0, "II": 1, "III": 2, "IV": 3, "V": 4}
LEVEL_MAP_REV = {v: k for k, v in LEVEL_MAP.items()}


# ======================================================================
# MODEL TRAINER — Orquesta todos los entrenamientos
# ======================================================================

class ModelTrainer:
    """
    Entrena y evalúa modelos unimodales y multimodales para triaje.
    """

    def __init__(self, random_seed: int = RANDOM_SEED):
        self.random_seed = random_seed
        self.results: Dict[str, Dict] = {}
        self.models: Dict[str, Any] = {}
        self.best_model_name: Optional[str] = None

    # ==================================================================
    # TT-E3-04: BASELINES UNIMODALES
    # ==================================================================

    def train_baselines(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, Dict]:
        """
        Entrena 3 baselines unimodales (solo features estructuradas).
        Retorna diccionario con métricas de cada modelo.
        """
        logger.info("=== Entrenando Baselines Unimodales ===")

        baselines = {
            "LR (Regresión Logística)": LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=self.random_seed,
            ),
            "RF (Random Forest)": RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                class_weight="balanced",
                random_state=self.random_seed,
                n_jobs=-1,
            ),
            "XGBoost": xgb.XGBClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.05,
                objective="multi:softprob",
                num_class=N_CLASSES,
                eval_metric="mlogloss",
                random_state=self.random_seed,
                verbosity=0,
            ),
        }

        for name, model in baselines.items():
            t0 = time.time()
            logger.info(f"  Entrenando {name}...")

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)

            metrics = _compute_all_metrics(y_test, y_pred, y_proba)
            metrics["train_time_s"] = round(time.time() - t0, 2)
            metrics["model"] = name

            self.results[name] = metrics
            self.models[name] = model

            logger.info(
                f"    {name}: F1={metrics['f1_macro']:.4f}, "
                f"AUC={metrics['auc_roc_macro']:.4f}, "
                f"Recall_I={metrics['recall_per_class']['I']:.4f}, "
                f"Recall_II={metrics['recall_per_class']['II']:.4f}"
            )

        return self.results

    # ==================================================================
    # TT-E3-05: EARLY FUSION
    # ==================================================================

    def train_early_fusion(
        self,
        X_struct_train: np.ndarray,
        X_nlp_train: np.ndarray,
        y_train: np.ndarray,
        X_struct_test: np.ndarray,
        X_nlp_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict:
        """
        Early Fusion: concatena features estructuradas + embeddings NLP,
        entrena XGBoost sobre el vector combinado.
        """
        logger.info("=== Entrenando Early Fusion ===")

        # Concatenar
        X_train_concat = np.hstack([X_struct_train, X_nlp_train])
        X_test_concat = np.hstack([X_struct_test, X_nlp_test])

        logger.info(f"  Features concatenadas: {X_train_concat.shape[1]} dims "
                    f"({X_struct_train.shape[1]} struct + {X_nlp_train.shape[1]} nlp)")

        model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=10,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="multi:softprob",
            num_class=N_CLASSES,
            eval_metric="mlogloss",
            random_state=self.random_seed,
            verbosity=0,
        )

        t0 = time.time()
        model.fit(X_train_concat, y_train)

        y_pred = model.predict(X_test_concat)
        y_proba = model.predict_proba(X_test_concat)

        metrics = _compute_all_metrics(y_test, y_pred, y_proba)
        metrics["train_time_s"] = round(time.time() - t0, 2)
        metrics["model"] = "Early Fusion (XGBoost)"
        metrics["n_features"] = X_train_concat.shape[1]

        self.results["Early Fusion"] = metrics
        self.models["Early Fusion"] = model

        logger.info(
            f"    Early Fusion: F1={metrics['f1_macro']:.4f}, "
            f"AUC={metrics['auc_roc_macro']:.4f}, "
            f"Recall_I={metrics['recall_per_class']['I']:.4f}"
        )

        return metrics

    # ==================================================================
    # TT-E3-06: LATE FUSION
    # ==================================================================

    def train_late_fusion(
        self,
        X_struct_train: np.ndarray,
        X_nlp_train: np.ndarray,
        y_train: np.ndarray,
        X_struct_test: np.ndarray,
        X_nlp_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict:
        """
        Late Fusion: entrena dos submodelos independientes:
          - Submodelo A: XGBoost sobre features estructuradas
          - Submodelo B: LogisticRegression sobre embeddings NLP
          - Meta-modelo: LogisticRegression (stacking) que combina probabilidades de A y B
        """
        logger.info("=== Entrenando Late Fusion ===")

        # --- Submodelo A: XGBoost sobre datos estructurados ---
        logger.info("  Submodelo A: XGBoost (estructurado)")
        submodel_a = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.05,
            objective="multi:softprob",
            num_class=N_CLASSES,
            eval_metric="mlogloss",
            random_state=self.random_seed,
            verbosity=0,
        )
        submodel_a.fit(X_struct_train, y_train)
        proba_a_train = submodel_a.predict_proba(X_struct_train)
        proba_a_test = submodel_a.predict_proba(X_struct_test)

        # --- Submodelo B: LogisticRegression sobre embeddings NLP ---
        logger.info("  Submodelo B: LogisticRegression (NLP)")
        submodel_b = LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=self.random_seed,
        )
        submodel_b.fit(X_nlp_train, y_train)
        proba_b_train = submodel_b.predict_proba(X_nlp_train)
        proba_b_test = submodel_b.predict_proba(X_nlp_test)

        # --- Stacking: meta-modelo (LogisticRegression) ---
        logger.info("  Meta-modelo: LogisticRegression (stacking)")
        X_meta_train = np.hstack([proba_a_train, proba_b_train])
        X_meta_test = np.hstack([proba_a_test, proba_b_test])

        meta_model = LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=self.random_seed,
        )

        t0 = time.time()
        meta_model.fit(X_meta_train, y_train)

        y_pred = meta_model.predict(X_meta_test)
        y_proba = meta_model.predict_proba(X_meta_test)

        metrics = _compute_all_metrics(y_test, y_pred, y_proba)
        metrics["train_time_s"] = round(time.time() - t0, 2)
        metrics["model"] = "Late Fusion (Stacking)"

        self.results["Late Fusion"] = metrics
        self.models["Late Fusion"] = {
            "submodel_a": submodel_a,
            "submodel_b": submodel_b,
            "meta_model": meta_model,
        }

        logger.info(
            f"    Late Fusion: F1={metrics['f1_macro']:.4f}, "
            f"AUC={metrics['auc_roc_macro']:.4f}, "
            f"Recall_I={metrics['recall_per_class']['I']:.4f}"
        )

        return metrics

    # ==================================================================
    # SELECCIÓN DEL MEJOR MODELO
    # ==================================================================

    def select_best_model(self, criterion: str = "f1_macro") -> Tuple[str, Any]:
        """
        Selecciona el mejor modelo según una métrica.
        Prioriza Recall I-II en caso de empate cercano.
        """
        if not self.results:
            raise ValueError("No hay resultados. Ejecute entrenamientos primero.")

        best_name = None
        best_score = -1
        best_recall_i_ii = -1

        for name, metrics in self.results.items():
            score = metrics.get(criterion, 0)
            recall_sum = (
                metrics.get("recall_per_class", {}).get("I", 0) +
                metrics.get("recall_per_class", {}).get("II", 0)
            )

            if score > best_score + 0.005:  # Margen de superioridad
                best_score = score
                best_recall_i_ii = recall_sum
                best_name = name
            elif abs(score - best_score) <= 0.005 and recall_sum > best_recall_i_ii:
                # Empate → priorizar Recall I-II
                best_recall_i_ii = recall_sum
                best_name = name
                best_score = score

        self.best_model_name = best_name
        logger.info(f"Mejor modelo: {best_name} (F1={best_score:.4f}, Recall_I+II={best_recall_i_ii:.4f})")
        return best_name, self.models.get(best_name)

    def get_summary_table(self) -> pd.DataFrame:
        """Retorna tabla comparativa de todos los modelos entrenados."""
        rows = []
        for name, m in self.results.items():
            rows.append({
                "Modelo": name,
                "F1 Macro": f"{m.get('f1_macro', 0):.4f}",
                "Precision": f"{m.get('precision_macro', 0):.4f}",
                "Recall Macro": f"{m.get('recall_macro', 0):.4f}",
                "AUC-ROC": f"{m.get('auc_roc_macro', 0):.4f}",
                "Recall I": f"{m.get('recall_per_class', {}).get('I', 0):.4f}",
                "Recall II": f"{m.get('recall_per_class', {}).get('II', 0):.4f}",
                "Recall III": f"{m.get('recall_per_class', {}).get('III', 0):.4f}",
                "Recall IV": f"{m.get('recall_per_class', {}).get('IV', 0):.4f}",
                "Recall V": f"{m.get('recall_per_class', {}).get('V', 0):.4f}",
                "Tiempo (s)": m.get("train_time_s", 0),
            })
        return pd.DataFrame(rows)


# ======================================================================
# MÉTRICAS
# ======================================================================

def _compute_all_metrics(y_true: np.ndarray, y_pred: np.ndarray,
                         y_proba: np.ndarray) -> Dict:
    """Calcula todas las métricas: globales, por clase, AUC."""
    metrics = {
        "f1_macro": f1_score(y_true, y_pred, average="macro"),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
        "precision_macro": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_true, y_pred, average="macro", zero_division=0),
        "accuracy": np.mean(y_true == y_pred),
    }

    # Por clase
    recall_per_class = {}
    f1_per_class = {}
    for i, label in enumerate(CLASS_LABELS):
        mask = (y_true == i)
        if mask.sum() > 0:
            recall_per_class[label] = recall_score(
                y_true == i, y_pred == i, average="binary", zero_division=0
            )
            f1_per_class[label] = f1_score(
                y_true == i, y_pred == i, average="binary", zero_division=0
            )
        else:
            recall_per_class[label] = 0.0
            f1_per_class[label] = 0.0

    metrics["recall_per_class"] = recall_per_class
    metrics["f1_per_class"] = f1_per_class

    # AUC-ROC (macro, one-vs-rest)
    try:
        metrics["auc_roc_macro"] = roc_auc_score(y_true, y_proba, average="macro")
    except ValueError:
        metrics["auc_roc_macro"] = 0.0

    return metrics


def encode_labels(y: np.ndarray) -> np.ndarray:
    """
    Convierte etiquetas de nivel de triaje (I-V) a índices 0-4.
    Soporta strings y numéricos.
    """
    y_str = np.array([str(v).strip().upper() for v in y])
    # Mapear: 'I'→0, 'II'→1, etc. y también '1'→0, '2'→1, etc.
    encoded = np.zeros(len(y_str), dtype=int) - 1
    for i, label in enumerate(CLASS_LABELS):
        encoded[(y_str == label) | (y_str == str(i + 1))] = i
    if (encoded == -1).any():
        n_unknown = (encoded == -1).sum()
        logger.warning(f"  {n_unknown} etiquetas no reconocidas → asignadas a clase III")
        encoded[encoded == -1] = 2  # Default: Nivel III
    return encoded
