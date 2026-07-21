"""
Servicio de Gestión de Modelos IA.
Extrae las consultas SQL desde model_management_page.py para exponer CRUD de modelos vía API REST.
"""
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from app.data.database import get_connection


class ModelManagementService:
    """Gestiona el registro, activación y escaneo de modelos de ML."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    # ------------------------------------------------------------------
    # Listar modelos registrados en BD
    # ------------------------------------------------------------------
    def list_models(self) -> List[Dict]:
        """Retorna todos los modelos registrados en la BD, ordenados por fecha descendente."""
        conn = get_connection(self.db_path)
        try:
            rows = conn.execute(
                "SELECT * FROM Modelo ORDER BY FechaRegistro DESC"
            ).fetchall()
            return [dict(r) for r in rows] if rows else []
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Obtener modelo activo
    # ------------------------------------------------------------------
    def get_active_model(self) -> Optional[Dict]:
        """Retorna el modelo activo actual, o None si no hay ninguno."""
        conn = get_connection(self.db_path)
        try:
            row = conn.execute(
                "SELECT * FROM Modelo WHERE Estado = 'Activo' LIMIT 1"
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Registrar nuevo modelo en BD
    # ------------------------------------------------------------------
    def register_model(
        self,
        nombre: str,
        version: str,
        arquitectura: str = "XGBoost",
        algoritmo: str = "Gradient Boosting",
        hiperparametros: Optional[Dict] = None,
        dataset_entrenamiento: str = "",
        f1_score: Optional[float] = None,
        auc_roc: Optional[float] = None,
        estado: str = "Inactivo",
    ) -> Dict:
        """
        Inserta un nuevo modelo en la tabla Modelo.

        Returns:
            Dict con los datos del modelo registrado.
        """
        conn = get_connection(self.db_path)
        try:
            id_modelo = f"mod-{uuid.uuid4().hex[:12]}"
            hiper_str = json.dumps(hiperparametros) if hiperparametros else None

            conn.execute(
                """INSERT INTO Modelo
                   (IdModelo, Nombre, Version, Arquitectura, Algoritmo,
                    Hiperparametros, DatasetEntrenamiento, F1Score,
                    Precision, Recall, AUCROC, Estado, FechaRegistro)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (
                    id_modelo, nombre, version, arquitectura, algoritmo,
                    hiper_str, dataset_entrenamiento, f1_score,
                    None, None, auc_roc, estado,
                ),
            )
            conn.commit()

            return {
                "id_modelo": id_modelo,
                "nombre": nombre,
                "version": version,
                "arquitectura": arquitectura,
                "estado": estado,
                "f1_score": f1_score,
                "auc_roc": auc_roc,
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Activar / desactivar modelo (atómico: solo uno activo a la vez)
    # ------------------------------------------------------------------
    def activate_model(self, id_modelo: str) -> Dict:
        """
        Activa un modelo y desactiva todos los demás.
        Operación atómica dentro de una transacción.
        """
        conn = get_connection(self.db_path)
        try:
            # Desactivar todos
            conn.execute("UPDATE Modelo SET Estado = 'Inactivo' WHERE Estado = 'Activo'")
            # Activar el seleccionado
            conn.execute(
                "UPDATE Modelo SET Estado = 'Activo' WHERE IdModelo = ?",
                (id_modelo,),
            )
            if conn.total_changes == 0:
                raise ValueError(f"Modelo con ID {id_modelo} no encontrado.")
            conn.commit()

            # Retornar el modelo activado
            row = conn.execute(
                "SELECT * FROM Modelo WHERE IdModelo = ?", (id_modelo,)
            ).fetchone()
            return dict(row) if row else {}
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Escanear modelos serializados en disco
    # ------------------------------------------------------------------
    def scan_disk_models(self, models_dir: Optional[Path] = None) -> List[Dict]:
        """
        Escanea el directorio de modelos y retorna los modelos encontrados.

        Cada modelo se identifica por tener un subdirectorio con metadata.json.
        """
        if models_dir is None:
            # Ruta por defecto relativa a este archivo
            models_dir = (
                Path(__file__).resolve().parent.parent.parent.parent / "models"
            )

        modelos = []
        if not models_dir.exists():
            return modelos

        for md in sorted(
            [d for d in models_dir.iterdir() if d.is_dir() and (d / "metadata.json").exists()],
            reverse=True,
        ):
            try:
                meta_path = md / "metadata.json"
                with open(meta_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                model_path = md / "model.joblib"
                size_mb = round(model_path.stat().st_size / (1024 * 1024), 1) if model_path.exists() else 0.0

                modelos.append({
                    "nombre": metadata.get("nombre", md.name),
                    "version": metadata.get("version", md.name),
                    "directorio": str(md),
                    "f1_macro": metadata.get("f1_macro"),
                    "auc_roc": metadata.get("auc_roc"),
                    "n_features": metadata.get("n_features"),
                    "shap_disponible": metadata.get("shap_disponible", True),
                    "tamano_mb": size_mb,
                    "metadata": metadata,
                })
            except (json.JSONDecodeError, OSError):
                # Directorio corrupto o sin metadata válida — omitir
                continue

        return modelos
