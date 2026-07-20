"""
Servicio de Auditoría — TT-E5-01, HU-E5-01, HU-E5-02.
Registro inmutable append-only, consulta con filtros, exportación CSV/Excel/PDF
y generación de reporte de triaje descargable.

Referencia: Documento de Arquitectura §8.3, RNAU-001 a 006.
"""
import sqlite3
import uuid
import json
import csv
import io
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable
import functools
import logging

from app.data.database import get_connection, rows_to_dicts, row_to_dict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Catálogo de acciones auditables (RF-AUD-001)
# ---------------------------------------------------------------------------
ACCIONES_AUDITABLES = {
    "LOGIN": "Inicio de sesión",
    "LOGOUT": "Cierre de sesión",
    "PACIENTE_CREADO": "Registro de paciente",
    "PACIENTE_ACTUALIZADO": "Actualización de datos del paciente",
    "TRIAJE_CREADO": "Creación de evento de triaje",
    "SIGNOS_VITALES_GUARDADOS": "Captura de signos vitales",
    "EVALUACION_CLINICA_GUARDADA": "Evaluación clínica registrada",
    "IA_EJECUTADA": "Ejecución de inferencia IA",
    "CLASIFICACION_VALIDADA": "Validación de clasificación por profesional",
    "RECLASIFICACION": "Reclasificación del paciente",
    "EVENTO_CERRADO": "Cierre de evento de triaje",
    "USUARIO_CREADO": "Creación de usuario",
    "ROL_CAMBIADO": "Cambio de rol de usuario",
    "USUARIO_DESACTIVADO": "Desactivación de usuario",
    "MODELO_REGISTRADO": "Registro de nuevo modelo IA",
    "MODELO_ACTIVADO": "Activación de modelo IA",
    "CONFIGURACION_CAMBIADA": "Cambio de configuración del sistema",
}


class AuditService:
    """
    Servicio de auditoría: registro inmutable, consulta y exportación.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    # ------------------------------------------------------------------
    # TT-E5-01: Registro inmutable
    # ------------------------------------------------------------------
    def register(
        self,
        usuario: str,
        accion: str,
        entidad: Optional[str] = None,
        id_entidad: Optional[str] = None,
        valor_anterior: Optional[Dict] = None,
        valor_nuevo: Optional[Dict] = None,
        observaciones: Optional[str] = None,
    ) -> str:
        """
        Registra una acción en la tabla de auditoría (append-only).
        Retorna el ID del registro creado.
        """
        conn = get_connection(self.db_path)
        try:
            id_audit = f"aud-{uuid.uuid4().hex[:12]}"
            ahora = datetime.utcnow().isoformat()

            conn.execute(
                """INSERT INTO Auditoria
                   (IdAuditoria, Usuario, FechaHora, Accion, EntidadAfectada,
                    IdEntidad, ValorAnterior, ValorNuevo, Observaciones)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    id_audit,
                    usuario,
                    ahora,
                    accion,
                    entidad,
                    id_entidad,
                    json.dumps(valor_anterior, ensure_ascii=False) if valor_anterior else None,
                    json.dumps(valor_nuevo, ensure_ascii=False) if valor_nuevo else None,
                    observaciones,
                ),
            )
            conn.commit()
            logger.debug(f"Auditoría registrada: {accion} por {usuario} ({id_audit})")
            return id_audit
        except Exception as e:
            conn.rollback()
            logger.error(f"Error registrando auditoría: {e}")
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # HU-E5-01: Consulta con filtros
    # ------------------------------------------------------------------
    def query(
        self,
        usuario: Optional[str] = None,
        accion: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        entidad: Optional[str] = None,
        id_entidad: Optional[str] = None,
        id_triaje: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple:
        """
        Consulta registros de auditoría con filtros.
        Retorna (lista_resultados, total_count).
        """
        conn = get_connection(self.db_path)
        try:
            where_clauses = []
            params = []

            if usuario:
                where_clauses.append("a.Usuario = ?")
                params.append(usuario)
            if accion:
                where_clauses.append("a.Accion = ?")
                params.append(accion)
            if fecha_desde:
                where_clauses.append("a.FechaHora >= ?")
                params.append(fecha_desde)
            if fecha_hasta:
                where_clauses.append("a.FechaHora <= ?")
                params.append(fecha_hasta)
            if entidad:
                where_clauses.append("a.EntidadAfectada = ?")
                params.append(entidad)
            if id_entidad:
                where_clauses.append("a.IdEntidad = ?")
                params.append(id_entidad)
            if id_triaje:
                where_clauses.append(
                    "(a.IdEntidad = ? OR a.ValorNuevo LIKE ?)"
                )
                params.append(id_triaje)
                params.append(f"%{id_triaje}%")

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            # Contar total
            count_row = conn.execute(
                f"SELECT COUNT(*) as cnt FROM Auditoria a WHERE {where_sql}",
                params,
            ).fetchone()
            total = count_row["cnt"] if count_row else 0

            # Obtener resultados paginados
            rows = conn.execute(
                f"""SELECT a.* FROM Auditoria a
                    WHERE {where_sql}
                    ORDER BY a.FechaHora DESC
                    LIMIT ? OFFSET ?""",
                params + [limit, offset],
            ).fetchall()

            return rows_to_dicts(rows), total
        finally:
            conn.close()

    def get_acciones_disponibles(self) -> List[str]:
        """Retorna la lista de acciones registradas en auditoría."""
        conn = get_connection(self.db_path)
        try:
            rows = conn.execute(
                "SELECT DISTINCT Accion FROM Auditoria ORDER BY Accion"
            ).fetchall()
            return [r["Accion"] for r in rows]
        finally:
            conn.close()

    def get_usuarios_auditados(self) -> List[str]:
        """Retorna la lista de usuarios con registros de auditoría."""
        conn = get_connection(self.db_path)
        try:
            rows = conn.execute(
                "SELECT DISTINCT Usuario FROM Auditoria ORDER BY Usuario"
            ).fetchall()
            return [r["Usuario"] for r in rows]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # HU-E5-01: Exportación
    # ------------------------------------------------------------------
    def export_csv(self, resultados: List[Dict]) -> str:
        """Exporta resultados de auditoría a CSV (retorna string)."""
        if not resultados:
            return "Sin resultados para exportar."

        output = io.StringIO()
        writer = csv.writer(output)

        # Cabecera
        headers = ["ID", "Usuario", "Fecha/Hora", "Acción", "Entidad",
                   "ID Entidad", "Valor Anterior", "Valor Nuevo", "Observaciones"]
        writer.writerow(headers)

        for r in resultados:
            writer.writerow([
                r.get("id_auditoria", ""),
                r.get("usuario", ""),
                r.get("fecha_hora", ""),
                ACCIONES_AUDITABLES.get(r.get("accion", ""), r.get("accion", "")),
                r.get("entidad_afectada", ""),
                r.get("id_entidad", ""),
                r.get("valor_anterior", "")[:200] if r.get("valor_anterior") else "",
                r.get("valor_nuevo", "")[:200] if r.get("valor_nuevo") else "",
                r.get("observaciones", ""),
            ])

        return output.getvalue()

    def export_excel_dataframe(self, resultados: List[Dict]) -> "pd.DataFrame":
        """Convierte resultados a DataFrame para exportación Excel."""
        import pandas as pd

        rows = []
        for r in resultados:
            rows.append({
                "ID Auditoría": r.get("id_auditoria", ""),
                "Usuario": r.get("usuario", ""),
                "Fecha/Hora": r.get("fecha_hora", ""),
                "Acción": ACCIONES_AUDITABLES.get(r.get("accion", ""), r.get("accion", "")),
                "Entidad": r.get("entidad_afectada", ""),
                "ID Entidad": r.get("id_entidad", ""),
                "Valor Anterior": str(r.get("valor_anterior", ""))[:300],
                "Valor Nuevo": str(r.get("valor_nuevo", ""))[:300],
                "Observaciones": r.get("observaciones", ""),
            })

        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # HU-E5-02: Generación de reporte de triaje descargable
    # ------------------------------------------------------------------
    def generate_triage_report(self, id_triaje: str) -> Dict[str, Any]:
        """
        Genera todos los datos necesarios para el PDF de registro de triaje.
        Retorna un dict estructurado con todos los campos requeridos.
        """
        conn = get_connection(self.db_path)
        try:
            # Obtener datos completos del triaje
            row = conn.execute(
                """SELECT e.*,
                       p.TipoDocumento, p.Edad as EdadPaciente, p.Sexo,
                       p.ViaLlegada, p.EpisodiosPreviosUrgencias,
                       sv.Temperatura, sv.FrecuenciaCardiaca, sv.FrecuenciaRespiratoria,
                       sv.SaturacionO2, sv.PresionSistolica, sv.PresionDiastolica,
                       sv.Peso, sv.Talla, sv.IMC,
                       ec.MotivoTextoLibre, ec.MotivoCategoria, ec.EscalaDolor,
                       ec.Glasgow, ec.NivelConciencia,
                       ec.Diabetes, ec.Hipertension, ec.EnfermedadRenal,
                       ec.Embarazo, ec.Cancer, ec.Cardiopatias,
                       ec.EnfermedadPulmonar, ec.CirugiasRecientes,
                       ec.Alergias, ec.Observaciones
                FROM EventoTriaje e
                JOIN Paciente p ON e.IdPaciente = p.IdPaciente
                LEFT JOIN SignosVitales sv ON e.IdTriaje = sv.IdTriaje
                LEFT JOIN EvaluacionClinica ec ON e.IdTriaje = ec.IdTriaje
                WHERE e.IdTriaje = ?""",
                (id_triaje,),
            ).fetchone()

            if not row:
                raise ValueError(f"Evento de triaje {id_triaje} no encontrado.")

            data = row_to_dict(row)

            # Obtener predicciones IA
            predicciones = conn.execute(
                """SELECT * FROM PrediccionIA
                   WHERE IdTriaje = ?
                   ORDER BY FechaHora DESC""",
                (id_triaje,),
            ).fetchall()
            preds_list = rows_to_dicts(predicciones) if predicciones else []

            # Obtener auditoría del evento
            auditoria = conn.execute(
                """SELECT * FROM Auditoria
                   WHERE IdEntidad = ? OR ValorNuevo LIKE ?
                   ORDER BY FechaHora ASC""",
                (id_triaje, f"%{id_triaje}%"),
            ).fetchall()
            audit_list = rows_to_dicts(auditoria) if auditoria else []

            # Construir antecedentes
            antecedentes = []
            for key, label in [
                ("diabetes", "Diabetes"),
                ("hipertension", "Hipertensión Arterial"),
                ("enfermedad_renal", "Enfermedad Renal Crónica"),
                ("embarazo", "Embarazo"),
                ("cancer", "Cáncer"),
                ("cardiopatias", "Cardiopatías"),
                ("enfermedad_pulmonar", "Enfermedad Pulmonar"),
                ("cirugias_recientes", "Cirugías Recientes"),
            ]:
                if data.get(key):
                    antecedentes.append(label)

            # Nivel de triaje IA
            nivel_ia = data.get("nivel_sugerido_ia")
            nivel_pro = data.get("nivel_asignado_profesional")

            # Probabilidades IA
            try:
                probs_ia = json.loads(data.get("probabilidades_ia", "{}"))
            except (json.JSONDecodeError, TypeError):
                probs_ia = {}

            # Niveles semánticos
            niveles_labels = {
                "I": "I — Atención Inmediata",
                "II": "II — Emergencia (< 30 min)",
                "III": "III — Urgencia (30-60 min)",
                "IV": "IV — Urgencia Menor (1-2 h)",
                "V": "V — Consulta General (> 2 h)",
            }

            return {
                "id_triaje": id_triaje,
                "fecha_ingreso": data.get("fecha_hora_ingreso", ""),
                "fecha_cierre": data.get("fecha_hora_cierre", ""),
                "estado": data.get("estado", ""),
                # Paciente (anonimizado: sin nombre ni documento)
                "edad_paciente": data.get("edad_paciente", ""),
                "sexo": data.get("sexo", ""),
                "via_llegada": data.get("via_llegada", ""),
                "episodios_previos": data.get("episodios_previos_urgencias", 0),
                # Signos vitales
                "temperatura": data.get("temperatura"),
                "frecuencia_cardiaca": data.get("frecuencia_cardiaca"),
                "frecuencia_respiratoria": data.get("frecuencia_respiratoria"),
                "saturacion_o2": data.get("saturacion_o2"),
                "presion_sistolica": data.get("presion_sistolica"),
                "presion_diastolica": data.get("presion_diastolica"),
                "imc": data.get("imc"),
                "peso": data.get("peso"),
                "talla": data.get("talla"),
                # Evaluación clínica
                "motivo_categoria": data.get("motivo_categoria", ""),
                "motivo_texto_libre": data.get("motivo_texto_libre", ""),
                "escala_dolor": data.get("escala_dolor"),
                "glasgow": data.get("glasgow"),
                "nivel_conciencia": data.get("nivel_conciencia", ""),
                "antecedentes": antecedentes,
                "alergias": data.get("alergias", ""),
                "observaciones": data.get("observaciones", ""),
                # Clasificación
                "nivel_ia": nivel_ia,
                "nivel_ia_label": niveles_labels.get(nivel_ia, "") if nivel_ia else "No disponible",
                "nivel_profesional": nivel_pro,
                "nivel_profesional_label": niveles_labels.get(nivel_pro, "") if nivel_pro else "No asignado",
                "concordancia": "Sí" if data.get("concordancia") == 1 else ("No" if data.get("concordancia") == 0 else "N/A"),
                "motivo_discrepancia": data.get("motivo_discrepancia", ""),
                "probabilidades_ia": probs_ia,
                "confianza_ia": max(probs_ia.values()) if probs_ia else None,
                "version_modelo": data.get("version_modelo_usado", "N/A"),
                # Auditoría
                "total_acciones_auditadas": len(audit_list),
                "profesional_responsable": data.get("profesional_responsable", "N/A"),
                # Metadatos
                "fecha_generacion": datetime.utcnow().isoformat(),
                "sistema": "Sistema de Triaje Multimodal IA — TFM UNIR",
            }

        finally:
            conn.close()


# ======================================================================
# DECORADOR @auditar (TT-E5-01)
# ======================================================================

def auditar(
    accion: str,
    entidad: Optional[str] = None,
    extraer_id: Optional[Callable] = None,
):
    """
    Decorador que registra automáticamente una acción en auditoría.

    Uso:
        @auditar("SIGNOS_VITALES_GUARDADOS", entidad="SignosVitales")
        def save_vital_signs(self, id_triaje, ...):
            ...

    Args:
        accion: Clave de la acción en ACCIONES_AUDITABLES.
        entidad: Nombre de la entidad afectada.
        extraer_id: Función que extrae el ID de la entidad de los argumentos.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Intentar obtener db_path y usuario del contexto
            usuario = "Sistema"
            db_path = None

            # Buscar en args (self suele tener db_path)
            for arg in args:
                if hasattr(arg, "db_path"):
                    db_path = arg.db_path
                    break

            # Intentar obtener usuario de Streamlit session_state
            try:
                import streamlit as st
                if hasattr(st, "session_state") and "user" in st.session_state:
                    usuario = st.session_state.user.get("nombre_usuario", "Sistema")
            except Exception:
                pass

            # Extraer ID de entidad
            id_entidad = None
            if extraer_id:
                try:
                    id_entidad = extraer_id(*args, **kwargs)
                except Exception:
                    pass

            # Ejecutar función original
            result = func(*args, **kwargs)

            # Registrar auditoría si hay db_path
            if db_path:
                try:
                    audit_svc = AuditService(db_path)
                    audit_svc.register(
                        usuario=usuario,
                        accion=accion,
                        entidad=entidad,
                        id_entidad=id_entidad,
                    )
                except Exception as e:
                    logger.warning(f"No se pudo registrar auditoría para {accion}: {e}")

            return result

        return wrapper
    return decorator
