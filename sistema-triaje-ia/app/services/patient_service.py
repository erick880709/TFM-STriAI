"""
Servicio de Pacientes.
Cubre: HU-E2-01 (Registro de paciente), HU-E2-02 (Búsqueda),
       HU-E2-03 (Historial de triajes).
Incluye: Control de cambios (versionado de entidades clínicas).
"""
import sqlite3
import uuid
from datetime import datetime
from typing import Optional, Dict, List

from app.data.database import get_connection, row_to_dict, rows_to_dicts


# ---------------------------------------------------------------------------
# Catálogos del dominio
# ---------------------------------------------------------------------------
TIPOS_DOCUMENTO = ["CC", "TI", "CE", "PA", "RC"]
TIPOS_DOC_LABELS = {
    "CC": "Cédula de Ciudadanía",
    "TI": "Tarjeta de Identidad",
    "CE": "Cédula de Extranjería",
    "PA": "Pasaporte",
    "RC": "Registro Civil",
}
VIAS_LLEGADA = ["Ambulancia", "Particular", "Remision"]
REGIMENES_SALUD = ["Contributivo", "Subsidiado", "Especial", "No afiliado"]
SEXOS = ["M", "F"]
SEXO_LABELS = {"M": "Masculino", "F": "Femenino"}

# ---------------------------------------------------------------------------
# Catálogos de geografía colombiana (Épica 7)
# ---------------------------------------------------------------------------
DEPARTAMENTOS_COLOMBIA = [
    "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bolívar", "Boyacá",
    "Caldas", "Caquetá", "Casanare", "Cauca", "Cesar", "Chocó",
    "Córdoba", "Cundinamarca", "Guainía", "Guaviare", "Huila", "La Guajira",
    "Magdalena", "Meta", "Nariño", "Norte de Santander", "Putumayo",
    "Quindío", "Risaralda", "San Andrés y Providencia", "Santander", "Sucre",
    "Tolima", "Valle del Cauca", "Vaupés", "Vichada",
]

CIUDADES_POR_DEPARTAMENTO = {
    "Amazonas": ["Leticia", "Puerto Nariño"],
    "Antioquia": ["Medellín", "Bello", "Envigado", "Itagüí", "Rionegro", "Apartadó", "Turbo", "Caucasia"],
    "Arauca": ["Arauca", "Saravena", "Tame"],
    "Atlántico": ["Barranquilla", "Soledad", "Malambo", "Puerto Colombia", "Sabanalarga"],
    "Bolívar": ["Cartagena", "Magangué", "Turbaco", "El Carmen de Bolívar"],
    "Boyacá": ["Tunja", "Duitama", "Sogamoso", "Chiquinquirá", "Paipa"],
    "Caldas": ["Manizales", "La Dorada", "Villamaría", "Chinchiná"],
    "Caquetá": ["Florencia", "San Vicente del Caguán"],
    "Casanare": ["Yopal", "Aguazul", "Villanueva"],
    "Cauca": ["Popayán", "Santander de Quilichao", "Puerto Tejada"],
    "Cesar": ["Valledupar", "Aguachica", "Codazzi"],
    "Chocó": ["Quibdó", "Istmina", "Bahía Solano"],
    "Córdoba": ["Montería", "Cereté", "Lorica", "Sahagún"],
    "Cundinamarca": ["Bogotá D.C.", "Soacha", "Chía", "Facatativá", "Zipaquirá", "Fusagasugá", "Girardot", "Mosquera"],
    "Guainía": ["Inírida"],
    "Guaviare": ["San José del Guaviare"],
    "Huila": ["Neiva", "Pitalito", "Garzón", "La Plata"],
    "La Guajira": ["Riohacha", "Maicao", "Uribia"],
    "Magdalena": ["Santa Marta", "Ciénaga", "Fundación"],
    "Meta": ["Villavicencio", "Acacías", "Granada"],
    "Nariño": ["Pasto", "Ipiales", "Tumaco"],
    "Norte de Santander": ["Cúcuta", "Ocaña", "Pamplona"],
    "Putumayo": ["Mocoa", "Puerto Asís"],
    "Quindío": ["Armenia", "Calarcá", "Montenegro"],
    "Risaralda": ["Pereira", "Dosquebradas", "Santa Rosa de Cabal"],
    "San Andrés y Providencia": ["San Andrés", "Providencia"],
    "Santander": ["Bucaramanga", "Floridablanca", "Barrancabermeja", "Girón", "Piedecuesta"],
    "Sucre": ["Sincelejo", "Corozal", "Tolú"],
    "Tolima": ["Ibagué", "Espinal", "Melgar"],
    "Valle del Cauca": ["Cali", "Palmira", "Buenaventura", "Tuluá", "Cartago", "Buga", "Jamundí"],
    "Vaupés": ["Mitú"],
    "Vichada": ["Puerto Carreño"],
}


class PatientService:
    """Gestiona el ciclo de vida del paciente: registro, búsqueda, historial."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    # ------------------------------------------------------------------
    # HU-E2-01: Registrar nuevo paciente (ampliado Épica 7)
    # ------------------------------------------------------------------
    def register_patient(
        self,
        tipo_documento: str,
        numero_documento: str,
        fecha_nacimiento: str,
        sexo: str,
        via_llegada: str,
        regimen_salud: Optional[str] = None,
        eps: Optional[str] = None,
        episodios_previos: int = 0,
        # -- Campos ampliados Épica 7 --
        nombres: str = "",
        apellidos: str = "",
        telefono: str = "",
        correo: Optional[str] = None,
        contacto_emergencia: str = "",
        numero_contacto_emergencia: str = "",
        departamento: str = "",
        ciudad: str = "",
        direccion_residencia: str = "",
    ) -> Dict:
        """
        Registra un nuevo paciente.
        Lanza ValueError si el documento ya existe (duplicado detectado).
        Lanza ValueError si los datos de contacto no son válidos.
        Retorna el dict del paciente creado.
        """
        # Validar catálogos
        if tipo_documento not in TIPOS_DOCUMENTO:
            raise ValueError(f"Tipo de documento inválido: {tipo_documento}")
        if sexo not in SEXOS:
            raise ValueError(f"Sexo inválido: {sexo}")
        if via_llegada not in VIAS_LLEGADA:
            raise ValueError(f"Vía de llegada inválida: {via_llegada}")
        if regimen_salud and regimen_salud not in REGIMENES_SALUD:
            raise ValueError(f"Régimen de salud inválido: {regimen_salud}")

        # Validar campos ampliados (Épica 7)
        if telefono and not self._validar_telefono(telefono):
            raise ValueError("Teléfono inválido. Debe tener al menos 10 dígitos.")
        if correo and not self._validar_correo(correo):
            raise ValueError("Correo electrónico inválido.")
        if numero_contacto_emergencia and not self._validar_telefono(numero_contacto_emergencia):
            raise ValueError("Número de contacto de emergencia inválido.")
        if departamento and departamento not in DEPARTAMENTOS_COLOMBIA:
            raise ValueError(f"Departamento inválido: {departamento}")
        if ciudad and departamento and ciudad not in CIUDADES_POR_DEPARTAMENTO.get(departamento, []):
            raise ValueError(f"Ciudad '{ciudad}' no pertenece al departamento '{departamento}'")

        # Calcular edad
        try:
            edad = self._calcular_edad(fecha_nacimiento)
        except (ValueError, TypeError):
            raise ValueError("Fecha de nacimiento inválida. Use formato YYYY-MM-DD.")

        if edad < 0 or edad > 120:
            raise ValueError(f"Edad calculada fuera de rango: {edad}")

        conn = get_connection(self.db_path)
        try:
            # Verificar duplicado
            existente = conn.execute(
                "SELECT IdPaciente, NumeroDocumento, FechaRegistro FROM Paciente WHERE NumeroDocumento = ?",
                (numero_documento,),
            ).fetchone()

            if existente:
                existente_dict = row_to_dict(existente)
                ultimo = conn.execute(
                    """SELECT e.FechaHoraIngreso, e.NivelSugeridoIA, e.Estado
                       FROM EventoTriaje e
                       WHERE e.IdPaciente = ?
                       ORDER BY e.FechaHoraIngreso DESC LIMIT 1""",
                    (existente["IdPaciente"],),
                ).fetchone()
                total_episodios = conn.execute(
                    "SELECT COUNT(*) as cnt FROM EventoTriaje WHERE IdPaciente = ?",
                    (existente["IdPaciente"],),
                ).fetchone()["cnt"]

                raise DuplicatePatientError(
                    paciente_existente=existente_dict,
                    ultimo_triaje=row_to_dict(ultimo) if ultimo else None,
                    total_episodios=total_episodios,
                )

            # Crear paciente
            id_paciente = f"pac-{uuid.uuid4().hex[:12]}"
            ahora = datetime.utcnow().isoformat()

            conn.execute(
                """INSERT INTO Paciente
                   (IdPaciente, TipoDocumento, NumeroDocumento, FechaNacimiento,
                    Edad, Sexo, RegimenSalud, EPS, ViaLlegada,
                    EpisodiosPreviosUrgencias, FechaRegistro,
                    Nombres, Apellidos, Telefono, Correo,
                    ContactoEmergencia, NumeroContactoEmergencia,
                    Departamento, Ciudad, DireccionResidencia)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                           ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    id_paciente, tipo_documento, numero_documento, fecha_nacimiento,
                    edad, sexo, regimen_salud, eps, via_llegada,
                    episodios_previos, ahora,
                    nombres, apellidos, telefono, correo,
                    contacto_emergencia, numero_contacto_emergencia,
                    departamento, ciudad, direccion_residencia,
                ),
            )
            conn.commit()

            return {
                "id_paciente": id_paciente,
                "tipo_documento": tipo_documento,
                "numero_documento": numero_documento,
                "fecha_nacimiento": fecha_nacimiento,
                "edad": edad,
                "sexo": sexo,
                "regimen_salud": regimen_salud,
                "eps": eps,
                "via_llegada": via_llegada,
                "episodios_previos": episodios_previos,
                "fecha_registro": ahora,
                # Campos ampliados Épica 7
                "nombres": nombres,
                "apellidos": apellidos,
                "telefono": telefono,
                "correo": correo,
                "contacto_emergencia": contacto_emergencia,
                "numero_contacto_emergencia": numero_contacto_emergencia,
                "departamento": departamento,
                "ciudad": ciudad,
                "direccion_residencia": direccion_residencia,
            }
        except DuplicatePatientError:
            raise
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # HU-E2-02: Buscar paciente existente (ampliado Épica 7)
    # ------------------------------------------------------------------
    def search_patients(
        self,
        query: str = "",
        tipo_documento: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Busca pacientes por número de documento, nombres o apellidos
        (búsqueda parcial en documento, nombres y apellidos).
        """
        conn = get_connection(self.db_path)
        try:
            sql = """SELECT p.*,
                       (SELECT COUNT(*) FROM EventoTriaje e WHERE e.IdPaciente = p.IdPaciente) as total_triages,
                       (SELECT MAX(e.FechaHoraIngreso) FROM EventoTriaje e WHERE e.IdPaciente = p.IdPaciente) as ultimo_triaje
                    FROM Paciente p WHERE 1=1"""
            params: List = []

            if query.strip():
                q = f"%{query.strip()}%"
                sql += " AND (p.NumeroDocumento LIKE ? OR p.Nombres LIKE ? OR p.Apellidos LIKE ?)"
                params.extend([q, q, q])

            if tipo_documento:
                sql += " AND p.TipoDocumento = ?"
                params.append(tipo_documento)

            sql += " ORDER BY p.FechaRegistro DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(sql, params).fetchall()
            return rows_to_dicts(rows)
        finally:
            conn.close()

    def get_patient_by_document(self, numero_documento: str) -> Optional[Dict]:
        """Obtiene un paciente por su número de documento exacto."""
        conn = get_connection(self.db_path)
        try:
            row = conn.execute(
                "SELECT * FROM Paciente WHERE NumeroDocumento = ?",
                (numero_documento,),
            ).fetchone()
            return row_to_dict(row) if row else None
        finally:
            conn.close()

    def get_patient_by_id(self, id_paciente: str) -> Optional[Dict]:
        """Obtiene un paciente por su ID interno."""
        conn = get_connection(self.db_path)
        try:
            row = conn.execute(
                "SELECT * FROM Paciente WHERE IdPaciente = ?",
                (id_paciente,),
            ).fetchone()
            return row_to_dict(row) if row else None
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # HU-E2-03: Historial de triajes del paciente
    # ------------------------------------------------------------------
    def get_patient_triage_history(self, id_paciente: str) -> List[Dict]:
        """
        Retorna todos los eventos de triaje de un paciente,
        ordenados del más reciente al más antiguo.
        """
        conn = get_connection(self.db_path)
        try:
            rows = conn.execute(
                """SELECT e.*,
                       sv.Temperatura, sv.FrecuenciaCardiaca, sv.FrecuenciaRespiratoria,
                       sv.SaturacionO2, sv.PresionSistolica, sv.PresionDiastolica,
                       sv.IMC,
                       ec.MotivoCategoria, ec.EscalaDolor, ec.Glasgow,
                       ec.NivelConciencia
                FROM EventoTriaje e
                LEFT JOIN SignosVitales sv ON e.IdTriaje = sv.IdTriaje
                LEFT JOIN EvaluacionClinica ec ON e.IdTriaje = ec.IdTriaje
                WHERE e.IdPaciente = ?
                ORDER BY e.FechaHoraIngreso DESC""",
                (id_paciente,),
            ).fetchall()
            return rows_to_dicts(rows)
        finally:
            conn.close()

    def update_episodios_previos(self, id_paciente: str) -> int:
        """Recalcula el contador de episodios previos desde EventoTriaje."""
        conn = get_connection(self.db_path)
        try:
            total = conn.execute(
                "SELECT COUNT(*) as cnt FROM EventoTriaje WHERE IdPaciente = ?",
                (id_paciente,),
            ).fetchone()["cnt"]
            conn.execute(
                "UPDATE Paciente SET EpisodiosPreviosUrgencias = ? WHERE IdPaciente = ?",
                (total, id_paciente),
            )
            conn.commit()
            return total
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Búsqueda de triajes por número de documento del paciente
    # ------------------------------------------------------------------
    def search_triages_by_documento(
        self,
        numero_documento: str,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Busca eventos de triaje usando el número de documento del paciente.
        Este es el método principal de búsqueda de triajes — no se busca por ID interno.
        """
        conn = get_connection(self.db_path)
        try:
            rows = conn.execute(
                """SELECT e.*, p.TipoDocumento, p.NumeroDocumento,
                          p.Nombres, p.Apellidos, p.Edad as EdadPaciente, p.Sexo
                   FROM EventoTriaje e
                   JOIN Paciente p ON e.IdPaciente = p.IdPaciente
                   WHERE p.NumeroDocumento LIKE ?
                   ORDER BY e.FechaHoraIngreso DESC
                   LIMIT ?""",
                (f"%{numero_documento.strip()}%", limit),
            ).fetchall()
            return rows_to_dicts(rows) if rows else []
        finally:
            conn.close()

    def get_active_triages_by_documento(self, numero_documento: str) -> List[Dict]:
        """
        Obtiene los triajes activos (no cerrados) de un paciente por su documento.
        Útil para verificar si un paciente ya tiene un triaje en curso.
        """
        conn = get_connection(self.db_path)
        try:
            rows = conn.execute(
                """SELECT e.* FROM EventoTriaje e
                   JOIN Paciente p ON e.IdPaciente = p.IdPaciente
                   WHERE p.NumeroDocumento = ? AND e.Estado NOT IN ('Cerrado', 'Cancelado')
                   ORDER BY e.FechaHoraIngreso DESC""",
                (numero_documento.strip(),),
            ).fetchall()
            return rows_to_dicts(rows) if rows else []
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Control de Cambios (versionado de entidades clínicas)
    # ------------------------------------------------------------------
    def registrar_cambio(
        self,
        entidad: str,
        id_entidad: str,
        campo: str,
        valor_anterior: Optional[str],
        valor_nuevo: str,
        usuario: str,
        numero_documento: Optional[str] = None,
        motivo: Optional[str] = None,
    ) -> str:
        """
        Registra un cambio en el Control de Cambios para trazabilidad clínica.
        Cada modificación de datos del paciente o triaje debe pasar por aquí.
        """
        conn = get_connection(self.db_path)
        try:
            id_cc = f"cc-{uuid.uuid4().hex[:12]}"
            ahora = datetime.utcnow().isoformat()

            # Obtener versión actual
            current_version = conn.execute(
                """SELECT MAX(Version) as max_v FROM ControlCambios
                   WHERE Entidad = ? AND IdEntidad = ?""",
                (entidad, id_entidad),
            ).fetchone()
            new_version = (current_version["max_v"] or 0) + 1

            conn.execute(
                """INSERT INTO ControlCambios
                   (IdControlCambios, Entidad, IdEntidad, CampoModificado,
                    ValorAnterior, ValorNuevo, Usuario, FechaHora, Motivo,
                    NumeroDocumento, Version)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    id_cc, entidad, id_entidad, campo,
                    str(valor_anterior) if valor_anterior is not None else None,
                    str(valor_nuevo),
                    usuario, ahora, motivo,
                    numero_documento, new_version,
                ),
            )
            conn.commit()
            return id_cc
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_historial_cambios(
        self,
        entidad: Optional[str] = None,
        id_entidad: Optional[str] = None,
        numero_documento: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """
        Consulta el historial de cambios de una entidad o paciente.
        """
        conn = get_connection(self.db_path)
        try:
            where = []
            params = []
            if entidad:
                where.append("Entidad = ?")
                params.append(entidad)
            if id_entidad:
                where.append("IdEntidad = ?")
                params.append(id_entidad)
            if numero_documento:
                where.append("NumeroDocumento = ?")
                params.append(numero_documento.strip())

            where_sql = " AND ".join(where) if where else "1=1"
            rows = conn.execute(
                f"""SELECT * FROM ControlCambios
                    WHERE {where_sql}
                    ORDER BY FechaHora DESC LIMIT ?""",
                params + [limit],
            ).fetchall()
            return rows_to_dicts(rows) if rows else []
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    @staticmethod
    def _calcular_edad(fecha_nacimiento: str) -> int:
        """Calcula la edad en años a partir de una fecha YYYY-MM-DD."""
        nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        hoy = datetime.utcnow()
        edad = hoy.year - nac.year
        if (hoy.month, hoy.day) < (nac.month, nac.day):
            edad -= 1
        return edad

    @staticmethod
    def _validar_telefono(telefono: str) -> bool:
        """Valida que el teléfono tenga al menos 10 dígitos (formato colombiano)."""
        digitos = ''.join(c for c in telefono if c.isdigit())
        return len(digitos) >= 10

    @staticmethod
    def _validar_correo(correo: str) -> bool:
        """Valida formato básico de correo electrónico (contiene @ y .)."""
        return "@" in correo and "." in correo.split("@")[-1]


class DuplicatePatientError(Exception):
    """Se lanza cuando se intenta registrar un paciente con documento duplicado."""

    def __init__(
        self,
        paciente_existente: Dict,
        ultimo_triaje: Optional[Dict],
        total_episodios: int,
    ):
        self.paciente_existente = paciente_existente
        self.ultimo_triaje = ultimo_triaje
        self.total_episodios = total_episodios
        super().__init__(
            f"Paciente con documento {paciente_existente.get('numero_documento')} ya existe"
        )
