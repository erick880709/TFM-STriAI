"""
Inicialización de la base de datos SQLite.
Crea las 12 tablas del modelo de dominio + usuarios + auditoría + modelos.
Ejecuta datos semilla para catálogos.
"""
import sqlite3
import os
from datetime import datetime

SCHEMA_SQL = """
-- ============================================================
-- TABLAS DEL MODELO DE DOMINIO (ENT-001 a ENT-012 + extendidas)
-- ============================================================

CREATE TABLE IF NOT EXISTS Paciente (
    IdPaciente TEXT PRIMARY KEY,
    TipoDocumento TEXT NOT NULL CHECK(TipoDocumento IN ('CC','TI','CE','PA','RC')),
    NumeroDocumento TEXT NOT NULL UNIQUE,
    FechaNacimiento TEXT NOT NULL,
    Edad INTEGER NOT NULL,
    Sexo TEXT NOT NULL CHECK(Sexo IN ('M','F')),
    RegimenSalud TEXT CHECK(RegimenSalud IN ('Contributivo','Subsidiado','Especial','No afiliado')),
    EPS TEXT,
    Municipio TEXT,
    ViaLlegada TEXT NOT NULL CHECK(ViaLlegada IN ('Ambulancia','Particular','Remision')),
    EpisodiosPreviosUrgencias INTEGER DEFAULT 0,
    FechaRegistro TEXT NOT NULL DEFAULT (datetime('now')),
    -- Campos ampliados (Épica 7 — Datos del Paciente)
    Nombres TEXT NOT NULL DEFAULT '',
    Apellidos TEXT NOT NULL DEFAULT '',
    Telefono TEXT NOT NULL DEFAULT '',
    Correo TEXT,
    ContactoEmergencia TEXT NOT NULL DEFAULT '',
    NumeroContactoEmergencia TEXT NOT NULL DEFAULT '',
    Departamento TEXT NOT NULL DEFAULT '',
    Ciudad TEXT NOT NULL DEFAULT '',
    DireccionResidencia TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS EventoTriaje (
    IdTriaje TEXT PRIMARY KEY,
    IdPaciente TEXT NOT NULL REFERENCES Paciente(IdPaciente),
    FechaHoraIngreso TEXT NOT NULL DEFAULT (datetime('now')),
    FechaHoraClasificacion TEXT,
    FechaHoraCierre TEXT,
    Estado TEXT NOT NULL DEFAULT 'Registrado'
        CHECK(Estado IN ('Registrado','EnEvaluacion','PendienteIA','Clasificado','Validado','Cerrado','Cancelado')),
    NivelSugeridoIA TEXT CHECK(NivelSugeridoIA IN ('I','II','III','IV','V')),
    ProbabilidadesIA TEXT,  -- JSON
    NivelAsignadoProfesional TEXT CHECK(NivelAsignadoProfesional IN ('I','II','III','IV','V')),
    Concordancia INTEGER,   -- 0/1, calculado
    MotivoDiscrepancia TEXT,
    VersionModeloUsado TEXT,
    ProfesionalResponsable TEXT,
    FechaModificacion TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS SignosVitales (
    IdSignosVitales TEXT PRIMARY KEY,
    IdTriaje TEXT NOT NULL UNIQUE REFERENCES EventoTriaje(IdTriaje),
    Temperatura REAL CHECK(Temperatura BETWEEN 30 AND 45),
    FrecuenciaCardiaca INTEGER CHECK(FrecuenciaCardiaca > 0),
    FrecuenciaRespiratoria INTEGER CHECK(FrecuenciaRespiratoria > 0),
    SaturacionO2 INTEGER CHECK(SaturacionO2 BETWEEN 0 AND 100),
    PresionSistolica INTEGER CHECK(PresionSistolica > 0),
    PresionDiastolica INTEGER CHECK(PresionDiastolica > 0 AND PresionDiastolica < PresionSistolica),
    Peso REAL,
    Talla REAL,
    IMC REAL,
    FechaRegistro TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS EvaluacionClinica (
    IdEvaluacion TEXT PRIMARY KEY,
    IdTriaje TEXT NOT NULL UNIQUE REFERENCES EventoTriaje(IdTriaje),
    MotivoTextoLibre TEXT,
    MotivoCategoria TEXT NOT NULL CHECK(MotivoCategoria IN (
        'Dolor toracico','Trauma','Disnea','Dolor abdominal','Fiebre',
        'Cefalea','Convulsiones','Hemorragia','Intoxicacion','Otro'
    )),
    EscalaDolor INTEGER CHECK(EscalaDolor BETWEEN 0 AND 10),
    Glasgow INTEGER CHECK(Glasgow BETWEEN 3 AND 15),
    NivelConciencia TEXT CHECK(NivelConciencia IN ('Alerta','Somnoliento','Obnubilado','Inconsciente')),
    Diabetes INTEGER DEFAULT 0,
    Hipertension INTEGER DEFAULT 0,
    EnfermedadRenal INTEGER DEFAULT 0,
    Embarazo INTEGER DEFAULT 0,
    Cancer INTEGER DEFAULT 0,
    Cardiopatias INTEGER DEFAULT 0,
    EnfermedadPulmonar INTEGER DEFAULT 0,
    CirugiasRecientes INTEGER DEFAULT 0,
    MedicacionRelevante TEXT,
    EpisodiosPreviosUrgencias INTEGER,
    Alergias TEXT,
    Observaciones TEXT,
    FechaRegistro TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS PrediccionIA (
    IdPrediccion TEXT PRIMARY KEY,
    IdTriaje TEXT NOT NULL REFERENCES EventoTriaje(IdTriaje),
    IdModelo TEXT,
    NivelPredicho TEXT NOT NULL CHECK(NivelPredicho IN ('I','II','III','IV','V')),
    Probabilidades TEXT NOT NULL,  -- JSON {I: p1, II: p2, III: p3, IV: p4, V: p5}
    Confianza REAL NOT NULL,
    TiempoInferencia REAL NOT NULL,
    FechaHora TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ExplicacionSHAP (
    IdExplicacion TEXT PRIMARY KEY,
    IdPrediccion TEXT NOT NULL UNIQUE REFERENCES PrediccionIA(IdPrediccion),
    VariablesSHAP TEXT NOT NULL,  -- JSON
    ValorBase REAL NOT NULL,
    FechaHora TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS Modelo (
    IdModelo TEXT PRIMARY KEY,
    Nombre TEXT NOT NULL UNIQUE,
    Version TEXT NOT NULL,
    Arquitectura TEXT NOT NULL CHECK(Arquitectura IN ('Early Fusion','Late Fusion','Unimodal')),
    Algoritmo TEXT NOT NULL,
    Hiperparametros TEXT,   -- JSON
    DatasetEntrenamiento TEXT,
    F1Score REAL,
    Precision REAL,
    Recall REAL,
    AUCROC REAL,
    AUPRC REAL,
    Estado TEXT NOT NULL DEFAULT 'EnValidacion'
        CHECK(Estado IN ('Activo','Inactivo','EnValidacion')),
    FechaRegistro TEXT NOT NULL DEFAULT (datetime('now')),
    RegistradoPor TEXT
);

CREATE TABLE IF NOT EXISTS Usuario (
    IdUsuario TEXT PRIMARY KEY,
    NombreUsuario TEXT NOT NULL UNIQUE,
    PasswordHash TEXT NOT NULL,
    Email TEXT,
    Rol TEXT NOT NULL CHECK(Rol IN ('Administrador','Medico','Enfermera','Investigador','Auditor')),
    Activo INTEGER NOT NULL DEFAULT 1,
    IntentosFallidos INTEGER NOT NULL DEFAULT 0,
    BloqueadoHasta TEXT,
    HistorialPasswords TEXT,  -- JSON array de últimos 3 hashes
    FechaCreacion TEXT NOT NULL DEFAULT (datetime('now')),
    UltimoAcceso TEXT
);

CREATE TABLE IF NOT EXISTS Auditoria (
    IdAuditoria TEXT PRIMARY KEY,
    Usuario TEXT NOT NULL,
    FechaHora TEXT NOT NULL DEFAULT (datetime('now')),
    Accion TEXT NOT NULL,
    EntidadAfectada TEXT,
    IdEntidad TEXT,
    ValorAnterior TEXT,   -- JSON
    ValorNuevo TEXT,      -- JSON
    IP TEXT,
    Dispositivo TEXT,
    Observaciones TEXT
);

-- Tabla de configuración del sistema
CREATE TABLE IF NOT EXISTS Configuracion (
    Clave TEXT PRIMARY KEY,
    Valor TEXT NOT NULL,
    Descripcion TEXT
);

-- Tabla de control de cambios (versionado de entidades clínicas)
CREATE TABLE IF NOT EXISTS ControlCambios (
    IdControlCambios TEXT PRIMARY KEY,
    Entidad TEXT NOT NULL,              -- Paciente, EventoTriaje, SignosVitales...
    IdEntidad TEXT NOT NULL,            -- ID del registro modificado
    CampoModificado TEXT NOT NULL,      -- Nombre del campo cambiado
    ValorAnterior TEXT,                 -- Valor antes del cambio
    ValorNuevo TEXT,                    -- Valor después del cambio
    Usuario TEXT NOT NULL,              -- Quién hizo el cambio
    FechaHora TEXT NOT NULL DEFAULT (datetime('now')),
    Motivo TEXT,                        -- Motivo del cambio (obligatorio para cambios clínicos)
    NumeroDocumento TEXT,               -- Documento del paciente (para trazabilidad)
    Version INTEGER NOT NULL DEFAULT 1  -- Número de versión del registro
);

-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_paciente_documento ON Paciente(NumeroDocumento);
CREATE INDEX IF NOT EXISTS idx_triaje_paciente ON EventoTriaje(IdPaciente);
CREATE INDEX IF NOT EXISTS idx_triaje_estado ON EventoTriaje(Estado);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON Auditoria(FechaHora);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON Auditoria(Usuario);
CREATE INDEX IF NOT EXISTS idx_auditoria_accion ON Auditoria(Accion);
CREATE INDEX IF NOT EXISTS idx_prediccion_triaje ON PrediccionIA(IdTriaje);
CREATE INDEX IF NOT EXISTS idx_modelo_estado ON Modelo(Estado);
CREATE INDEX IF NOT EXISTS idx_usuario_nombre ON Usuario(NombreUsuario);
CREATE INDEX IF NOT EXISTS idx_control_cambios_entidad ON ControlCambios(Entidad, IdEntidad);
CREATE INDEX IF NOT EXISTS idx_control_cambios_documento ON ControlCambios(NumeroDocumento);
CREATE INDEX IF NOT EXISTS idx_control_cambios_fecha ON ControlCambios(FechaHora);
"""

SEED_SQL = """
-- ============================================================
-- DATOS SEMILLA — Catálogos y usuario administrador inicial
-- ============================================================

-- Usuario admin por defecto (password: admin123 — cambiar en producción)
INSERT OR IGNORE INTO Usuario (IdUsuario, NombreUsuario, PasswordHash, Email, Rol)
VALUES (
    'u-admin-001',
    'admin',
    '$2b$12$qhwcjBqc..g7Sqk1eZjVD.zKgwE5TlH0h/XB6SSkDSQg0a4X1cepq',
    'admin@triaje-ia.local',
    'Administrador'
);

-- Usuarios demo para pruebas
INSERT OR IGNORE INTO Usuario (IdUsuario, NombreUsuario, PasswordHash, Email, Rol)
VALUES ('u-enf-001', 'enfermera_01', '$2b$12$qhwcjBqc..g7Sqk1eZjVD.zKgwE5TlH0h/XB6SSkDSQg0a4X1cepq', 'enf@triaje-ia.local', 'Enfermera');
INSERT OR IGNORE INTO Usuario (IdUsuario, NombreUsuario, PasswordHash, Email, Rol)
VALUES ('u-med-001', 'medico_01', '$2b$12$qhwcjBqc..g7Sqk1eZjVD.zKgwE5TlH0h/XB6SSkDSQg0a4X1cepq', 'med@triaje-ia.local', 'Medico');
INSERT OR IGNORE INTO Usuario (IdUsuario, NombreUsuario, PasswordHash, Email, Rol)
VALUES ('u-inv-001', 'investigador_01', '$2b$12$qhwcjBqc..g7Sqk1eZjVD.zKgwE5TlH0h/XB6SSkDSQg0a4X1cepq', 'inv@triaje-ia.local', 'Investigador');
INSERT OR IGNORE INTO Usuario (IdUsuario, NombreUsuario, PasswordHash, Email, Rol)
VALUES ('u-aud-001', 'auditor_01', '$2b$12$qhwcjBqc..g7Sqk1eZjVD.zKgwE5TlH0h/XB6SSkDSQg0a4X1cepq', 'aud@triaje-ia.local', 'Auditor');

-- Configuración por defecto
INSERT OR IGNORE INTO Configuracion (Clave, Valor, Descripcion) VALUES
('session_timeout_minutes', '15', 'Minutos de inactividad antes de cerrar sesión'),
('max_login_attempts', '5', 'Intentos fallidos antes de bloquear cuenta'),
('lockout_minutes', '15', 'Minutos de bloqueo tras exceder intentos'),
('app_version', '1.0.0', 'Versión de la aplicación'),
('app_name', 'Sistema de Triaje Multimodal IA', 'Nombre de la aplicación');
"""


def init_db(db_path: str) -> None:
    """Inicializa la base de datos: crea tablas, aplica migraciones e inserta datos semilla."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_SQL)
    _apply_migrations(conn)
    conn.executescript(SEED_SQL)
    conn.commit()
    conn.close()


def _apply_migrations(conn: sqlite3.Connection) -> None:
    """Aplica migraciones incrementales para BDs existentes (no destructivo)."""
    migraciones = [
        # Épica 7 — Datos ampliados del paciente
        "ALTER TABLE Paciente ADD COLUMN Nombres TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE Paciente ADD COLUMN Apellidos TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE Paciente ADD COLUMN Telefono TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE Paciente ADD COLUMN Correo TEXT",
        "ALTER TABLE Paciente ADD COLUMN ContactoEmergencia TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE Paciente ADD COLUMN NumeroContactoEmergencia TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE Paciente ADD COLUMN Departamento TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE Paciente ADD COLUMN Ciudad TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE Paciente ADD COLUMN DireccionResidencia TEXT NOT NULL DEFAULT ''",
    ]
    for sql in migraciones:
        try:
            conn.execute(sql)
        except sqlite3.OperationalError:
            pass  # Columna ya existe — ignorar


def get_connection(db_path: str) -> sqlite3.Connection:
    """Retorna una conexión a la base de datos con foreign keys activadas."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row: sqlite3.Row) -> dict:
    """
    Convierte un sqlite3.Row (PascalCase) a un dict con claves snake_case.
    Esto permite que los servicios usen snake_case consistente con el resto
    de la capa de negocio, independientemente del casing del schema SQL.
    """
    if row is None:
        return None
    result = {}
    for key in row.keys():
        snake_key = _pascal_to_snake(key)
        result[snake_key] = row[key]
    return result


def rows_to_dicts(rows: list) -> list:
    """Convierte una lista de sqlite3.Row a lista de dicts con claves snake_case."""
    return [row_to_dict(r) for r in rows] if rows else []


def _pascal_to_snake(name: str) -> str:
    """Convierte PascalCase a snake_case. Ej: 'IdPaciente' → 'id_paciente', 'IMC' → 'imc', 'NivelSugeridoIA' → 'nivel_sugerido_ia'."""
    import re
    # Insert underscore before capital letters that follow lowercase or precede lowercase
    s1 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    # Insert underscore before uppercase sequences that precede lowercase
    s2 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s1)
    return s2.lower()
