"""
Serialización del Modelo — TT-E3-09.
Guarda el modelo ganador + transformadores (scaler, encoder, tokenizer)
+ metadata.json para carga reproducible en la demo (Épica 4).

Referencia: Documento de Arquitectura §14, RT-002.
"""
import os
import json
import joblib
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"


class ModelSerializer:
    """
    Serializa el modelo ganador y todos sus artefactos asociados
    (scaler, encoder, tokenizer, metadata) para consumo en la demo.
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else MODELS_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Serialización principal
    # ------------------------------------------------------------------
    def serialize(
        self,
        model: Any,
        model_name: str,
        version: str,
        scaler: Any,
        encoder: Any,
        feature_names: list,
        metrics: Dict[str, float],
        thresholds: Optional[Dict[int, float]] = None,
        nlp_model_key: Optional[str] = None,
        extra_artifacts: Optional[Dict[str, Any]] = None,
        description: str = "",
    ) -> str:
        """
        Serializa el modelo completo con todos sus artefactos.
        Retorna la ruta del directorio de salida.
        """
        model_slug = f"{model_name.lower().replace(' ', '_')}_{version}"
        model_dir = self.output_dir / model_slug
        os.makedirs(model_dir, exist_ok=True)

        logger.info(f"Serializando modelo en: {model_dir}")

        # 1. Guardar modelo
        model_path = model_dir / "model.joblib"
        joblib.dump(model, model_path)
        model_hash = self._file_hash(model_path)
        logger.info(f"  Modelo guardado: {model_path} (SHA256: {model_hash[:12]}...)")

        # 2. Guardar scaler
        if scaler is not None:
            scaler_path = model_dir / "scaler.joblib"
            joblib.dump(scaler, scaler_path)
            logger.info(f"  Scaler guardado: {scaler_path}")

        # 3. Guardar encoder
        if encoder is not None:
            encoder_path = model_dir / "encoder.joblib"
            joblib.dump(encoder, encoder_path)
            logger.info(f"  Encoder guardado: {encoder_path}")

        # 4. Guardar feature names
        features_path = model_dir / "feature_names.json"
        with open(features_path, "w", encoding="utf-8") as f:
            json.dump({"feature_names": feature_names}, f, indent=2, ensure_ascii=False)
        logger.info(f"  Feature names guardados ({len(feature_names)} features)")

        # 5. Guardar thresholds (si existen)
        if thresholds:
            th_path = model_dir / "thresholds.json"
            # Convertir keys de int a str para JSON
            th_serializable = {str(k): v for k, v in thresholds.items()}
            with open(th_path, "w", encoding="utf-8") as f:
                json.dump(th_serializable, f, indent=2)
            logger.info(f"  Umbrales guardados: {thresholds}")

        # 6. Generar metadata.json
        metadata = self._build_metadata(
            model_name=model_name,
            version=version,
            model_hash=model_hash,
            feature_names=feature_names,
            metrics=metrics,
            thresholds=thresholds,
            nlp_model_key=nlp_model_key,
            description=description,
        )

        metadata_path = model_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"  Metadata guardada: {metadata_path}")

        # 7. Guardar artefactos extra
        if extra_artifacts:
            for name, artifact in extra_artifacts.items():
                art_path = model_dir / f"{name}.joblib"
                joblib.dump(artifact, art_path)
                logger.info(f"  Artefacto extra '{name}' guardado: {art_path}")

        # 8. Crear archivo de versión activa
        self._set_active_version(model_slug, model_dir)

        logger.info(f"  ✓ Modelo serializado exitosamente en {model_dir}")
        return str(model_dir)

    # ------------------------------------------------------------------
    # Carga (para la demo — Épica 4)
    # ------------------------------------------------------------------
    @staticmethod
    def load(model_dir: str) -> Dict[str, Any]:
        """
        Carga un modelo serializado con todos sus artefactos.
        Retorna un dict con model, scaler, encoder, feature_names, metadata, thresholds.
        """
        model_path = Path(model_dir)

        result = {}

        # Cargar modelo
        result["model"] = joblib.load(model_path / "model.joblib")

        # Cargar scaler
        scaler_path = model_path / "scaler.joblib"
        if scaler_path.exists():
            result["scaler"] = joblib.load(scaler_path)

        # Cargar encoder
        encoder_path = model_path / "encoder.joblib"
        if encoder_path.exists():
            result["encoder"] = joblib.load(encoder_path)

        # Cargar feature names
        features_path = model_path / "feature_names.json"
        if features_path.exists():
            with open(features_path, "r", encoding="utf-8") as f:
                result["feature_names"] = json.load(f).get("feature_names", [])

        # Cargar thresholds
        th_path = model_path / "thresholds.json"
        if th_path.exists():
            with open(th_path, "r", encoding="utf-8") as f:
                th_raw = json.load(f)
                result["thresholds"] = {int(k): v for k, v in th_raw.items()}

        # Cargar metadata
        meta_path = model_path / "metadata.json"
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                result["metadata"] = json.load(f)

        logger.info(f"Modelo cargado desde {model_dir}")
        return result

    @staticmethod
    def load_active_model(models_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Carga la versión activa del modelo (según active_version.txt).
        """
        base = Path(models_dir) if models_dir else MODELS_DIR
        active_file = base / "active_version.txt"

        if not active_file.exists():
            # Intentar cargar el último modelo disponible
            model_dirs = sorted(
                [d for d in base.iterdir() if d.is_dir() and (d / "model.joblib").exists()],
                key=lambda d: d.stat().st_mtime,
                reverse=True,
            )
            if model_dirs:
                logger.info(f"Cargando último modelo: {model_dirs[0].name}")
                return ModelSerializer.load(str(model_dirs[0]))
            raise FileNotFoundError(f"No se encontró modelo activo en {base}")

        with open(active_file, "r") as f:
            active_version = f.read().strip()

        model_dir = base / active_version
        if not model_dir.exists():
            raise FileNotFoundError(f"Modelo activo {active_version} no encontrado en {base}")

        logger.info(f"Cargando modelo activo: {active_version}")
        return ModelSerializer.load(str(model_dir))

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    def _build_metadata(
        self,
        model_name: str,
        version: str,
        model_hash: str,
        feature_names: list,
        metrics: Dict[str, float],
        thresholds: Optional[Dict[int, float]] = None,
        nlp_model_key: Optional[str] = None,
        description: str = "",
    ) -> dict:
        """Construye el diccionario de metadata."""
        return {
            "model_name": model_name,
            "version": version,
            "serialized_at": datetime.utcnow().isoformat() + "Z",
            "model_hash_sha256": model_hash,
            "n_features": len(feature_names),
            "feature_names": feature_names,
            "metrics": {
                "f1_macro": metrics.get("f1_macro"),
                "f1_weighted": metrics.get("f1_weighted"),
                "precision_macro": metrics.get("precision_macro"),
                "recall_macro": metrics.get("recall_macro"),
                "accuracy": metrics.get("accuracy"),
                "auc_roc_macro": metrics.get("auc_roc_macro"),
                "auprc_macro": metrics.get("auprc_macro", metrics.get("auprc_macro_avg")),
            },
            "thresholds": {str(k): v for k, v in (thresholds or {}).items()},
            "nlp_model_key": nlp_model_key,
            "framework": "scikit-learn + XGBoost",
            "description": description,
            "class_labels": ["I", "II", "III", "IV", "V"],
        }

    def _set_active_version(self, version_slug: str, model_dir: Path):
        """Registra esta versión como la activa."""
        active_file = self.output_dir / "active_version.txt"
        with open(active_file, "w") as f:
            f.write(version_slug)
        logger.info(f"  Versión activa: {version_slug}")

    @staticmethod
    def _file_hash(filepath: Path) -> str:
        """Calcula SHA256 de un archivo."""
        sha = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
        return sha.hexdigest()
