"""
Servicio de Triaje — Máquina de estados, signos vitales y evaluación clínica.
Cubre: HU-E2-04 (Signos vitales), HU-E2-05 (Evaluación clínica),
       HU-E2-06 (Flujo de estados), HU-E2-07 (Reclasificación),
       HU-E2-08 (Cierre de evento).
"""
import sqlite3
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple

from app.data.database import get_connection, row_to_dict


# ---------------------------------------------------------------------------
# Máquina de estados del triaje (HU-E2-06)
# ---------------------------------------------------------------------------
ESTADOS_TRIAGE = [
    "Registrado",
    "EnEvaluacion",
    "PendienteIA",
    "Clasificado",
    "Validado",
    "Cerrado",
    "Cancelado",
]

# Transiciones válidas: origen → [destinos permitidos]
TRANSICIONES_VALIDAS: Dict[str, List[str]] = {
    "Registrado":    ["EnEvaluacion", "Cancelado"],
    "EnEvaluacion":  ["PendienteIA", "Registrado", "Cancelado"],
    "PendienteIA":   ["Clasificado", "EnEvaluacion", "Cancelado"],
    "Clasificado":   ["Validado", "PendienteIA", "Cancelado"],
    "Validado":      ["Cerrado", "Clasificado", "Cancelado"],
    "Cerrado":       [],               # Estado terminal
    "Cancelado":     ["Registrado"],   # Permite reactivar
}

# Catálogos clínicos
NIVELES_CONCIENCIA = ["Alerta", "Somnoliento", "Obnubilado", "Inconsciente"]
MOTIVOS_CATEGORIA = [
    "Dolor toracico", "Trauma", "Disnea", "Dolor abdominal", "Fiebre",
    "Cefalea", "Convulsiones", "Hemorragia", "Intoxicacion", "Otro",
]
MOTIVOS_CATEGORIA_LABELS = {
    "Dolor toracico": "Dolor torácico",
    "Trauma": "Trauma",
    "Disnea": "Disnea",
    "Dolor abdominal": "Dolor abdominal",
    "Fiebre": "Fiebre",
    "Cefalea": "Cefalea",
    "Convulsiones": "Convulsiones",
    "Hemorragia": "Hemorragia",
    "Intoxicacion": "Intoxicación",
    "Otro": "Otro",
}
NIVELES_TRIAGE = ["I", "II", "III", "IV", "V"]
NIVELES_LABELS = {
    "I": "I — Atención Inmediata",
    "II": "II — Emergencia (< 30 min)",
    "III": "III — Urgencia (30-60 min)",
    "IV": "IV — Urgencia Menor (1-2 h)",
    "V": "V — Consulta General (> 2 h)",
}

# Rangos fisiológicos para validación de signos vitales
RANGOS_VITALES = {
    "temperatura":        (30.0, 45.0),
    "frecuencia_cardiaca": (1, 300),
    "frecuencia_respiratoria": (1, 60),
    "saturacion_o2":      (0, 100),
    "presion_sistolica":  (1, 300),
    "presion_diastolica": (1, 200),
    "peso":               (0.5, 500.0),
    "talla":              (20.0, 250.0),
}

# Umbrales de alerta
ALERTAS_VITALES = {
    "saturacion_o2":      (None, 90),     # < 90 → crítico
    "frecuencia_respiratoria": (25, None), # > 25 → elevada
    "presion_sistolica":  (None, 90),     # < 90 → hipotensión (peligro alto: > 180)
    "temperatura":        (None, 35),     # < 35 → hipotermia (peligro alto: > 41)
    "frecuencia_cardiaca": (120, None),   # > 120 → taquicardia
}


class TriageService:
    """Gestiona el ciclo de vida completo del evento de triaje."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    # ==================================================================
    # EVENTO DE TRIAJE — Creación y consulta
    # ==================================================================

    def create_triage_event(
        self,
        id_paciente: str,
        profesional_responsable: Optional[str] = None,
    ) -> Dict:
        """
        Crea un nuevo evento de triaje en estado 'Registrado'.
        HU-E2-01 — flujo post-registro.
        """
        conn = get_connection(self.db_path)
        try:
            # Verificar que el paciente existe
            paciente = conn.execute(
                "SELECT IdPaciente FROM Paciente WHERE IdPaciente = ?",
                (id_paciente,),
            ).fetchone()
            if not paciente:
                raise ValueError(f"Paciente {id_paciente} no encontrado.")

            id_triaje = f"tri-{uuid.uuid4().hex[:12]}"
            ahora = datetime.utcnow().isoformat()

            conn.execute(
                """INSERT INTO EventoTriaje
                   (IdTriaje, IdPaciente, FechaHoraIngreso, Estado,
                    ProfesionalResponsable, FechaModificacion)
                   VALUES (?, ?, ?, 'Registrado', ?, ?)""",
                (id_triaje, id_paciente, ahora, profesional_responsable, ahora),
            )
            conn.commit()

            # Actualizar contador de episodios previos
            total = conn.execute(
                "SELECT COUNT(*) as cnt FROM EventoTriaje WHERE IdPaciente = ?",
                (id_paciente,),
            ).fetchone()["cnt"]
            conn.execute(
                "UPDATE Paciente SET EpisodiosPreviosUrgencias = ? WHERE IdPaciente = ?",
                (total, id_paciente),
            )
            conn.commit()

            return {
                "id_triaje": id_triaje,
                "id_paciente": id_paciente,
                "fecha_hora_ingreso": ahora,
                "estado": "Registrado",
                "profesional_responsable": profesional_responsable,
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_triage_event(self, id_triaje: str) -> Optional[Dict]:
        """Obtiene un evento de triaje con sus datos clínicos completos."""
        conn = get_connection(self.db_path)
        try:
            row = conn.execute(
                """SELECT e.*,
                       p.NumeroDocumento, p.TipoDocumento, p.Edad as EdadPaciente,
                       p.Sexo, p.ViaLlegada, p.EpisodiosPreviosUrgencias,
                       p.Nombres, p.Apellidos,
                       sv.Temperatura, sv.FrecuenciaCardiaca, sv.FrecuenciaRespiratoria,
                       sv.SaturacionO2, sv.PresionSistolica, sv.PresionDiastolica,
                       sv.Peso, sv.Talla, sv.IMC,
                       ec.MotivoTextoLibre, ec.MotivoCategoria, ec.EscalaDolor,
                       ec.Glasgow, ec.NivelConciencia, ec.Diabetes, ec.Hipertension,
                       ec.EnfermedadRenal, ec.Embarazo, ec.Cancer, ec.Cardiopatias,
                       ec.EnfermedadPulmonar, ec.CirugiasRecientes,
                       ec.MedicacionRelevante, ec.Alergias, ec.Observaciones,
                       ec.EpisodiosPreviosUrgencias as EpPreviosEval
                FROM EventoTriaje e
                JOIN Paciente p ON e.IdPaciente = p.IdPaciente
                LEFT JOIN SignosVitales sv ON e.IdTriaje = sv.IdTriaje
                LEFT JOIN EvaluacionClinica ec ON e.IdTriaje = ec.IdTriaje
                WHERE e.IdTriaje = ?""",
                (id_triaje,),
            ).fetchone()
            return row_to_dict(row) if row else None
        finally:
            conn.close()

    def get_active_triage_for_patient(self, id_paciente: str) -> Optional[Dict]:
        """Obtiene el evento de triaje activo (no cerrado ni cancelado) de un paciente."""
        conn = get_connection(self.db_path)
        try:
            row = conn.execute(
                """SELECT * FROM EventoTriaje
                   WHERE IdPaciente = ? AND Estado NOT IN ('Cerrado', 'Cancelado')
                   ORDER BY FechaHoraIngreso DESC LIMIT 1""",
                (id_paciente,),
            ).fetchone()
            return row_to_dict(row) if row else None
        finally:
            conn.close()

    # ==================================================================
    # MÁQUINA DE ESTADOS (HU-E2-06)
    # ==================================================================

    def transition_state(
        self,
        id_triaje: str,
        nuevo_estado: str,
        usuario: str,
        motivo: Optional[str] = None,
    ) -> Dict:
        """
        Ejecuta una transición de estado válida en la máquina de estados.
        Lanza ValueError si la transición no es válida.
        Registra el cambio en auditoría.
        """
        if nuevo_estado not in ESTADOS_TRIAGE:
            raise ValueError(f"Estado no reconocido: {nuevo_estado}")

        conn = get_connection(self.db_path)
        try:
            evento = conn.execute(
                "SELECT * FROM EventoTriaje WHERE IdTriaje = ?",
                (id_triaje,),
            ).fetchone()

            if not evento:
                raise ValueError(f"Evento de triaje {id_triaje} no encontrado.")

            estado_actual = evento["Estado"]
            destinos = TRANSICIONES_VALIDAS.get(estado_actual, [])

            if nuevo_estado not in destinos:
                raise ValueError(
                    f"Transición no válida: '{estado_actual}' → '{nuevo_estado}'. "
                    f"Transiciones permitidas: {destinos}"
                )

            ahora = datetime.utcnow().isoformat()

            # Actualizar estado
            conn.execute(
                """UPDATE EventoTriaje
                   SET Estado = ?, FechaModificacion = ?
                   WHERE IdTriaje = ?""",
                (nuevo_estado, ahora, id_triaje),
            )

            # Si es cierre, registrar timestamp
            if nuevo_estado == "Cerrado":
                conn.execute(
                    "UPDATE EventoTriaje SET FechaHoraCierre = ? WHERE IdTriaje = ?",
                    (ahora, id_triaje),
                )

            # Registrar en auditoría
            self._auditar_cambio_estado(
                conn, id_triaje, estado_actual, nuevo_estado,
                usuario, motivo or "",
            )

            conn.commit()

            return {
                "id_triaje": id_triaje,
                "estado_anterior": estado_actual,
                "estado_nuevo": nuevo_estado,
                "fecha_modificacion": ahora,
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # ==================================================================
    # SIGNOS VITALES (HU-E2-04)
    # ==================================================================

    def save_vital_signs(
        self,
        id_triaje: str,
        temperatura: Optional[float] = None,
        frecuencia_cardiaca: Optional[int] = None,
        frecuencia_respiratoria: Optional[int] = None,
        saturacion_o2: Optional[int] = None,
        presion_sistolica: Optional[int] = None,
        presion_diastolica: Optional[int] = None,
        peso: Optional[float] = None,
        talla: Optional[float] = None,
    ) -> Tuple[Dict, List[Dict]]:
        """
        Guarda o actualiza los signos vitales de un evento de triaje.
        Retorna (dict_signos, lista_alertas).
        """
        alertas = []

        # Validar rangos fisiológicos
        self._validar_signo("temperatura", temperatura, alertas)
        self._validar_signo("frecuencia_cardiaca", frecuencia_cardiaca, alertas)
        self._validar_signo("frecuencia_respiratoria", frecuencia_respiratoria, alertas)
        self._validar_signo("saturacion_o2", saturacion_o2, alertas)
        self._validar_signo("presion_sistolica", presion_sistolica, alertas)
        self._validar_signo("presion_diastolica", presion_diastolica, alertas)

        # Validar PA: sistólica > diastólica
        if presion_sistolica and presion_diastolica:
            if presion_sistolica <= presion_diastolica:
                alertas.append({
                    "campo": "presion_arterial",
                    "tipo": "error",
                    "mensaje": "Presión sistólica debe ser mayor que diastólica.",
                })

        # Calcular IMC
        imc = None
        if peso and talla and talla > 0:
            talla_m = talla / 100.0
            imc = round(peso / (talla_m ** 2), 1)

        conn = get_connection(self.db_path)
        try:
            ahora = datetime.utcnow().isoformat()

            # Verificar si ya existen signos vitales
            existente = conn.execute(
                "SELECT IdSignosVitales FROM SignosVitales WHERE IdTriaje = ?",
                (id_triaje,),
            ).fetchone()

            if existente:
                conn.execute(
                    """UPDATE SignosVitales SET
                       Temperatura=?, FrecuenciaCardiaca=?, FrecuenciaRespiratoria=?,
                       SaturacionO2=?, PresionSistolica=?, PresionDiastolica=?,
                       Peso=?, Talla=?, IMC=?, FechaRegistro=?
                       WHERE IdTriaje=?""",
                    (temperatura, frecuencia_cardiaca, frecuencia_respiratoria,
                     saturacion_o2, presion_sistolica, presion_diastolica,
                     peso, talla, imc, ahora, id_triaje),
                )
            else:
                id_signos = f"sv-{uuid.uuid4().hex[:12]}"
                conn.execute(
                    """INSERT INTO SignosVitales
                       (IdSignosVitales, IdTriaje, Temperatura, FrecuenciaCardiaca,
                        FrecuenciaRespiratoria, SaturacionO2, PresionSistolica,
                        PresionDiastolica, Peso, Talla, IMC, FechaRegistro)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (id_signos, id_triaje, temperatura, frecuencia_cardiaca,
                     frecuencia_respiratoria, saturacion_o2, presion_sistolica,
                     presion_diastolica, peso, talla, imc, ahora),
                )

            conn.commit()

            signos = {
                "temperatura": temperatura,
                "frecuencia_cardiaca": frecuencia_cardiaca,
                "frecuencia_respiratoria": frecuencia_respiratoria,
                "saturacion_o2": saturacion_o2,
                "presion_sistolica": presion_sistolica,
                "presion_diastolica": presion_diastolica,
                "peso": peso,
                "talla": talla,
                "imc": imc,
            }
            return signos, alertas
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_vital_signs(self, id_triaje: str) -> Optional[Dict]:
        """Obtiene los signos vitales de un evento."""
        conn = get_connection(self.db_path)
        try:
            row = conn.execute(
                "SELECT * FROM SignosVitales WHERE IdTriaje = ?",
                (id_triaje,),
            ).fetchone()
            return row_to_dict(row) if row else None
        finally:
            conn.close()

    # ==================================================================
    # EVALUACIÓN CLÍNICA (HU-E2-05)
    # ==================================================================

    def save_clinical_evaluation(
        self,
        id_triaje: str,
        motivo_categoria: str,
        motivo_texto_libre: Optional[str] = None,
        escala_dolor: Optional[int] = None,
        glasgow: Optional[int] = None,
        nivel_conciencia: Optional[str] = None,
        diabetes: bool = False,
        hipertension: bool = False,
        enfermedad_renal: bool = False,
        embarazo: bool = False,
        cancer: bool = False,
        cardiopatias: bool = False,
        enfermedad_pulmonar: bool = False,
        cirugias_recientes: bool = False,
        medicacion_relevante: Optional[str] = None,
        alergias: Optional[str] = None,
        observaciones: Optional[str] = None,
        episodios_previos: Optional[int] = None,
    ) -> Dict:
        """Guarda o actualiza la evaluación clínica de un evento de triaje."""
        # Validar catálogos
        if motivo_categoria not in MOTIVOS_CATEGORIA:
            raise ValueError(f"Categoría de motivo inválida: {motivo_categoria}")
        if nivel_conciencia and nivel_conciencia not in NIVELES_CONCIENCIA:
            raise ValueError(f"Nivel de conciencia inválido: {nivel_conciencia}")
        if escala_dolor is not None and not (0 <= escala_dolor <= 10):
            raise ValueError("Escala de dolor debe ser 0-10")
        if glasgow is not None and not (3 <= glasgow <= 15):
            raise ValueError("Glasgow debe ser 3-15")

        conn = get_connection(self.db_path)
        try:
            ahora = datetime.utcnow().isoformat()

            existente = conn.execute(
                "SELECT IdEvaluacion FROM EvaluacionClinica WHERE IdTriaje = ?",
                (id_triaje,),
            ).fetchone()

            if existente:
                conn.execute(
                    """UPDATE EvaluacionClinica SET
                       MotivoTextoLibre=?, MotivoCategoria=?, EscalaDolor=?,
                       Glasgow=?, NivelConciencia=?, Diabetes=?, Hipertension=?,
                       EnfermedadRenal=?, Embarazo=?, Cancer=?, Cardiopatias=?,
                       EnfermedadPulmonar=?, CirugiasRecientes=?,
                       MedicacionRelevante=?, Alergias=?, Observaciones=?,
                       EpisodiosPreviosUrgencias=?, FechaRegistro=?
                       WHERE IdTriaje=?""",
                    (motivo_texto_libre, motivo_categoria, escala_dolor,
                     glasgow, nivel_conciencia,
                     1 if diabetes else 0, 1 if hipertension else 0,
                     1 if enfermedad_renal else 0, 1 if embarazo else 0,
                     1 if cancer else 0, 1 if cardiopatias else 0,
                     1 if enfermedad_pulmonar else 0, 1 if cirugias_recientes else 0,
                     medicacion_relevante, alergias, observaciones,
                     episodios_previos, ahora, id_triaje),
                )
            else:
                id_eval = f"ev-{uuid.uuid4().hex[:12]}"
                conn.execute(
                    """INSERT INTO EvaluacionClinica
                       (IdEvaluacion, IdTriaje, MotivoTextoLibre, MotivoCategoria,
                        EscalaDolor, Glasgow, NivelConciencia, Diabetes, Hipertension,
                        EnfermedadRenal, Embarazo, Cancer, Cardiopatias,
                        EnfermedadPulmonar, CirugiasRecientes, MedicacionRelevante,
                        Alergias, Observaciones, EpisodiosPreviosUrgencias, FechaRegistro)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (id_eval, id_triaje, motivo_texto_libre, motivo_categoria,
                     escala_dolor, glasgow, nivel_conciencia,
                     1 if diabetes else 0, 1 if hipertension else 0,
                     1 if enfermedad_renal else 0, 1 if embarazo else 0,
                     1 if cancer else 0, 1 if cardiopatias else 0,
                     1 if enfermedad_pulmonar else 0, 1 if cirugias_recientes else 0,
                     medicacion_relevante, alergias, observaciones,
                     episodios_previos, ahora),
                )

            conn.commit()

            return {
                "motivo_categoria": motivo_categoria,
                "motivo_texto_libre": motivo_texto_libre,
                "escala_dolor": escala_dolor,
                "glasgow": glasgow,
                "nivel_conciencia": nivel_conciencia,
                "antecedentes": {
                    "diabetes": diabetes,
                    "hipertension": hipertension,
                    "enfermedad_renal": enfermedad_renal,
                    "embarazo": embarazo,
                    "cancer": cancer,
                    "cardiopatias": cardiopatias,
                    "enfermedad_pulmonar": enfermedad_pulmonar,
                    "cirugias_recientes": cirugias_recientes,
                },
                "alergias": alergias,
                "observaciones": observaciones,
                "episodios_previos": episodios_previos,
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_clinical_evaluation(self, id_triaje: str) -> Optional[Dict]:
        """Obtiene la evaluación clínica de un evento."""
        conn = get_connection(self.db_path)
        try:
            row = conn.execute(
                "SELECT * FROM EvaluacionClinica WHERE IdTriaje = ?",
                (id_triaje,),
            ).fetchone()
            return row_to_dict(row) if row else None
        finally:
            conn.close()

    # ==================================================================
    # RECLASIFICACIÓN (HU-E2-07)
    # ==================================================================

    def reclassify(
        self,
        id_triaje: str,
        nuevo_nivel: str,
        motivo: str,
        usuario: str,
    ) -> Dict:
        """
        Reclasifica un triaje ya validado. Requiere motivo obligatorio.
        Preserva el nivel anterior en el campo MotivoDiscrepancia.
        """
        if nuevo_nivel not in NIVELES_TRIAGE:
            raise ValueError(f"Nivel de triaje inválido: {nuevo_nivel}")
        if not motivo or not motivo.strip():
            raise ValueError("El motivo de reclasificación es obligatorio.")

        conn = get_connection(self.db_path)
        try:
            evento = conn.execute(
                "SELECT * FROM EventoTriaje WHERE IdTriaje = ?",
                (id_triaje,),
            ).fetchone()
            if not evento:
                raise ValueError(f"Evento {id_triaje} no encontrado.")

            estado_actual = evento["Estado"]
            if estado_actual not in ("Validado", "Clasificado"):
                raise ValueError(
                    f"Solo se puede reclasificar desde 'Validado' o 'Clasificado'. "
                    f"Estado actual: {estado_actual}"
                )

            nivel_anterior = evento["NivelAsignadoProfesional"]
            ahora = datetime.utcnow().isoformat()

            conn.execute(
                """UPDATE EventoTriaje SET
                   NivelAsignadoProfesional = ?,
                   MotivoDiscrepancia = ?,
                   Estado = 'Clasificado',
                   FechaModificacion = ?
                   WHERE IdTriaje = ?""",
                (nuevo_nivel, motivo, ahora, id_triaje),
            )

            # Auditoría
            self._auditar(
                conn, usuario, "Reclasificacion", "EventoTriaje", id_triaje,
                json.dumps({"nivel_anterior": nivel_anterior, "estado": estado_actual}),
                json.dumps({"nivel_nuevo": nuevo_nivel, "motivo": motivo}),
            )

            conn.commit()

            return {
                "id_triaje": id_triaje,
                "nivel_anterior": nivel_anterior,
                "nivel_nuevo": nuevo_nivel,
                "motivo": motivo,
                "fecha": ahora,
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # ==================================================================
    # CIERRE DE EVENTO (HU-E2-08)
    # ==================================================================

    def close_event(
        self,
        id_triaje: str,
        nivel_profesional: str,
        usuario: str,
        motivo_discrepancia: Optional[str] = None,
    ) -> Dict:
        """
        Cierra el evento de triaje.
        Valida concordancia entre IA (si existe) y profesional.
        Si hay discrepancia, exige motivo.
        """
        if nivel_profesional not in NIVELES_TRIAGE:
            raise ValueError(f"Nivel de triaje inválido: {nivel_profesional}")

        conn = get_connection(self.db_path)
        try:
            evento = conn.execute(
                "SELECT * FROM EventoTriaje WHERE IdTriaje = ?",
                (id_triaje,),
            ).fetchone()
            if not evento:
                raise ValueError(f"Evento {id_triaje} no encontrado.")

            estado_actual = evento["Estado"]
            # Permitir cierre desde Validado o Clasificado (sin validación IA)
            if estado_actual not in ("Validado", "Clasificado", "PendienteIA", "EnEvaluacion"):
                raise ValueError(
                    f"No se puede cerrar desde estado '{estado_actual}'. "
                    f"Debe estar en Validado, Clasificado, PendienteIA o EnEvaluacion."
                )

            nivel_ia = evento["NivelSugeridoIA"]
            concordancia = None

            # Si hay nivel IA, calcular concordancia
            if nivel_ia:
                concordancia = 1 if nivel_ia == nivel_profesional else 0

                # Si hay discrepancia y no hay motivo → error
                if concordancia == 0 and (not motivo_discrepancia or not motivo_discrepancia.strip()):
                    raise ValueError(
                        "Hay discrepancia entre la IA y el profesional. "
                        "Debe registrar el motivo antes de cerrar."
                    )

            ahora = datetime.utcnow().isoformat()

            conn.execute(
                """UPDATE EventoTriaje SET
                   NivelAsignadoProfesional = ?,
                   Concordancia = ?,
                   MotivoDiscrepancia = ?,
                   Estado = 'Cerrado',
                   FechaHoraCierre = ?,
                   FechaModificacion = ?
                   WHERE IdTriaje = ?""",
                (nivel_profesional, concordancia,
                 motivo_discrepancia, ahora, ahora, id_triaje),
            )

            # Auditoría
            valor_nuevo = {
                "nivel_profesional": nivel_profesional,
                "concordancia": concordancia,
                "estado": "Cerrado",
            }
            self._auditar(
                conn, usuario, "CierreEvento", "EventoTriaje", id_triaje,
                json.dumps({"estado": estado_actual}),
                json.dumps(valor_nuevo),
            )

            conn.commit()

            return {
                "id_triaje": id_triaje,
                "estado": "Cerrado",
                "nivel_profesional": nivel_profesional,
                "nivel_ia": nivel_ia,
                "concordancia": concordancia,
                "fecha_cierre": ahora,
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # ==================================================================
    # UTILIDADES INTERNAS
    # ==================================================================

    def _validar_signo(self, nombre: str, valor, alertas: List[Dict]):
        """Valida un signo vital contra rangos fisiológicos y umbrales de alerta."""
        if valor is None:
            return

        rango = RANGOS_VITALES.get(nombre)
        if rango:
            minimo, maximo = rango
            if valor < minimo or valor > maximo:
                alertas.append({
                    "campo": nombre,
                    "tipo": "error",
                    "mensaje": (
                        f"{nombre.replace('_', ' ').title()} fuera de rango "
                        f"({valor}). Debe estar entre {minimo} y {maximo}."
                    ),
                })

        alerta = ALERTAS_VITALES.get(nombre)
        if alerta:
            umbral_bajo, umbral_alto = alerta
            if umbral_bajo is not None and valor < umbral_bajo:
                alertas.append({
                    "campo": nombre,
                    "tipo": "critico",
                    "mensaje": _MENSAJES_ALERTA.get(nombre, f"{nombre}: valor crítico bajo"),
                })
            if umbral_alto is not None and valor > umbral_alto:
                alertas.append({
                    "campo": nombre,
                    "tipo": "critico",
                    "mensaje": _MENSAJES_ALERTA.get(nombre, f"{nombre}: valor crítico alto"),
                })

    def _auditar_cambio_estado(
        self, conn, id_triaje: str, estado_anterior: str,
        estado_nuevo: str, usuario: str, motivo: str,
    ):
        """Registra un cambio de estado en la tabla de auditoría."""
        self._auditar(
            conn, usuario,
            f"CambioEstado_{estado_anterior}_a_{estado_nuevo}",
            "EventoTriaje", id_triaje,
            json.dumps({"estado": estado_anterior}),
            json.dumps({"estado": estado_nuevo, "motivo": motivo}),
        )

    def _auditar(
        self, conn, usuario: str, accion: str,
        entidad: str, id_entidad: str,
        valor_anterior: str, valor_nuevo: str,
    ):
        """Inserta un registro de auditoría."""
        id_aud = f"aud-{uuid.uuid4().hex[:12]}"
        ahora = datetime.utcnow().isoformat()
        conn.execute(
            """INSERT INTO Auditoria
               (IdAuditoria, Usuario, FechaHora, Accion, EntidadAfectada,
                IdEntidad, ValorAnterior, ValorNuevo)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (id_aud, usuario, ahora, accion, entidad, id_entidad,
             valor_anterior, valor_nuevo),
        )


_MENSAJES_ALERTA = {
    "saturacion_o2": "⚠️ SpO₂ crítica (< 90%) — posible hipoxemia",
    "frecuencia_respiratoria": "⚠️ FR elevada (> 25 rpm) — posible dificultad respiratoria",
    "presion_sistolica": "⚠️ PA sistólica < 90 mmHg — posible hipotensión",
    "temperatura": "⚠️ Temperatura < 35°C — posible hipotermia",
    "frecuencia_cardiaca": "⚠️ FC elevada (> 120 lpm) — posible taquicardia",
}
