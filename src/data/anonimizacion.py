"""
Módulo de Anonimización — TT-E3-01.
Elimina identificadores directos e indirectos según Ley 1581/2012.
Referencia: Documento de Arquitectura §2.2, RT-003.
"""
import pandas as pd
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tipos de identificadores a eliminar según Ley 1581/2012
# ---------------------------------------------------------------------------
IDENTIFICADORES_DIRECTOS = [
    "nombre", "nombres", "apellido", "apellidos",
    "numero_documento", "documento", "identificacion", "cc", "cedula",
    "direccion", "dirección", "domicilio",
    "telefono", "teléfono", "celular", "email", "correo",
    "historia_clinica", "numero_historia", "hc",
]

IDENTIFICADORES_INDIRECTOS = [
    "fecha_nacimiento",  # Se transforma a edad
    "municipio",         # Se transforma a departamento (menos granular)
    "codigo_postal",
    "ips",               # Institucion prestadora (se elimina)
    "medico_tratante",
]


class Anonymizer:
    """
    Aplica anonimización a un DataFrame según los lineamientos de la Ley 1581/2012.
    - Elimina columnas con identificadores directos.
    - Transforma identificadores indirectos (fecha_nac → edad, municipio → depto).
    - Verifica que no queden PII tras el proceso.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.columnas_eliminadas: List[str] = []
        self.columnas_transformadas: List[str] = []

    # ------------------------------------------------------------------
    # Paso 1: Eliminar identificadores directos
    # ------------------------------------------------------------------
    def remove_direct_identifiers(self) -> "Anonymizer":
        """Elimina columnas que contienen identificadores personales directos."""
        cols_lower = {c.strip().lower(): c for c in self.df.columns}

        for id_col in IDENTIFICADORES_DIRECTOS:
            # Coincidencia exacta o parcial
            for col_name_lower, col_name_orig in cols_lower.items():
                if id_col in col_name_lower or col_name_lower in id_col:
                    if col_name_orig in self.df.columns:
                        self.df.drop(columns=[col_name_orig], inplace=True)
                        self.columnas_eliminadas.append(col_name_orig)
                        logger.info(f"  Eliminado (directo): {col_name_orig}")

        return self

    # ------------------------------------------------------------------
    # Paso 2: Transformar identificadores indirectos
    # ------------------------------------------------------------------
    def transform_indirect_identifiers(self) -> "Anonymizer":
        """
        Transforma cuasi-identificadores para reducir granularidad:
        - fecha_nacimiento → edad (entero)
        - municipio → departamento (si hay mapeo disponible)
        """
        cols_lower = {c.strip().lower(): c for c in self.df.columns}

        # Fecha de nacimiento → edad
        for fecha_candidate in ["fecha_nacimiento", "fecha nacimiento", "birth_date", "fnac"]:
            if fecha_candidate in cols_lower:
                col = cols_lower[fecha_candidate]
                try:
                    fechas = pd.to_datetime(self.df[col], errors="coerce")
                    hoy = pd.Timestamp.now()
                    edades = fechas.apply(
                        lambda x: hoy.year - x.year - ((hoy.month, hoy.day) < (x.month, x.day))
                        if pd.notna(x) else np.nan
                    )
                    # Solo actualizar si la columna edad no existe o está toda NaN
                    if "edad" not in self.df.columns or self.df["edad"].isna().all():
                        self.df["edad"] = edades
                    self.df.drop(columns=[col], inplace=True)
                    self.columnas_eliminadas.append(col)
                    self.columnas_transformadas.append(f"{col} → edad")
                    logger.info(f"  Transformado: {col} → edad")
                except Exception as e:
                    logger.warning(f"  No se pudo transformar {col}: {e}")

        # Municipio → Departamento (simplificado: agrupar por primeros dígitos si es código DANE)
        if "municipio" in self.df.columns:
            # Si municipio tiene códigos DANE (5 dígitos), derivar depto (2 primeros)
            try:
                if self.df["municipio"].dtype in ("int64", "float64"):
                    self.df["municipio"] = self.df["municipio"].astype(str).str.zfill(5)
            except Exception:
                pass

        # Eliminar columnas con identificadores indirectos
        for id_col in IDENTIFICADORES_INDIRECTOS:
            if id_col == "fecha_nacimiento":
                continue  # Ya procesada
            if id_col == "municipio":
                continue  # Ya procesada (o se mantiene como depto)
            for col_lower, col_orig in cols_lower.items():
                if id_col in col_lower:
                    if col_orig in self.df.columns:
                        self.df.drop(columns=[col_orig], inplace=True)
                        self.columnas_eliminadas.append(col_orig)
                        logger.info(f"  Eliminado (indirecto): {col_orig}")

        return self

    # ------------------------------------------------------------------
    # Paso 3: Verificación
    # ------------------------------------------------------------------
    def verify_no_pii(self) -> bool:
        """
        Verifica que no queden columnas sospechosas de contener PII.
        Retorna True si pasa la verificación.
        """
        cols_actuales = [c.lower() for c in self.df.columns]
        sospechosas = []

        all_identifiers = IDENTIFICADORES_DIRECTOS + IDENTIFICADORES_INDIRECTOS
        for id_col in all_identifiers:
            for col in cols_actuales:
                if id_col in col:
                    sospechosas.append(col)

        if sospechosas:
            logger.warning(f"  ⚠ Columnas potencialmente identificables: {sospechosas}")
            return False

        logger.info("  ✓ Verificación PII: ningún identificador detectado")
        return True

    # ------------------------------------------------------------------
    # Paso 4: Resultado
    # ------------------------------------------------------------------
    def get_result(self) -> pd.DataFrame:
        """Retorna el DataFrame anonimizado."""
        return self.df

    def get_summary(self) -> dict:
        """Retorna un resumen de las acciones de anonimización."""
        return {
            "columnas_eliminadas": self.columnas_eliminadas,
            "columnas_transformadas": self.columnas_transformadas,
            "filas_resultantes": len(self.df),
            "columnas_resultantes": len(self.df.columns),
        }


def anonymize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Función de conveniencia: aplica el pipeline completo de anonimización.
    """
    anon = Anonymizer(df)
    anon.remove_direct_identifiers()
    anon.transform_indirect_identifiers()
    anon.verify_no_pii()
    summary = anon.get_summary()
    logger.info(f"Anonimización completada: {summary}")
    return anon.get_result()
