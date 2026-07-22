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
# Constantes del modelo NLP usado en entrenamiento (Early Fusion)
# ---------------------------------------------------------------------------
NLP_MODEL_KEY = "multilingual"  # mismo que run_pipeline.py
NLP_EMBEDDING_DIM = 384  # sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# Número total de features esperadas por el modelo Early Fusion
# = features estructuradas + embeddings NLP
# El modelo actual (v20260720_224350) tiene 3 struct + 384 NLP = 387
EXPECTED_STRUCT_FEATURES = 3  # edad, sexo_Desconocido, regimen_salud_Desconocido

# Orden real de las features estructuradas tras el pipeline de entrenamiento
# (limpieza.py: X_num → X_cat → X_bin, luego hstack)
STRUCT_FEATURE_ORDER = ["edad", "sexo_Desconocido", "regimen_salud_Desconocido"]

# Mapeo de columnas categóricas → índice en el encoder
CAT_ENCODER_COLS = ["sexo", "regimen_salud"]

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
        self._nlp_embedder = None  # Carga lazy del NLPEmbedder (BERT)
        self._nlp_available = None  # True/False/None (aún no verificado)

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

            # Inicializar SHAP Explainer con TODAS las features (estructuradas + NLP)
            try:
                import shap
                # Construir la lista completa de feature names (estructuradas + NLP)
                full_feature_names = list(self.feature_names)  # 3 estructuradas
                # Agregar nombres genéricos para las features NLP
                n_nlp_features = NLP_EMBEDDING_DIM  # 384
                for i in range(n_nlp_features):
                    full_feature_names.append(f"nlp_dim_{i}")
                self.shap_explainer = SHAPExplainer(self.model, full_feature_names)
                logger.info(
                    f"  SHAP TreeExplainer inicializado (lazy) con "
                    f"{len(full_feature_names)} features"
                )
            except ImportError:
                logger.warning("  SHAP no disponible. La explicabilidad estará limitada.")
                self.shap_explainer = None

            self.model_loaded = True
            self.error_message = None
            logger.info(
                f"  ✓ Modelo cargado: {self.model_name} v{self.model_version} "
                f"({len(self.feature_names)} features)"
            )

            # Precargar NLP embedder en segundo plano para que la primera
            # predicción sea rápida (evita los ~12s de carga lazy de BERT)
            self._prewarm_nlp()

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
            # 1. Construir features estructuradas (3 dims) aplicando scaler/encoder
            X_struct = self._build_structured_features(clinical_data)
            n_struct = X_struct.shape[1]

            # 2. Generar embeddings NLP (384 dims) para el motivo de consulta
            X_nlp = self._generate_nlp_features(motivo_texto or "")
            n_nlp = X_nlp.shape[1]

            # 3. Concatenar → vector completo (387 dims para Early Fusion)
            X_final = np.hstack([X_struct, X_nlp])

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
                # Campos que espera el router (PredictResponse schema)
                "nivel_predicho": nivel_sugerido,
                "nivel_codigo": y_pred_idx,
                "probabilidades": probabilidades,
                "tiempo_inferencia_ms": round(tiempo * 1000, 2),
                "modelo_version": self.model_version,
                "shap_disponible": self.shap_explainer is not None,
                # Campos adicionales para depuración / Streamlit
                "nivel_sugerido": nivel_sugerido,
                "confianza": confianza,
                "tiempo_inferencia_s": tiempo,
                "version_modelo": self.model_version,
                "modelo_nombre": self.model_name,
                "n_features_struct": n_struct,
                "n_features_nlp": n_nlp,
                "error": None,
            }

            logger.info(
                f"  Predicción: Nivel {nivel_sugerido} "
                f"({confianza:.0%}) en {tiempo}s "
                f"[struct={n_struct}, nlp={n_nlp}]"
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
            # Construir vector completo (usando misma lógica que predict)
            X_struct = self._build_structured_features(clinical_data)
            X_nlp = self._generate_nlp_features(motivo_texto or "")
            X_final = np.hstack([X_struct, X_nlp])

            # Inicializar SHAP si es necesario
            if self.shap_explainer.explainer is None:
                self.shap_explainer.fit(X_final.reshape(1, -1), max_samples=100)

            # Explicar predicción individual
            explanation = self.shap_explainer.explain_single(X_final)

            # Traducir a lenguaje clínico y enriquecer
            enriched = self._enrich_explanation(explanation, clinical_data)

            # Agregar campos requeridos por el router (ExplainResponse schema)
            enriched["nivel_predicho"] = explanation.get("class_predicted", "?")
            enriched["shap_disponible"] = True
            enriched["fallback"] = False

            return enriched

        except Exception as e:
            logger.exception(f"Error en SHAP: {e}")
            return {
                "error": f"Error generando explicación: {str(e)}",
                "nivel_predicho": None,
                "shap_disponible": False,
                "fallback": True,
                "top_features_fallback": self._feature_importance_fallback(clinical_data),
            }

    # ------------------------------------------------------------------
    # Construcción del vector de features estructuradas (3 dims)
    # ------------------------------------------------------------------
    def _build_structured_features(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Construye el vector de features estructuradas (3 columnas)
        aplicando el scaler y encoder del entrenamiento sobre los datos crudos.

        Orden de columnas: [edad_scaled, sexo_encoded, regimen_salud_encoded]

        Esto replica exactamente la transformación del pipeline de entrenamiento:
          limpieza.py: X_num (scaler) → X_cat (encoder) → X_bin → hstack
        """
        import warnings

        # 1. Feature numérica: edad (aplicar scaler)
        edad_raw = float(data.get("edad", 0) or 0)
        edad_arr = np.array([[edad_raw]])
        if self.scaler is not None:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                edad_scaled = self.scaler.transform(edad_arr)[0, 0]
        else:
            edad_scaled = edad_raw

        # 2. Features categóricas: sexo, regimen_salud (aplicar encoder)
        sexo_val = str(data.get("sexo", "Desconocido") or "Desconocido")
        regimen_val = str(data.get("regimen_salud", "Desconocido") or "Desconocido")

        if self.encoder is not None:
            cat_arr = np.array([[sexo_val, regimen_val]])
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    cat_encoded = self.encoder.transform(cat_arr)[0]
            except Exception:
                # Fallback: si el encoder falla, usar zeros
                cat_encoded = np.zeros(2)
        else:
            cat_encoded = np.zeros(2)

        # 3. Construir vector en el orden correcto:
        #    [edad, sexo_Desconocido, regimen_salud_Desconocido]
        result = np.array([
            edad_scaled,
            float(cat_encoded[0]) if len(cat_encoded) > 0 else 0.0,
            float(cat_encoded[1]) if len(cat_encoded) > 1 else 0.0,
        ]).reshape(1, -1)

        return result

    # ------------------------------------------------------------------
    # Generación de embeddings NLP (384 dims, BERT multilingual)
    # ------------------------------------------------------------------
    def _generate_nlp_features(self, texto: str) -> np.ndarray:
        """
        Genera embeddings NLP de 384 dimensiones usando el mismo modelo
        BERT multilingual del entrenamiento (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2).

        Si el modelo NLP no está disponible, usa un fallback TF-IDF de 384 dimensiones
        para mantener la compatibilidad dimensional con el modelo Early Fusion.
        """
        # Intentar cargar el NLP embedder lazy
        if self._nlp_embedder is None and self._nlp_available is None:
            self._nlp_available = self._try_load_nlp_embedder()

        # Usar BERT si está disponible
        if self._nlp_available and self._nlp_embedder is not None:
            try:
                embeddings = self._nlp_embedder.generate_embeddings([texto], fit_tfidf=False)
                # Asegurar que tenga la dimensión correcta
                if embeddings.shape[1] != NLP_EMBEDDING_DIM:
                    logger.warning(
                        f"  NLP dim mismatch: esperado {NLP_EMBEDDING_DIM}, "
                        f"obtenido {embeddings.shape[1]}. Ajustando..."
                    )
                    embeddings = self._pad_or_truncate(embeddings, NLP_EMBEDDING_DIM)
                return embeddings
            except Exception as e:
                logger.warning(f"  Error generando embeddings BERT: {e}. Usando fallback.")

        # Fallback: TF-IDF con 384 dimensiones
        return self._generate_tfidf_fallback(texto, NLP_EMBEDDING_DIM)

    def _prewarm_nlp(self):
        """Precarga el modelo NLP en segundo plano para evitar latencia en la primera predicción."""
        try:
            import threading
            def _load():
                self._try_load_nlp_embedder()
                if self._nlp_available:
                    # Generar un embedding dummy para calentar el modelo
                    try:
                        self._nlp_embedder.generate_embeddings(["calentamiento"], fit_tfidf=False)
                    except Exception:
                        pass
            t = threading.Thread(target=_load, daemon=True)
            t.start()
            logger.info("  NLP: precarga iniciada en segundo plano")
        except Exception as e:
            logger.warning(f"  NLP: no se pudo iniciar precarga ({e})")

    def _try_load_nlp_embedder(self) -> bool:
        """Intenta cargar el NLPEmbedder de forma lazy. Retorna True si tuvo éxito."""
        try:
            from src.features.nlp_embeddings import NLPEmbedder
            self._nlp_embedder = NLPEmbedder(
                model_name=NLP_MODEL_KEY,
                use_gpu=False,
                batch_size=1,
            )
            # Forzar carga del modelo
            self._nlp_embedder._ensure_loaded()
            if getattr(self._nlp_embedder, "_fallback_mode", False):
                logger.info("  NLP: usando modo fallback TF-IDF (BERT no disponible)")
                self._nlp_embedder = None
                return False
            logger.info(f"  NLP: BERT multilingual cargado ({NLP_EMBEDDING_DIM} dims)")
            return True
        except ImportError as e:
            logger.warning(f"  NLP: transformers no instalado ({e}). Usando fallback TF-IDF.")
            return False
        except Exception as e:
            logger.warning(f"  NLP: error al cargar BERT ({e}). Usando fallback TF-IDF.")
            return False

    def _generate_tfidf_fallback(self, texto: str, target_dim: int) -> np.ndarray:
        """Fallback TF-IDF que produce exactamente target_dim features."""
        from sklearn.feature_extraction.text import TfidfVectorizer

        if not hasattr(self, "_tfidf_vectorizer"):
            self._tfidf_vectorizer = TfidfVectorizer(
                max_features=target_dim,
                ngram_range=(1, 2),
            )

        texto_limpio = str(texto).strip() if texto else "sin motivo"
        if not texto_limpio:
            texto_limpio = "sin motivo"

        try:
            embedding = self._tfidf_vectorizer.fit_transform([texto_limpio]).toarray()
        except Exception:
            embedding = np.zeros((1, 1))

        return self._pad_or_truncate(embedding, target_dim)

    def _pad_or_truncate(self, arr: np.ndarray, target_dim: int) -> np.ndarray:
        """Ajusta un array 2D a la dimensión objetivo."""
        current = arr.shape[1]
        if current == target_dim:
            return arr
        elif current < target_dim:
            # Pad con ceros
            padding = np.zeros((arr.shape[0], target_dim - current))
            return np.hstack([arr, padding])
        else:
            # Truncar
            return arr[:, :target_dim]

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
            # El router espera "top_features", copiamos de "top_contributors"
            if "top_features" not in enriched:
                enriched["top_features"] = enriched["top_contributors"]

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
