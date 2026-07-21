"""
Servicio de Dashboard Operativo.
Extrae las consultas SQL desde dashboard_page.py para exponer KPIs vía API REST.
"""
from typing import Dict, List, Optional
from datetime import datetime

from app.data.database import get_connection, rows_to_dicts


class DashboardService:
    """Provee métricas operacionales del sistema de triaje."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    # ------------------------------------------------------------------
    # KPIs consolidados (una sola llamada para minimizar round-trips)
    # ------------------------------------------------------------------
    def get_kpis(self) -> Dict:
        """
        Retorna todos los KPIs del dashboard en un solo diccionario.

        Returns:
            {
                "total_triages": int,
                "total_pacientes": int,
                "triajes_hoy": int,
                "tasa_concordancia": float,
                "concordancia_si": int,
                "concordancia_total": int,
                "tiempo_inferencia_promedio": float,
                "tasa_cierre": float,
                "cerrados": int,
                "triajes_por_estado": {estado: count},
                "triajes_por_nivel_ia": {nivel: count},
                "total_con_ia": int,
            }
        """
        conn = get_connection(self.db_path)
        try:
            # Total de triajes
            total_triages = conn.execute(
                "SELECT COUNT(*) as cnt FROM EventoTriaje"
            ).fetchone()["cnt"]

            # Triajes por estado
            estados_rows = conn.execute(
                "SELECT Estado, COUNT(*) as cnt FROM EventoTriaje GROUP BY Estado"
            ).fetchall()
            estados = {r["Estado"]: r["cnt"] for r in estados_rows}

            # Distribución por nivel IA
            niveles_rows = conn.execute(
                "SELECT NivelSugeridoIA, COUNT(*) as cnt FROM EventoTriaje "
                "WHERE NivelSugeridoIA IS NOT NULL GROUP BY NivelSugeridoIA"
            ).fetchall()
            niveles_ia = {r["NivelSugeridoIA"]: r["cnt"] for r in niveles_rows}
            total_con_ia = sum(niveles_ia.values())

            # Concordancia
            concordancia_total = conn.execute(
                "SELECT COUNT(*) as cnt FROM EventoTriaje WHERE Concordancia IS NOT NULL"
            ).fetchone()["cnt"]
            concordancia_si = conn.execute(
                "SELECT COUNT(*) as cnt FROM EventoTriaje WHERE Concordancia = 1"
            ).fetchone()["cnt"]
            tasa_concordancia = (
                (concordancia_si / concordancia_total * 100)
                if concordancia_total > 0
                else 0.0
            )

            # Total pacientes
            total_pacientes = conn.execute(
                "SELECT COUNT(*) as cnt FROM Paciente"
            ).fetchone()["cnt"]

            # Tiempo promedio de inferencia
            avg_time = conn.execute(
                "SELECT AVG(TiempoInferencia) as avg_t FROM PrediccionIA"
            ).fetchone()["avg_t"] or 0.0

            # Triajes hoy
            hoy = datetime.now().strftime("%Y-%m-%d")
            triajes_hoy = conn.execute(
                "SELECT COUNT(*) as cnt FROM EventoTriaje WHERE FechaHoraIngreso LIKE ?",
                (f"{hoy}%",),
            ).fetchone()["cnt"]

            # Tasa de cierre
            cerrados = estados.get("Cerrado", 0)
            tasa_cierre = (
                (cerrados / max(total_triages, 1) * 100)
            )

            return {
                "total_triages": total_triages,
                "total_pacientes": total_pacientes,
                "triajes_hoy": triajes_hoy,
                "tasa_concordancia": round(tasa_concordancia, 1),
                "concordancia_si": concordancia_si,
                "concordancia_total": concordancia_total,
                "tiempo_inferencia_promedio": round(float(avg_time), 2),
                "tasa_cierre": round(tasa_cierre, 1),
                "cerrados": cerrados,
                "triajes_por_estado": estados,
                "triajes_por_nivel_ia": niveles_ia,
                "total_con_ia": total_con_ia,
            }
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Tendencia de triajes (últimos 7 días)
    # ------------------------------------------------------------------
    def get_triages_7d(self) -> List[Dict]:
        """
        Retorna el conteo de triajes por día en los últimos 7 días.

        Returns:
            [{"dia": "2026-07-15", "cnt": 42}, ...]
        """
        conn = get_connection(self.db_path)
        try:
            rows = conn.execute(
                "SELECT DATE(FechaHoraIngreso) as dia, COUNT(*) as cnt "
                "FROM EventoTriaje "
                "WHERE FechaHoraIngreso >= DATE('now', '-7 days') "
                "GROUP BY dia ORDER BY dia"
            ).fetchall()
            return rows_to_dicts(rows) if rows else []
        finally:
            conn.close()
