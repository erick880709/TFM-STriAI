"""
Pipeline de Ingesta de Datos — TT-E3-01.
Lee 5 fuentes de datos (MIMIC-IV-ED, San Juan de Dios, datos.gov.co, BDUA, Supersalud),
unifica esquemas y produce un DataFrame normalizado.

Referencias:
  - RT-003 (fuentes de datos)
  - Documento de Arquitectura §10.1-10.2
  - Ley 1581/2012 (anonimización obligatoria)
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración de fuentes
# ---------------------------------------------------------------------------
FUENTES_ESPERADAS = {
    "Clasificación_en_Triage_Urgencias_20260713.csv": "datos_gov",
    "dataset_urgencias_san_juan_de_dios_custom.csv": "san_juan_de_dios",
    "MORBILIDAD_EN_EL_SERVICIO_DE_URGENCIAS_20260713.csv": "morbilidad_urgencias",
    "Morbilidad_Urgencias_2019_Municipio_Pitalito_Huila_ESE_Hospital_Departamental_San_Antonio_de_Pitalito_20260713.csv": "pitalito",
}

# Columnas estándar del esquema unificado
ESQUEMA_UNIFICADO = [
    "fuente",               # Origen del registro
    "tipo_documento",       # CC, TI, CE, PA, RC
    "edad",                 # Edad en años (calculada si viene fecha_nac)
    "sexo",                 # M, F
    "regimen_salud",        # Contributivo, Subsidiado, Especial, No afiliado
    "eps",                  # Nombre de la EPS (si disponible)
    "municipio",            # Municipio de residencia
    "departamento",         # Departamento (derivado de municipio)
    "via_llegada",          # Ambulancia, Particular, Remision
    "temperatura",          # °C
    "frecuencia_cardiaca",  # lpm
    "frecuencia_respiratoria",  # rpm
    "saturacion_o2",        # %
    "presion_sistolica",    # mmHg
    "presion_diastolica",   # mmHg
    "peso",                 # kg
    "talla",                # cm
    "imc",                  # kg/m² (calculado si no viene)
    "motivo_consulta_texto",  # Texto libre
    "motivo_categoria",     # Catálogo: Dolor toracico, Trauma, Disnea...
    "escala_dolor",         # 0-10
    "glasgow",              # 3-15
    "nivel_conciencia",     # Alerta, Somnoliento, Obnubilado, Inconsciente
    "diabetes",             # 0/1
    "hipertension",         # 0/1
    "enfermedad_renal",     # 0/1
    "embarazo",             # 0/1
    "cancer",               # 0/1
    "cardiopatias",         # 0/1
    "enfermedad_pulmonar",  # 0/1
    "cirugias_recientes",   # 0/1
    "alergias",             # Texto libre
    "nivel_triaje",         # I, II, III, IV, V (target)
    "fecha_ingreso",        # Fecha de ingreso a urgencias
    "episodios_previos",    # Número de visitas previas
]

# ---------------------------------------------------------------------------
# Clase principal de ingesta
# ---------------------------------------------------------------------------

class DataIngester:
    """
    Ingesta y unificación de las 5 fuentes de datos del proyecto.
    Produce un DataFrame unificado con el esquema estándar.
    """

    def __init__(self, datasets_dir: str):
        self.datasets_dir = Path(datasets_dir)
        self.loaded: Dict[str, pd.DataFrame] = {}
        self.log: List[str] = []

    # ------------------------------------------------------------------
    # Paso 1: Carga de fuentes
    # ------------------------------------------------------------------
    def load_all_sources(self) -> Dict[str, pd.DataFrame]:
        """Carga todas las fuentes disponibles en el directorio de datasets."""
        if not self.datasets_dir.exists():
            raise FileNotFoundError(f"Directorio de datasets no encontrado: {self.datasets_dir}")

        for filename in self.datasets_dir.glob("*.csv"):
            fname = filename.name
            self.log.append(f"Cargando: {fname}")

            try:
                df = pd.read_csv(filename, encoding="utf-8", low_memory=False)
                self.loaded[fname] = df
                self.log.append(f"  → {len(df):,} filas, {len(df.columns)} columnas")
            except UnicodeDecodeError:
                df = pd.read_csv(filename, encoding="latin-1", low_memory=False)
                self.loaded[fname] = df
                self.log.append(f"  → {len(df):,} filas, {len(df.columns)} columnas (latin-1)")
            except Exception as e:
                self.log.append(f"  → ERROR: {e}")

        return self.loaded

    # ------------------------------------------------------------------
    # Paso 2: Unificación de esquemas
    # ------------------------------------------------------------------
    def unify_schemas(self) -> pd.DataFrame:
        """
        Detecta automáticamente el esquema de cada fuente y lo mapea
        al esquema unificado. Combina todos los DataFrames.
        """
        if not self.loaded:
            self.load_all_sources()

        unified_dfs = []

        for filename, df in self.loaded.items():
            fuente_tag = FUENTES_ESPERADAS.get(filename, filename[:30])

            try:
                mapped = self._map_to_unified(df, fuente_tag)
                if mapped is not None and len(mapped) > 0:
                    mapped["fuente"] = fuente_tag
                    unified_dfs.append(mapped)
                    self.log.append(f"Mapeado {filename} → {len(mapped):,} filas válidas")
            except Exception as e:
                self.log.append(f"Error mapeando {filename}: {e}")

        if not unified_dfs:
            raise ValueError("No se pudo unificar ninguna fuente. Revise los datasets.")

        result = pd.concat(unified_dfs, ignore_index=True)
        self.log.append(f"Dataset unificado: {len(result):,} filas × {len(result.columns)} columnas")
        return result

    # ------------------------------------------------------------------
    # Mapeo inteligente de columnas por fuente
    # ------------------------------------------------------------------
    @staticmethod
    def _clean_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Post-procesa columnas que deberían ser numéricas pero contienen
        texto (ej. '24 AÑOS' → 24). Extrae el primer número encontrado.
        """
        import re
        import pandas.api.types as pd_types
        numeric_cols = ["edad", "temperatura", "frecuencia_cardiaca",
                        "frecuencia_respiratoria", "saturacion_o2",
                        "presion_sistolica", "presion_diastolica",
                        "peso", "talla", "imc", "escala_dolor", "glasgow"]
        for col in numeric_cols:
            if col in df.columns:
                # Si la columna es string/object, intentar extraer números
                if pd_types.is_string_dtype(df[col]) or df[col].dtype == object:
                    try:
                        # Extraer primer número (entero o decimal) de cada valor
                        df[col] = df[col].astype(str).apply(
                            lambda x: float(re.findall(r'\d+\.?\d*', str(x))[0])
                            if re.findall(r'\d+\.?\d*', str(x)) else np.nan
                        )
                    except Exception:
                        pass
        return df

    def _map_to_unified(self, df: pd.DataFrame, fuente: str) -> Optional[pd.DataFrame]:
        """
        Detecta columnas en el CSV fuente y las mapea al esquema unificado.
        Usa heurísticas de nombre de columna (case-insensitive, sin tildes).
        """
        cols_lower = {c.strip().lower(): c for c in df.columns}
        result = pd.DataFrame()

        # --- Mapeo de columnas clave ---
        mapeos = {
            "edad": ["edad", "age", "edad_paciente", "edad paciente", "edadpaciente"],
            "sexo": ["sexo", "genero", "género", "gender", "sex", "sexo biologico", "sexo_biologico"],
            "temperatura": ["temperatura", "temp", "temperature", "temperatura_c", "temperatura corporal"],
            "frecuencia_cardiaca": ["frecuencia_cardiaca", "frecuencia cardiaca", "fc", "heart_rate", "pulso", "frecuenciacardiaca"],
            "frecuencia_respiratoria": ["frecuencia_respiratoria", "frecuencia respiratoria", "fr", "respiratory_rate", "frecuenciarespiratoria"],
            "saturacion_o2": ["saturacion_o2", "saturacion o2", "spo2", "sat_o2", "oxigeno", "saturaciono2", "saturacion_de_oxigeno", "oxigeno_saturacion"],
            "presion_sistolica": ["presion_sistolica", "presion sistolica", "pa_sistolica", "systolic", "tas", "presionsistolica", "tension_arterial_sistolica"],
            "presion_diastolica": ["presion_diastolica", "presion diastolica", "pa_diastolica", "diastolic", "tad", "presiondiastolica", "tension_arterial_diastolica"],
            "nivel_triaje": ["nivel_triaje", "nivel triaje", "triaje", "triage", "nivel_de_triaje", "nivel_triage", "clasificacion", "clasificación", "clasificacion_triaje"],
            "motivo_consulta_texto": ["motivo_consulta", "motivo consulta", "diagnostico", "diagnóstico", "dx", "motivo", "consulta", "motivo_de_consulta", "motivoconsulta", "descripcion", "descripción", "detalle"],
            "municipio": ["municipio", "municipio_residencia", "ciudad", "municipio de residencia"],
            "departamento": ["departamento", "departamento_residencia", "dpto"],
            "eps": ["eps", "entidad", "aseguradora", "nombre_eps", "eps o ips", "nom_admini", "ips", "eapb"],
            "regimen_salud": ["regimen", "régimen", "regimen_salud", "regimen de salud", "tipo_regimen", "regimen"],
            "fecha_ingreso": ["fecha_ing", "fecha_ingreso", "fecha", "fecha_atencion", "fecha de ingreso"],
        }

        for target_col, candidates in mapeos.items():
            for cand in candidates:
                if cand in cols_lower:
                    original_col = cols_lower[cand]
                    # Intentar conversión numérica; si falla o todo es NaN, mantener como string
                    try:
                        numeric_vals = pd.to_numeric(df[original_col], errors="coerce")
                        # Si al menos el 10% de los valores son numéricos no-nulos, usar numérico
                        if numeric_vals.notna().sum() > len(numeric_vals) * 0.1:
                            result[target_col] = numeric_vals
                        else:
                            result[target_col] = df[original_col].astype(str)
                    except (ValueError, TypeError):
                        result[target_col] = df[original_col].astype(str)
                    break

        # --- Derivar columnas faltantes ---
        if "edad" not in result.columns or result["edad"].isna().all():
            # Intentar derivar de fecha de nacimiento
            for date_candidate in ["fecha_nacimiento", "fecha nacimiento", "birth_date", "fnac", "fecha de nacimiento"]:
                if date_candidate in cols_lower:
                    try:
                        fechas = pd.to_datetime(df[cols_lower[date_candidate]], errors="coerce")
                        hoy = pd.Timestamp.now()
                        result["edad"] = fechas.apply(
                            lambda x: hoy.year - x.year - ((hoy.month, hoy.day) < (x.month, x.day))
                            if pd.notna(x) else np.nan
                        )
                        break
                    except Exception:
                        pass

        # IMC: peso/talla²
        peso_col = next((cols_lower[c] for c in ["peso", "weight", "peso_kg"] if c in cols_lower), None)
        talla_col = next((cols_lower[c] for c in ["talla", "height", "talla_cm", "estatura"] if c in cols_lower), None)
        if peso_col and talla_col:
            try:
                peso = pd.to_numeric(df[peso_col], errors="coerce")
                talla_cm = pd.to_numeric(df[talla_col], errors="coerce")
                talla_m = talla_cm / 100.0
                result["imc"] = np.where(talla_m > 0, peso / (talla_m ** 2), np.nan)
                result["peso"] = peso
                result["talla"] = talla_cm
            except Exception:
                pass

        # Nivel de conciencia
        for conc_candidate in ["nivel_conciencia", "conciencia", "consciousness", "estado_conciencia", "nivel de conciencia"]:
            if conc_candidate in cols_lower:
                result["nivel_conciencia"] = df[cols_lower[conc_candidate]].astype(str)
                break

        # Escala de dolor
        for dolor_candidate in ["escala_dolor", "dolor", "pain", "escala de dolor", "dolor_0_10"]:
            if dolor_candidate in cols_lower:
                result["escala_dolor"] = pd.to_numeric(df[cols_lower[dolor_candidate]], errors="coerce")
                break

        # --- Post-procesamiento: limpiar columnas numéricas con texto ---
        result = self._clean_numeric_columns(result)

        # Verificar si tenemos al menos algunas columnas mapeadas
        mapped_cols = [c for c in result.columns if c != "fuente" and result[c].notna().any()]
        # Si hay nivel_triaje, es suficiente (dataset de clasificación)
        has_triaje = "nivel_triaje" in result.columns and result["nivel_triaje"].notna().any()
        if len(mapped_cols) < 2 and not has_triaje:
            self.log.append(f"  ⚠ Pocas columnas mapeadas para {fuente}: {mapped_cols}")
            return None

        return result


# ---------------------------------------------------------------------------
# Funciones de conveniencia
# ---------------------------------------------------------------------------

def load_unified_dataset(datasets_dir: str) -> pd.DataFrame:
    """Función principal: carga y unifica todas las fuentes."""
    ingester = DataIngester(datasets_dir)
    ingester.load_all_sources()
    df = ingester.unify_schemas()
    for entry in ingester.log:
        logger.info(entry)
    return df
