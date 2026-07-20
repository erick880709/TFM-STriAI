"""
Pipeline de Limpieza y Normalización — TT-E3-02.
Imputación de nulos, detección de outliers (IQR), codificación de variables.
Referencia: Documento de Arquitectura §10.2-10.3.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rangos fisiológicos para detección de outliers
# ---------------------------------------------------------------------------
RANGOS_FISIOLOGICOS = {
    "temperatura": (30.0, 45.0),
    "frecuencia_cardiaca": (20, 250),
    "frecuencia_respiratoria": (4, 60),
    "saturacion_o2": (50, 100),
    "presion_sistolica": (50, 250),
    "presion_diastolica": (20, 150),
    "peso": (0.5, 300),
    "talla": (30, 250),
    "imc": (10, 65),
    "escala_dolor": (0, 10),
    "glasgow": (3, 15),
    "edad": (0, 120),
}

# Columnas numéricas a normalizar
NUMERIC_COLS = [
    "edad", "temperatura", "frecuencia_cardiaca", "frecuencia_respiratoria",
    "saturacion_o2", "presion_sistolica", "presion_diastolica",
    "peso", "talla", "imc", "escala_dolor", "glasgow", "episodios_previos",
]

# Columnas categóricas a codificar
CATEGORICAL_COLS = [
    "sexo", "via_llegada", "regimen_salud", "nivel_conciencia",
    "motivo_categoria", "tipo_documento",
]

# Columnas binarias (ya son 0/1)
BINARY_COLS = [
    "diabetes", "hipertension", "enfermedad_renal", "embarazo",
    "cancer", "cardiopatias", "enfermedad_pulmonar", "cirugias_recientes",
]


class DataCleaner:
    """
    Limpia y normaliza el dataset unificado para entrenamiento.
    """

    def __init__(self, df: pd.DataFrame, target_col: str = "nivel_triaje"):
        self.df = df.copy()
        self.target_col = target_col
        self.removed_outliers: int = 0
        self.imputed_cols: List[str] = []

    # ------------------------------------------------------------------
    # Paso 1: Filtrar filas sin target
    # ------------------------------------------------------------------
    def filter_no_target(self) -> "DataCleaner":
        """Elimina filas donde el nivel de triaje (target) no está disponible."""
        if self.target_col in self.df.columns:
            antes = len(self.df)
            target_vals = self.df[self.target_col].astype(str).str.strip().str.upper()
            # Mapear variantes comunes de niveles I-V
            validos = ["I", "II", "III", "IV", "V", "1", "2", "3", "4", "5"]
            mask = target_vals.isin(validos)
            self.df = self.df[mask].copy()
            despues = len(self.df)
            logger.info(f"  Filas sin target eliminadas: {antes - despues}")

            # Normalizar niveles: 1→I, 2→II, etc.
            mapping = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            self.df[self.target_col] = target_vals[mask].replace(mapping)
        return self

    # ------------------------------------------------------------------
    # Paso 2: Detectar y remover outliers fisiológicos (IQR)
    # ------------------------------------------------------------------
    def remove_outliers(self, method: str = "iqr") -> "DataCleaner":
        """
        Marca como NaN valores fuera de rangos fisiológicos.
        Opcional: eliminar filas con múltiples outliers extremos.
        """
        for col, (lo, hi) in RANGOS_FISIOLOGICOS.items():
            if col in self.df.columns:
                # Asegurar que la columna es numérica
                if not pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
                mask_out = (self.df[col] < lo) | (self.df[col] > hi)
                n_outliers = mask_out.sum()
                if n_outliers > 0:
                    self.df.loc[mask_out, col] = np.nan
                    self.removed_outliers += n_outliers
                    logger.info(f"  Outliers en {col}: {n_outliers} → marcados NaN (rango [{lo}, {hi}])")

        return self

    # ------------------------------------------------------------------
    # Paso 3: Imputar valores nulos
    # ------------------------------------------------------------------
    def impute_missing(self) -> "DataCleaner":
        """
        Imputa valores nulos: mediana para numéricas, "Desconocido" para categóricas.
        """
        # Numéricas: mediana
        for col in NUMERIC_COLS:
            if col in self.df.columns and self.df[col].isna().any():
                median_val = self.df[col].median()
                if pd.isna(median_val):
                    median_val = 0
                self.df[col] = self.df[col].fillna(median_val)
                self.imputed_cols.append(f"{col} (mediana={median_val:.1f})")

        # Categóricas: "Desconocido"
        for col in CATEGORICAL_COLS:
            if col in self.df.columns and self.df[col].isna().any():
                self.df[col] = self.df[col].fillna("Desconocido")
                self.imputed_cols.append(f"{col} (Desconocido)")

        # Binarias: 0
        for col in BINARY_COLS:
            if col in self.df.columns and self.df[col].isna().any():
                self.df[col] = self.df[col].fillna(0)
                self.imputed_cols.append(f"{col} (0)")

        logger.info(f"  Columnas imputadas: {len(self.imputed_cols)}")
        return self

    # ------------------------------------------------------------------
    # Paso 4: Derivar features
    # ------------------------------------------------------------------
    def derive_features(self) -> "DataCleaner":
        """Crea features derivadas que mejoran el poder predictivo."""
        # IMC si no existe pero hay peso y talla
        if "imc" not in self.df.columns or self.df["imc"].isna().all():
            if "peso" in self.df.columns and "talla" in self.df.columns:
                talla_m = self.df["talla"] / 100.0
                self.df["imc"] = np.where(talla_m > 0, self.df["peso"] / (talla_m ** 2), np.nan)
                self.df["imc"] = self.df["imc"].fillna(self.df["imc"].median())

        # Categorizar edad
        if "edad" in self.df.columns:
            self.df["edad_categoria"] = pd.cut(
                self.df["edad"],
                bins=[0, 12, 18, 65, 120],
                labels=["pediatrico", "adulto_joven", "adulto", "adulto_mayor"],
            ).astype(str)

        # Presión arterial media (PAM)
        if "presion_sistolica" in self.df.columns and "presion_diastolica" in self.df.columns:
            self.df["pam"] = (
                (self.df["presion_sistolica"] + 2 * self.df["presion_diastolica"]) / 3
            )

        # Shock Index (FC / PA sistólica) — predictor de gravedad
        if "frecuencia_cardiaca" in self.df.columns and "presion_sistolica" in self.df.columns:
            self.df["shock_index"] = np.where(
                self.df["presion_sistolica"] > 0,
                self.df["frecuencia_cardiaca"] / self.df["presion_sistolica"],
                np.nan,
            )
            self.df["shock_index"] = self.df["shock_index"].fillna(0)

        # qSOFA simplificado (Glasgow, FR, PA)
        if all(c in self.df.columns for c in ["glasgow", "frecuencia_respiratoria", "presion_sistolica"]):
            self.df["qsofa_score"] = (
                (self.df["glasgow"] < 15).astype(int) +
                (self.df["frecuencia_respiratoria"] >= 22).astype(int) +
                (self.df["presion_sistolica"] <= 100).astype(int)
            )

        logger.info("  Features derivadas: edad_categoria, pam, shock_index, qsofa_score")
        return self

    # ------------------------------------------------------------------
    # Paso 5: Normalizar y codificar
    # ------------------------------------------------------------------
    def normalize_and_encode(
        self,
        scaler: Optional[StandardScaler] = None,
        encoder: Optional[OneHotEncoder] = None,
    ) -> Tuple[np.ndarray, StandardScaler, OneHotEncoder, List[str]]:
        """
        Aplica StandardScaler a numéricas y OneHotEncoder a categóricas.
        Retorna matriz de features, scaler, encoder, y lista de nombres de features.
        """
        # Asegurar columnas numéricas
        numeric_present = [c for c in NUMERIC_COLS if c in self.df.columns]
        categorical_present = [c for c in CATEGORICAL_COLS if c in self.df.columns]
        binary_present = [c for c in BINARY_COLS if c in self.df.columns]
        derived = [c for c in ["pam", "shock_index", "qsofa_score"] if c in self.df.columns]

        # Escalar numéricas
        X_num = self.df[numeric_present + derived].copy()
        X_num = X_num.fillna(0)

        if scaler is None:
            scaler = StandardScaler()
            X_num_scaled = scaler.fit_transform(X_num)
        else:
            X_num_scaled = scaler.transform(X_num)

        # Codificar categóricas
        X_cat = self.df[categorical_present].copy()
        X_cat = X_cat.fillna("Desconocido")

        if encoder is None:
            encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
            X_cat_encoded = encoder.fit_transform(X_cat)
        else:
            X_cat_encoded = encoder.transform(X_cat)

        # Binarias (sin transformación)
        X_bin = self.df[binary_present].fillna(0).values if binary_present else np.array([]).reshape(len(self.df), 0)

        # Feature names
        feature_names = list(numeric_present + derived)
        if categorical_present:
            cat_names = encoder.get_feature_names_out(categorical_present)
            feature_names.extend(cat_names)
        feature_names.extend(binary_present)

        # Concatenar
        if X_bin.size > 0:
            X_final = np.hstack([X_num_scaled, X_cat_encoded, X_bin])
        else:
            X_final = np.hstack([X_num_scaled, X_cat_encoded])

        logger.info(f"  Features generadas: {X_final.shape[1]} columnas")
        return X_final, scaler, encoder, feature_names

    def get_result(self) -> pd.DataFrame:
        """Retorna el DataFrame limpio."""
        return self.df


def clean_and_prepare(
    df: pd.DataFrame,
    target_col: str = "nivel_triaje",
    scaler: Optional[StandardScaler] = None,
    encoder: Optional[OneHotEncoder] = None,
) -> Tuple[pd.DataFrame, np.ndarray, StandardScaler, OneHotEncoder, List[str]]:
    """
    Pipeline completo de limpieza + normalización.
    Retorna (df_limpio, X, scaler, encoder, feature_names).
    """
    cleaner = DataCleaner(df, target_col)
    cleaner.filter_no_target()
    cleaner.remove_outliers()
    cleaner.impute_missing()
    cleaner.derive_features()

    X, scaler, encoder, feature_names = cleaner.normalize_and_encode(scaler, encoder)
    df_clean = cleaner.get_result()

    return df_clean, X, scaler, encoder, feature_names
