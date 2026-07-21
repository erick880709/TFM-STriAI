"""
Servicio de Inferencia IA — TT-E4-01, HU-E4-01, HU-E4-02.
Carga el modelo serializado, preprocesa datos clínicos, ejecuta predicción
multimodal y genera explicación SHAP en lenguaje clínico.

Referencia: Documento de Arquitectura §7, §14, RNP-001 (< 3s).
"""
import sys
import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple
import numpy as np
import pandas as pd

# Agregar raíz del repo al path para acceder a src/ (paquete del pipeline ML)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # TFM-FINAL/
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.serving.serialize import ModelSerializer
from src.data.limpieza import NUMERIC_COLS, CATEGORICAL_COLS, BINARY_COLS, RANGOS_FISIOLOGICOS
from src.evaluation.shap_benchmarks import SHAPExplainer, NOMBRES_CLINICOS, CLASS_LABELS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
# Resolver ruta a models/ de forma robusta (prueba múltiples ubicaciones)
_MODULE_DIR = Path(__file__).resolve().parent  # .../app/services/
_APP_DIR = _MODULE_DIR.parent.parent  # sistema-triaje-ia/
_REPO_ROOT = _APP_DIR.parent  # TFM-FINAL/

# Intentar varias ubicaciones en orden de preferencia
_MODEL_CANDIDATES = [
    _REPO_ROOT / "models",                    # TFM-FINAL/models/
    _APP_DIR / "models",                       # sistema-triaje-ia/models/
    _MODULE_DIR.parent.parent.parent.parent / "models",  # fallback original
]
MODELS_DIR = next((d for d in _MODEL_CANDIDATES if d.exists()), _MODEL_CANDIDATES[0])

# Variables requeridas para inferencia
REQUIRED_FIELDS = [
    "edad", "sexo", "temperatura", "frecuencia_cardiaca",
    "frecuencia_respiratoria", "saturacion_o2",
    "presion_sistolica", "presion_diastolica",
]

# Variables derivadas que se calculan
DERIVED_FIELDS = ["pam", "shock_index", "qsofa_score", "imc"]

# Traducción de nombres de columnas DB → feature names del modelo
DB_TO_FEATURE_MAP = {
    "edad": "edad",
    "sexo": "sexo",
    "temperatura": "temperatura",
    "frecuencia_cardiaca": "frecuencia_cardiaca",
    "frecuencia_respiratoria": "frecuencia_respiratoria",
    "saturacion_o2": "saturacion_o2",
    "presion_sistolica": "presion_sistolica",
    "presion_diastolica": "presion_diastolica",
    "peso": "peso",
    "talla": "talla",
    "imc": "imc",
    "escala_dolor": "escala_dolor",
    "glasgow": "glasgow",
    "via_llegada": "via_llegada",
    "regimen_salud": "regimen_salud",
    "nivel_conciencia": "nivel_conciencia",
    "motivo_categoria": "motivo_categoria",
    "diabetes": "diabetes",
    "hipertension": "hipertension",
    "enfermedad_renal": "enfermedad_renal",
    "embarazo": "embarazo",
    "cancer": "cancer",
    "cardiopatias": "cardiopatias",
    "enfermedad_pulmonar": "enfermedad_pulmonar",
    "cirugias_recientes": "cirugias_recientes",
    "episodios_previos": "episodios_previos",
}


class InferenceService:
    """
    Servicio de inferencia IA para la demo Streamlit.
    Carga el modelo serializado al iniciar y expone predict() y explain().
    """

    def __init__(self, models_dir: Optional[str] = None):
        """
        Inicializa el servicio cargando el modelo activo.

        Args:
            models_dir: Directorio donde están los modelos serializados.
        """
        self.models_dir = Path(models_dir) if models_dir else MODELS_DIR
        self.model_loaded = False
        self.model = None
        self.scaler = None
        self.encoder = None
        self.feature_names = []
        self.thresholds = {}
        self.metadata = {}
        self.shap_explainer = None
        self.model_version = "N/A"
        self.model_name = "N/A"
        self.error_message = None

    # ------------------------------------------------------------------
    # TT-E4-01: Carga del modelo
    # ------------------------------------------------------------------
    def load_model(self) -> bool:
        """
        Carga el modelo activo desde models/.
        Retorna True si la carga fue exitosa.
        """
        try:
            if not self.models_dir.exists():
                self.error_message = f"Directorio de modelos no encontrado: {self.models_dir}"
                logger.warning(self.error_message)
                return False

            # Buscar modelo activo
            active_file = self.models_dir / "active_version.txt"
            if not active_file.exists():
                # Buscar el directorio de modelo más reciente
                model_dirs = sorted(
                    [d for d in self.models_dir.iterdir()
                     if d.is_dir() and (d / "model.joblib").exists()],
                    key=lambda d: d.stat().st_mtime,
                    reverse=True,
                )
                if not model_dirs:
                    self.error_message = (
                        "No se encontró ningún modelo serializado en models/. "
                        "Ejecute primero el pipeline de entrenamiento (run_pipeline.py)."
                    )
                    logger.warning(self.error_message)
                    return False
                model_dir = str(model_dirs[0])
            else:
                with open(active_file, "r") as f:
                    active_version = f.read().strip()
                model_dir = str(self.models_dir / active_version)

            logger.info(f"Cargando modelo desde: {model_dir}")

            artifacts = ModelSerializer.load(model_dir)

            self.model = artifacts.get("model")
            self.scaler = artifacts.get("scaler")
            self.encoder = artifacts.get("encoder")
            self.feature_names = artifacts.get("feature_names", [])
            self.thresholds = artifacts.get("thresholds", {})
            self.metadata = artifacts.get("metadata", {})

            if self.model is None:
                self.error_message = "El archivo model.joblib no contiene un modelo válido."
                logger.error(self.error_message)
                return False

            self.model_name = self.metadata.get("model_name", "Desconocido")
            self.model_version = self.metadata.get("version", "N/A")

            # Inicializar SHAP Explainer
            try:
                import shap
                self.shap_explainer = SHAPExplainer(self.model, self.feature_names)
                logger.info("  SHAP TreeExplainer inicializado (lazy)")
            except ImportError:
                logger.warning("  SHAP no disponible. La explicabilidad estará limitada.")
                self.shap_explainer = None

            self.model_loaded = True
            self.error_message = None
            logger.info(
                f"  ✓ Modelo cargado: {self.model_name} v{self.model_version} "
                f"({len(self.feature_names)} features)"
            )
            return True

        except FileNotFoundError as e:
            self.error_message = f"Archivo de modelo no encontrado: {e}"
            logger.error(self.error_message)
            return False
        except Exception as e:
            self.error_message = f"Error al cargar el modelo: {e}"
            logger.exception(self.error_message)
            return False

    # ------------------------------------------------------------------
    # HU-E4-01: Inferencia
    # ------------------------------------------------------------------
    def predict(
        self,
        clinical_data: Dict[str, Any],
        motivo_texto: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ejecuta la inferencia multimodal sobre datos clínicos.

        Args:
            clinical_data: Dict con campos clínicos (edad, sexo, temperatura, etc.).
            motivo_texto: Texto libre del motivo de consulta (opcional).

        Returns:
            Dict con:
                - nivel_sugerido: str (I-V)
                - probabilidades: Dict[str, float]
                - confianza: float
                - tiempo_inferencia_s: float
                - version_modelo: str
                - error: str (si falló)
        """
        if not self.model_loaded:
            return {"error": "Modelo no cargado. Intente recargar la página.", "nivel_sugerido": None}

        t0 = time.time()

        try:
            # 1. Construir vector de features estructuradas
            X_struct = self._build_feature_vector(clinical_data)

            # 2. Normalizar y codificar (reutilizando scaler/encoder del entrenamiento)
            X_processed = self._preprocess(X_struct)

            # 3. Generar embeddings NLP si hay texto
            X_final = X_processed
            if motivo_texto and motivo_texto.strip():
                # Usar fallback TF-IDF o BERT según disponibilidad
                try:
                    X_nlp = self._generate_nlp_features(motivo_texto)
                    X_final = np.hstack([X_processed, X_nlp])
                except Exception as e:
                    logger.warning(f"  NLP no disponible, usando solo features estructuradas: {e}")

            # 4. Predecir
            if hasattr(self.model, "predict_proba"):
                y_proba = self.model.predict_proba(X_final)[0]
            else:
                y_proba = np.zeros(5)
                y_pred = self.model.predict(X_final)[0]
                y_proba[int(y_pred)] = 1.0

            # 5. Aplicar umbrales optimizados (si existen)
            if self.thresholds:
                y_pred_idx = self._apply_thresholds(y_proba)
            else:
                y_pred_idx = int(np.argmax(y_proba))

            nivel_sugerido = CLASS_LABELS[y_pred_idx]
            confianza = float(y_proba[y_pred_idx])
            tiempo = round(time.time() - t0, 3)

            # Construir dict de probabilidades
            probabilidades = {
                CLASS_LABELS[i]: round(float(y_proba[i]), 4)
                for i in range(5)
            }

            result = {
                "nivel_sugerido": nivel_sugerido,
                "probabilidades": probabilidades,
                "confianza": confianza,
                "tiempo_inferencia_s": tiempo,
                "version_modelo": self.model_version,
                "modelo_nombre": self.model_name,
                "error": None,
            }

            logger.info(
                f"  Predicción: Nivel {nivel_sugerido} "
                f"({confianza:.0%}) en {tiempo}s"
            )

            return result

        except Exception as e:
            logger.exception(f"Error en inferencia: {e}")
            return {
                "error": f"Error en predicción: {str(e)}",
                "nivel_sugerido": None,
                "tiempo_inferencia_s": round(time.time() - t0, 3),
            }

    # ------------------------------------------------------------------
    # HU-E4-02: Explicación SHAP
    # ------------------------------------------------------------------
    def explain(
        self,
        clinical_data: Dict[str, Any],
        motivo_texto: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Genera explicación SHAP para una predicción.

        Returns:
            Dict con top_features, shap_values por clase, etc.
        """
        if not self.model_loaded:
            return {"error": "Modelo no cargado."}

        if self.shap_explainer is None:
            return {
                "error": "SHAP no disponible. Instale: pip install shap",
                "top_features_fallback": self._feature_importance_fallback(clinical_data),
            }

        try:
            # Construir vector
            X_struct = self._build_feature_vector(clinical_data)
            X_processed = self._preprocess(X_struct)

            if motivo_texto and motivo_texto.strip():
                try:
                    X_nlp = self._generate_nlp_features(motivo_texto)
                    X_final = np.hstack([X_processed, X_nlp])
                except Exception:
                    X_final = X_processed
            else:
                X_final = X_processed

            # Inicializar SHAP si es necesario
            if self.shap_explainer.explainer is None:
                self.shap_explainer.fit(X_final.reshape(1, -1), max_samples=100)

            # Explicar predicción individual
            explanation = self.shap_explainer.explain_single(X_final)

            # Traducir a lenguaje clínico y enriquecer
            enriched = self._enrich_explanation(explanation, clinical_data)

            return enriched

        except Exception as e:
            logger.exception(f"Error en SHAP: {e}")
            return {
                "error": f"Error generando explicación: {str(e)}",
                "top_features_fallback": self._feature_importance_fallback(clinical_data),
            }

    # ------------------------------------------------------------------
    # Construcción del vector de features
    # ------------------------------------------------------------------
    def _build_feature_vector(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Construye el vector de features estructuradas a partir de datos clínicos.
        Replica la lógica de src/data/limpieza.py para evitar training-serving skew.
        """
        features = {}

        # Mapear campos clínicos a features del modelo
        for db_col, feat_col in DB_TO_FEATURE_MAP.items():
            if db_col in data and data[db_col] is not None:
                features[feat_col] = data[db_col]

        # Calcular features derivadas
        pas = features.get("presion_sistolica", 0)
        pad = features.get("presion_diastolica", 0)
        fc = features.get("frecuencia_cardiaca", 0)
        fr = features.get("frecuencia_respiratoria", 0)
        glasgow = features.get("glasgow", 15)

        # PAM
        if pas and pad:
            features["pam"] = (pas + 2 * pad) / 3

        # Shock Index
        features["shock_index"] = fc / max(pas, 1)

        # qSOFA
        features["qsofa_score"] = (
            (glasgow < 15) + (fr >= 22) + (pas <= 100)
        )

        # IMC
        peso = data.get("peso") or data.get("peso_kg")
        talla = data.get("talla") or data.get("talla_cm")
        if peso and talla and talla > 0:
            features["imc"] = peso / ((talla / 100) ** 2)

        # Build vector in correct order
        vec = []
        for fname in self.feature_names:
            val = features.get(fname, 0)
            # Handle categorical (encoded) features
            if isinstance(val, str):
                val = 0  # Categorical features are handled by encoder
            vec.append(float(val) if val is not None else 0.0)

        return np.array(vec).reshape(1, -1)

    def _preprocess(self, X: np.ndarray) -> np.ndarray:
        """Aplica scaler y encoder del entrenamiento."""
        # Extraer columnas numéricas, categóricas, derivadas
        n_numeric = len([c for c in NUMERIC_COLS if c in self.feature_names])
        n_derived = len([c for c in DERIVED_FIELDS if c in self.feature_names])

        numeric_fields = NUMERIC_COLS + DERIVED_FIELDS
        cat_fields = [c for c in CATEGORICAL_COLS if c in self.feature_names]

        # Reconstruir matriz para scaler
        numeric_indices = [i for i, f in enumerate(self.feature_names)
                          if f in numeric_fields]
        categorical_indices = [i for i, f in enumerate(self.feature_names)
                               if f in cat_fields]

        X_num = X[:, numeric_indices] if numeric_indices else X[:, :1]
        X_cat = X[:, categorical_indices] if categorical_indices else X[:, :1]

        # Aplicar scaler
        if self.scaler is not None and numeric_indices:
            X_num = self.scaler.transform(X_num)

        # Aplicar encoder
        if self.encoder is not None and categorical_indices:
            try:
                X_cat = self.encoder.transform(X_cat)
            except Exception:
                X_cat = np.zeros((X.shape[0], 1))

        # Reconstruir en orden original
        result_parts = []
        ni, ci = 0, 0
        for i, fname in enumerate(self.feature_names):
            if fname in numeric_fields and ni < X_num.shape[1]:
                result_parts.append(X_num[:, ni:ni+1])
                ni += 1
            elif fname in cat_fields and ci < X_cat.shape[1]:
                result_parts.append(X_cat[:, ci:ci+1])
                ci += 1
            else:
                result_parts.append(X[:, i:i+1])

        return np.hstack(result_parts) if result_parts else X

    def _generate_nlp_features(self, texto: str) -> np.ndarray:
        """Genera features NLP para un texto clínico (fallback TF-IDF)."""
        from sklearn.feature_extraction.text import TfidfVectorizer

        # TF-IDF rápido con 256 features
        vectorizer = TfidfVectorizer(max_features=256, ngram_range=(1, 2))
        embedding = vectorizer.fit_transform([texto]).toarray()
        return embedding

    def _apply_thresholds(self, y_proba: np.ndarray) -> int:
        """Aplica umbrales optimizados para priorizar Recall I-II."""
        y_pred = int(np.argmax(y_proba))
        for cls_idx, th in self.thresholds.items():
            cls_idx = int(cls_idx)
            if y_proba[cls_idx] >= th:
                y_pred = cls_idx
        return y_pred

    # ------------------------------------------------------------------
    # Enriquecimiento de explicación
    # ------------------------------------------------------------------
    def _enrich_explanation(
        self, explanation: Dict, clinical_data: Dict
    ) -> Dict:
        """Traduce SHAP a lenguaje clínico y agrega contexto MTS."""
        enriched = dict(explanation)

        # Traducir nombres de features
        if "top_contributors" in enriched:
            for item in enriched["top_contributors"]:
                item["nombre_clinico"] = NOMBRES_CLINICOS.get(
                    item.get("feature", ""), item.get("feature", "")
                )

        # Comparación con MTS (Manchester Triage System) simplificada
        enriched["mts_comparison"] = self._mts_comparison(clinical_data)

        return enriched

    def _mts_comparison(self, data: Dict) -> Dict:
        """
        Compara signos vitales con criterios MTS simplificados.
        Retorna coincidencias para contexto clínico.
        """
        matches = []
        spo2 = data.get("saturacion_o2", 100)
        fr = data.get("frecuencia_respiratoria", 16)
        temp = data.get("temperatura", 37)
        fc = data.get("frecuencia_cardiaca", 80)
        pas = data.get("presion_sistolica", 120)
        glasgow = data.get("glasgow", 15)

        if spo2 < 92:
            matches.append(f"SpO₂ {spo2}% → MTS: Nivel I-II (hipoxemia)")
        elif spo2 < 95:
            matches.append(f"SpO₂ {spo2}% → MTS: Nivel II-III (saturación baja)")

        if fr > 25:
            matches.append(f"FR {fr} rpm → MTS: Nivel I-II (dificultad respiratoria)")
        elif fr > 20:
            matches.append(f"FR {fr} rpm → MTS: Nivel III (taquipnea leve)")

        if fc > 120:
            matches.append(f"FC {fc} lpm → MTS: Nivel II (taquicardia)")
        elif fc < 50:
            matches.append(f"FC {fc} lpm → MTS: Nivel II (bradicardia)")

        if pas < 90:
            matches.append(f"PA sistólica {pas} → MTS: Nivel I (shock)")
        elif pas > 180:
            matches.append(f"PA sistólica {pas} → MTS: Nivel II (crisis hipertensiva)")

        if glasgow < 13:
            matches.append(f"Glasgow {glasgow} → MTS: Nivel I (alteración conciencia)")
        elif glasgow < 15:
            matches.append(f"Glasgow {glasgow} → MTS: Nivel II (conciencia alterada)")

        if temp > 41:
            matches.append(f"Temp {temp}°C → MTS: Nivel I (hipertermia extrema)")
        elif temp < 35:
            matches.append(f"Temp {temp}°C → MTS: Nivel II (hipotermia)")

        return {"coincidencias": matches, "total": len(matches)}

    def _feature_importance_fallback(self, data: Dict) -> List[Dict]:
        """
        Fallback: ranking de variables por importancia clínica (sin SHAP).
        Basado en desviación de rangos normales.
        """
        alerts = []
        rangos = {
            "saturacion_o2": (95, 100, "Saturación de O₂", False),
            "frecuencia_respiratoria": (12, 20, "Frecuencia respiratoria", False),
            "frecuencia_cardiaca": (60, 100, "Frecuencia cardíaca", False),
            "temperatura": (36, 37.5, "Temperatura", False),
            "presion_sistolica": (90, 140, "Presión sistólica", False),
            "glasgow": (15, 15, "Escala de Glasgow", True),
        }

        for key, (lo, hi, label, lower_is_worse) in rangos.items():
            val = data.get(key)
            if val is not None:
                if val < lo:
                    deviation = (lo - val) / max(lo, 1)
                    alerts.append({
                        "nombre_clinico": label,
                        "valor": val,
                        "importancia_relativa": round(min(deviation, 1.0), 2),
                        "mensaje": f"{label}: {val} (bajo, normal: {lo}-{hi})",
                    })
                elif val > hi:
                    deviation = (val - hi) / max(hi, 1)
                    alerts.append({
                        "nombre_clinico": label,
                        "valor": val,
                        "importancia_relativa": round(min(deviation, 1.0), 2),
                        "mensaje": f"{label}: {val} (alto, normal: {lo}-{hi})",
                    })

        alerts.sort(key=lambda x: x["importancia_relativa"], reverse=True)
        return alerts[:10]

    # ------------------------------------------------------------------
    # Estado del servicio
    # ------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        """Retorna el estado actual del servicio de inferencia."""
        return {
            "modelo_cargado": self.model_loaded,
            "nombre_modelo": self.model_name,
            "version": self.model_version,
            "n_features": len(self.feature_names),
            "shap_disponible": self.shap_explainer is not None,
            "thresholds": self.thresholds,
            "error": self.error_message,
            "models_dir": str(self.models_dir),
        }


# ---------------------------------------------------------------------------
# Singleton para Streamlit (se inicializa una vez por sesión)
# ---------------------------------------------------------------------------
_inference_service: Optional[InferenceService] = None


def get_inference_service(models_dir: Optional[str] = None) -> InferenceService:
    """Retorna la instancia singleton del servicio de inferencia."""
    global _inference_service
    if _inference_service is None:
        _inference_service = InferenceService(models_dir)
        _inference_service.load_model()
    return _inference_service
