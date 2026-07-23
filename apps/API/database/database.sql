-- ============================================================================
-- SISTEMA DE CONTROL DE ASISTENCIA - FAMILIA PUES
-- Modelo Fisico v2.2 - PostgreSQL 16+
-- Basado en: ERS KT-ERS-001 v2.2
-- Stack: FastAPI + SQLAlchemy 2.0 + PostgreSQL
-- Autor: Anderson Gomez Tobon
-- Fecha: 22/07/2026
-- Revision: Incorpora 16 observaciones de revision de arquitectura.
-- ============================================================================

SET client_encoding = 'UTF8';
SET timezone = 'America/Bogota';

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. CATALOGOS
-- Sin ENUM: todos parametrizables desde el panel.
-- SERIAL (INTEGER) para FK eficientes en tablas de alto volumen.
-- ============================================================================

-- 1.1 CAT_ESTADO (RF-043)
CREATE TABLE cat_estado (
    id          SERIAL          PRIMARY KEY,
    codigo      VARCHAR(20)     NOT NULL,
    nombre      VARCHAR(50)     NOT NULL,
    descripcion VARCHAR(255),
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cat_estado_codigo UNIQUE (codigo),
    CONSTRAINT ck_cat_estado_codigo CHECK (codigo = UPPER(TRIM(codigo)))
);
COMMENT ON TABLE cat_estado IS 'Catalogo de estados del sistema (RF-043). Aplica a empleados, sedes, usuarios, cargos, dispositivos.';

-- 1.2 CAT_ROL (RF-028)
CREATE TABLE cat_rol (
    id          SERIAL          PRIMARY KEY,
    codigo      VARCHAR(30)     NOT NULL,
    nombre      VARCHAR(50)     NOT NULL,
    id_estado   INTEGER         NOT NULL,
    descripcion VARCHAR(255),
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cat_rol_codigo UNIQUE (codigo),
    CONSTRAINT fk_cat_rol_estado FOREIGN KEY (id_estado) REFERENCES cat_estado(id),
    CONSTRAINT ck_cat_rol_codigo CHECK (codigo = UPPER(TRIM(codigo)))
);
COMMENT ON TABLE cat_rol IS 'Catalogo de roles de acceso (RF-028). Iniciales: SUPER_ADMIN, ADMIN.';

-- 1.3 CAT_CARGO (RF-044)
CREATE TABLE cat_cargo (
    id          SERIAL          PRIMARY KEY,
    codigo      VARCHAR(30)     NOT NULL,
    nombre      VARCHAR(100)    NOT NULL,
    id_estado   INTEGER         NOT NULL,
    descripcion VARCHAR(255),
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cat_cargo_codigo UNIQUE (codigo),
    CONSTRAINT fk_cat_cargo_estado FOREIGN KEY (id_estado) REFERENCES cat_estado(id),
    CONSTRAINT ck_cat_cargo_codigo CHECK (codigo = UPPER(TRIM(codigo)))
);
COMMENT ON TABLE cat_cargo IS 'Catalogo de cargos de empleados (RF-044).';

-- 1.4 CAT_TIPO_REGISTRO (RF-045)
CREATE TABLE cat_tipo_registro (
    id          SERIAL          PRIMARY KEY,
    codigo      VARCHAR(30)     NOT NULL,
    nombre      VARCHAR(50)     NOT NULL,
    id_estado   INTEGER         NOT NULL,
    descripcion VARCHAR(255),
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cat_tipo_registro_codigo UNIQUE (codigo),
    CONSTRAINT fk_cat_tipo_registro_estado FOREIGN KEY (id_estado) REFERENCES cat_estado(id),
    CONSTRAINT ck_cat_tipo_registro_codigo CHECK (codigo = UPPER(TRIM(codigo)))
);
COMMENT ON TABLE cat_tipo_registro IS 'Catalogo de tipos de marcacion (RF-045). Extensible sin rediseno.';

-- 1.5 CAT_NOVEDAD (RF-046)
CREATE TABLE cat_novedad (
    id          SERIAL          PRIMARY KEY,
    codigo      VARCHAR(30)     NOT NULL,
    nombre      VARCHAR(50)     NOT NULL,
    id_estado   INTEGER         NOT NULL,
    color       VARCHAR(7),
    icono       VARCHAR(50),
    descripcion VARCHAR(255),
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cat_novedad_codigo UNIQUE (codigo),
    CONSTRAINT fk_cat_novedad_estado FOREIGN KEY (id_estado) REFERENCES cat_estado(id),
    CONSTRAINT ck_cat_novedad_codigo CHECK (codigo = UPPER(TRIM(codigo))),
    CONSTRAINT ck_cat_novedad_color  CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$')
);
COMMENT ON TABLE cat_novedad IS 'Catalogo de novedades (RF-046). Incluye color e icono para resaltado visual.';

-- [REV-03] 1.6 CAT_ESTADO_TOKEN - Estados del token QR
-- Reemplaza el booleano `consumido` por estados extensibles.
CREATE TABLE cat_estado_token (
    id          SERIAL          PRIMARY KEY,
    codigo      VARCHAR(20)     NOT NULL,
    nombre      VARCHAR(50)     NOT NULL,
    descripcion VARCHAR(255),
    CONSTRAINT uq_cat_estado_token_codigo UNIQUE (codigo),
    CONSTRAINT ck_cat_estado_token_codigo CHECK (codigo = UPPER(TRIM(codigo)))
);
COMMENT ON TABLE cat_estado_token IS '[REV-03] Estados del token QR: GENERADO, ACTIVO, EXPIRADO, CONSUMIDO. Extensible.';

-- ============================================================================
-- 2. TABLAS PRINCIPALES
-- ============================================================================

-- 2.1 SEDE (RF-061 a RF-064)
CREATE TABLE sede (
    id          SERIAL          PRIMARY KEY,
    nombre      VARCHAR(100)    NOT NULL,
    direccion   VARCHAR(255)    NOT NULL,
    id_estado   INTEGER         NOT NULL,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_sede_estado FOREIGN KEY (id_estado) REFERENCES cat_estado(id),
    CONSTRAINT uq_sede_nombre UNIQUE (nombre)
);
COMMENT ON TABLE sede IS 'Puntos de venta (RF-061 a RF-064).';
CREATE INDEX idx_sede_estado ON sede(id_estado);

-- 2.2 DISPOSITIVO (RF-065 a RF-068)
-- [REV-12] Agregado ultimo_ping para monitoreo de conectividad.
CREATE TABLE dispositivo (
    id              SERIAL          PRIMARY KEY,
    id_sede         INTEGER         NOT NULL,
    identificador   VARCHAR(255)    NOT NULL,
    id_estado       INTEGER         NOT NULL,
    descripcion     VARCHAR(255),
    ultimo_ping     TIMESTAMPTZ,    -- [REV-12] Ultimo contacto del dispositivo
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_dispositivo_sede   FOREIGN KEY (id_sede)   REFERENCES sede(id),
    CONSTRAINT fk_dispositivo_estado FOREIGN KEY (id_estado) REFERENCES cat_estado(id),
    CONSTRAINT uq_dispositivo_identificador UNIQUE (identificador)
);
COMMENT ON TABLE dispositivo IS 'Celulares empresariales autorizados (RF-065 a RF-068).';
COMMENT ON COLUMN dispositivo.ultimo_ping IS '[REV-12] Timestamp del ultimo contacto. Util para monitoreo de conectividad.';
CREATE INDEX idx_dispositivo_sede   ON dispositivo(id_sede);
CREATE INDEX idx_dispositivo_estado ON dispositivo(id_estado);

-- 2.3 USUARIO (RF-047 a RF-051)
-- [REV-05] Agregado ultimo_login.
-- [REV-14] password_hash cambiado a TEXT para soportar Argon2 futuro.
CREATE TABLE usuario (
    id              SERIAL          PRIMARY KEY,
    id_rol          INTEGER         NOT NULL,
    id_estado       INTEGER         NOT NULL,
    nombre          VARCHAR(150)    NOT NULL,
    correo          VARCHAR(255)    NOT NULL,
    username        VARCHAR(50)     NOT NULL,
    password_hash   TEXT            NOT NULL,   -- [REV-14] TEXT en vez de VARCHAR(255) para Argon2 futuro
    debe_cambiar_pw BOOLEAN         NOT NULL DEFAULT TRUE,
    ultimo_login    TIMESTAMPTZ,                -- [REV-05] Timestamp del ultimo login exitoso
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_usuario_rol    FOREIGN KEY (id_rol)    REFERENCES cat_rol(id),
    CONSTRAINT fk_usuario_estado FOREIGN KEY (id_estado) REFERENCES cat_estado(id),
    CONSTRAINT uq_usuario_username UNIQUE (username),
    CONSTRAINT uq_usuario_correo   UNIQUE (correo)
);
COMMENT ON TABLE usuario IS 'Usuarios administrativos (RF-047 a RF-051). El empleado NO es usuario.';
COMMENT ON COLUMN usuario.password_hash IS '[REV-14] TEXT para soportar bcrypt hoy y Argon2 manana sin migracion.';
COMMENT ON COLUMN usuario.ultimo_login IS '[REV-05] Se actualiza en cada login exitoso. Util para dashboard y seguridad.';
CREATE INDEX idx_usuario_rol    ON usuario(id_rol);
CREATE INDEX idx_usuario_estado ON usuario(id_estado);
CREATE INDEX idx_usuario_login  ON usuario(username, id_estado);

-- 2.4 EMPLEADO (RF-056 a RF-060)
-- [REV-01] Agregado id_sede_actual FK para saber donde trabaja hoy.
CREATE TABLE empleado (
    id               SERIAL          PRIMARY KEY,
    nombre_completo  VARCHAR(200)    NOT NULL,
    documento        VARCHAR(10)     NOT NULL,
    id_cargo         INTEGER         NOT NULL,
    id_estado        INTEGER         NOT NULL,
    id_sede_actual   INTEGER,        -- [REV-01] Sede donde trabaja actualmente. NULL si no asignado.
    created_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_empleado_cargo      FOREIGN KEY (id_cargo)      REFERENCES cat_cargo(id),
    CONSTRAINT fk_empleado_estado     FOREIGN KEY (id_estado)     REFERENCES cat_estado(id),
    CONSTRAINT fk_empleado_sede_actual FOREIGN KEY (id_sede_actual) REFERENCES sede(id),
    CONSTRAINT uq_empleado_documento  UNIQUE (documento),
    CONSTRAINT ck_empleado_documento  CHECK (documento ~ '^\d{6,10}$')
);
COMMENT ON TABLE empleado IS 'Empleados (RF-056 a RF-060). NO son usuarios. Rotan entre sedes.';
COMMENT ON COLUMN empleado.id_sede_actual IS '[REV-01] Dato derivado del historial vigente (empleado_sede WHERE fecha_fin IS NULL). Debe mantenerse sincronizado mediante transaccion al cambiar de sede: UPDATE empleado + INSERT/UPDATE empleado_sede en una sola TX.';
COMMENT ON COLUMN empleado.documento IS 'Cedula colombiana: solo digitos, 6-10 caracteres (RF-015).';
CREATE INDEX idx_empleado_documento    ON empleado(documento);
CREATE INDEX idx_empleado_cargo        ON empleado(id_cargo);
CREATE INDEX idx_empleado_estado       ON empleado(id_estado);
CREATE INDEX idx_empleado_nombre       ON empleado(nombre_completo);
CREATE INDEX idx_empleado_sede_actual  ON empleado(id_sede_actual);

-- [REV-02] 2.5 EMPLEADO_SEDE - Historial de rotacion entre sedes
CREATE TABLE empleado_sede (
    id              SERIAL          PRIMARY KEY,
    id_empleado     INTEGER         NOT NULL,
    id_sede         INTEGER         NOT NULL,
    fecha_inicio    DATE            NOT NULL DEFAULT CURRENT_DATE,
    fecha_fin       DATE,           -- NULL = asignacion vigente
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_emp_sede_empleado FOREIGN KEY (id_empleado) REFERENCES empleado(id),
    CONSTRAINT fk_emp_sede_sede     FOREIGN KEY (id_sede)     REFERENCES sede(id),
    CONSTRAINT ck_emp_sede_vigencia CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio)
);
COMMENT ON TABLE empleado_sede IS '[REV-02] Historial de asignacion de empleados a sedes. fecha_fin NULL = vigente.';
CREATE INDEX idx_emp_sede_empleado ON empleado_sede(id_empleado, fecha_inicio DESC);
CREATE INDEX idx_emp_sede_sede     ON empleado_sede(id_sede);
CREATE INDEX idx_emp_sede_vigente  ON empleado_sede(id_empleado) WHERE fecha_fin IS NULL;

-- ============================================================================
-- 3. CONFIGURACION
-- ============================================================================

-- 3.1 HORARIO (RF-067 a RF-069)
-- [REV-09] Agregado nombre para facilitar administracion.
CREATE TABLE horario (
    id              SERIAL          PRIMARY KEY,
    id_sede         INTEGER         NOT NULL,
    nombre          VARCHAR(100),   -- [REV-09] Ej: "Horario Apertura", "Horario Fin de Semana"
    hora_entrada    TIME            NOT NULL,
    hora_salida     TIME,
    tolerancia_min  INTEGER         NOT NULL DEFAULT 15,
    vigente_desde   DATE            NOT NULL DEFAULT CURRENT_DATE,
    vigente_hasta   DATE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_horario_sede FOREIGN KEY (id_sede) REFERENCES sede(id),
    CONSTRAINT ck_horario_tolerancia CHECK (tolerancia_min >= 0 AND tolerancia_min <= 120),
    CONSTRAINT ck_horario_vigencia CHECK (vigente_hasta IS NULL OR vigente_hasta >= vigente_desde)
);
COMMENT ON TABLE horario IS 'Horarios por sede con historial (RF-067 a RF-069).';
COMMENT ON COLUMN horario.nombre IS '[REV-09] Nombre descriptivo: Horario Apertura, Horario Temporal, etc.';
CREATE INDEX idx_horario_sede_vigente ON horario(id_sede, vigente_desde, vigente_hasta);

-- 3.2 CALENDARIO_LABORAL (RF-070)
CREATE TABLE calendario_laboral (
    id          SERIAL          PRIMARY KEY,
    fecha       DATE            NOT NULL,
    tipo        VARCHAR(30)     NOT NULL,
    descripcion VARCHAR(255),
    anio        INTEGER         GENERATED ALWAYS AS (EXTRACT(YEAR FROM fecha)::INTEGER) STORED,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_calendario_fecha UNIQUE (fecha),
    CONSTRAINT ck_calendario_tipo CHECK (tipo IN ('FESTIVO', 'DOMINGO', 'CIERRE_EMPRESA'))
);
COMMENT ON TABLE calendario_laboral IS 'Calendario laboral Colombia (RF-070). Editable por Super Usuario.';
CREATE INDEX idx_calendario_fecha ON calendario_laboral(fecha);
CREATE INDEX idx_calendario_anio  ON calendario_laboral(anio);

-- [REV-08] 3.3 CONFIG_GENERAL (RF-085 a RF-090 + RF-066 personalizacion)
-- Personalizacion (logos/colores) se unifica aqui. Mismo concepto: clave-valor.
CREATE TABLE config_general (
    id          SERIAL          PRIMARY KEY,
    categoria   VARCHAR(30)     NOT NULL DEFAULT 'SISTEMA', -- SISTEMA, PERSONALIZACION
    clave       VARCHAR(50)     NOT NULL,
    valor       TEXT            NOT NULL,   -- TEXT para URLs de logos sin limite
    tipo_dato   VARCHAR(20)     NOT NULL DEFAULT 'STRING',
    descripcion VARCHAR(255),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_by  INTEGER,
    CONSTRAINT uq_config_clave UNIQUE (clave),
    CONSTRAINT fk_config_updated_by FOREIGN KEY (updated_by) REFERENCES usuario(id),
    CONSTRAINT ck_config_tipo CHECK (tipo_dato IN ('STRING', 'INTEGER', 'BOOLEAN')),
    CONSTRAINT ck_config_categoria CHECK (categoria IN ('SISTEMA', 'PERSONALIZACION'))
);
COMMENT ON TABLE config_general IS '[REV-08] Parametros globales + personalizacion visual unificados (RF-085 a RF-090, RF-066).';
COMMENT ON COLUMN config_general.categoria IS 'SISTEMA = parametros tecnicos. PERSONALIZACION = logos y colores.';

-- ============================================================================
-- 4. CONTROL DE ACCESO
-- ============================================================================

-- 4.1 MODULO
CREATE TABLE modulo (
    id          SERIAL          PRIMARY KEY,
    codigo      VARCHAR(50)     NOT NULL,
    nombre      VARCHAR(100)    NOT NULL,
    descripcion VARCHAR(255),
    CONSTRAINT uq_modulo_codigo UNIQUE (codigo)
);
COMMENT ON TABLE modulo IS 'Modulos del sistema para catalogo de permisos (RF-030).';

-- 4.2 PERMISO_ROL (RF-030, RF-031)
-- [REV-11] Agregado puede_administrar para operaciones avanzadas (roles, config).
CREATE TABLE permiso_rol (
    id              SERIAL          PRIMARY KEY,
    id_rol          INTEGER         NOT NULL,
    id_modulo       INTEGER         NOT NULL,
    puede_leer      BOOLEAN         NOT NULL DEFAULT FALSE,
    puede_escribir  BOOLEAN         NOT NULL DEFAULT FALSE,
    puede_eliminar  BOOLEAN         NOT NULL DEFAULT FALSE,
    puede_administrar BOOLEAN       NOT NULL DEFAULT FALSE,  -- [REV-11] Config avanzada, roles
    CONSTRAINT fk_permiso_rol    FOREIGN KEY (id_rol)    REFERENCES cat_rol(id) ON DELETE CASCADE,
    CONSTRAINT fk_permiso_modulo FOREIGN KEY (id_modulo) REFERENCES modulo(id)  ON DELETE CASCADE,
    CONSTRAINT uq_permiso_rol_modulo UNIQUE (id_rol, id_modulo)
);
COMMENT ON TABLE permiso_rol IS 'Permisos por rol y modulo (RF-030). Consultado en cada solicitud (RF-031).';
COMMENT ON COLUMN permiso_rol.puede_administrar IS '[REV-11] Para config avanzada: modificar roles, parametros globales, calendario.';
CREATE INDEX idx_permiso_rol ON permiso_rol(id_rol);

-- 4.3 SESION_USUARIO (RF-029, RF-030, RF-032)
-- [REV-06] Agregado refresh_token_hash para JWT moderno.
CREATE TABLE sesion_usuario (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_usuario          INTEGER         NOT NULL,
    token_hash          VARCHAR(255)    NOT NULL,
    refresh_token_hash  VARCHAR(255),   -- [REV-06] Para refresh token en flujo JWT
    ip_address          INET,
    user_agent          VARCHAR(500),
    activa              BOOLEAN         NOT NULL DEFAULT TRUE,
    fecha_login         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    fecha_expira        TIMESTAMPTZ     NOT NULL,
    fecha_logout        TIMESTAMPTZ,
    CONSTRAINT fk_sesion_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id)
);
COMMENT ON TABLE sesion_usuario IS 'Sesiones de usuarios administrativos (RF-029, RF-030, RF-032).';
COMMENT ON COLUMN sesion_usuario.refresh_token_hash IS '[REV-06] Hash del refresh token para rotacion JWT.';
CREATE INDEX idx_sesion_usuario   ON sesion_usuario(id_usuario, activa);
CREATE INDEX idx_sesion_token     ON sesion_usuario(token_hash) WHERE activa = TRUE;
CREATE INDEX idx_sesion_refresh   ON sesion_usuario(refresh_token_hash) WHERE activa = TRUE;
CREATE INDEX idx_sesion_expira    ON sesion_usuario(fecha_expira) WHERE activa = TRUE;

-- ============================================================================
-- 5. TABLAS DE OPERACION (ALTO VOLUMEN - BIGSERIAL)
-- ============================================================================

-- 5.1 TOKEN_QR (RF-001 a RF-007, RF-022)
-- [REV-03] consumido reemplazado por id_estado_token FK a cat_estado_token.
-- [REV-13] Agregado ip_generacion para auditoria.
-- [REV-16] Agregado id_dispositivo FK para trazabilidad sede->dispositivo->token.
CREATE TABLE token_qr (
    id                  BIGSERIAL       PRIMARY KEY,
    id_sede             INTEGER         NOT NULL,
    id_dispositivo      INTEGER         NOT NULL,   -- [REV-v3-02] NOT NULL: todo token lo genera un dispositivo
    id_estado_token     INTEGER         NOT NULL,   -- [REV-03] FK a cat_estado_token
    token               VARCHAR(255)    NOT NULL,
    codigo_alfa         VARCHAR(20)     NOT NULL,
    generado_en         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    expira_en           TIMESTAMPTZ     NOT NULL,
    consumido_en        TIMESTAMPTZ,
    ip_generacion       INET,           -- [REV-13] IP del dispositivo que genero
    CONSTRAINT fk_token_sede        FOREIGN KEY (id_sede)         REFERENCES sede(id),
    CONSTRAINT fk_token_dispositivo FOREIGN KEY (id_dispositivo)  REFERENCES dispositivo(id),
    CONSTRAINT fk_token_estado      FOREIGN KEY (id_estado_token) REFERENCES cat_estado_token(id),
    CONSTRAINT uq_token             UNIQUE (token),
    CONSTRAINT ck_token_expiracion  CHECK (expira_en > generado_en)
);
COMMENT ON TABLE token_qr IS 'Tokens QR generados por el Sistema de Escritorio (RF-001 a RF-007).';
COMMENT ON COLUMN token_qr.id_estado_token IS '[REV-03] Estado del token: GENERADO, ACTIVO, EXPIRADO, CONSUMIDO. Extensible.';
COMMENT ON COLUMN token_qr.id_dispositivo IS '[REV-16] Dispositivo que genero el token. Trazabilidad: sede->dispositivo->token->asistencia.';
COMMENT ON COLUMN token_qr.ip_generacion IS '[REV-13] IP del equipo que genero el token. Util para auditoria e incidencias.';

CREATE INDEX idx_token_validacion    ON token_qr(token, id_estado_token, expira_en);
CREATE INDEX idx_token_sede_activo   ON token_qr(id_sede, id_estado_token, expira_en DESC);
CREATE INDEX idx_token_generado      ON token_qr(generado_en DESC);
CREATE INDEX idx_token_dispositivo   ON token_qr(id_dispositivo);

-- 5.2 ASISTENCIA (RF-021, RF-020, RF-060)
-- [REV-04] Eliminado codigo_ingresado (redundante con id_token que ya conoce el codigo).
-- [REV-15] Agregado created_by para registro manual futuro por administrador.
-- [REV-v3-01] Eliminados id_sede e id_dispositivo: redundantes.
-- La trazabilidad completa se resuelve via: asistencia -> token_qr -> dispositivo -> sede.
-- Guardar id_sede aqui generaria riesgo de inconsistencia (ej: token.sede=Medellin, asistencia.sede=Bogota).
CREATE TABLE asistencia (
    id                  BIGSERIAL       PRIMARY KEY,
    id_empleado         INTEGER         NOT NULL,
    id_tipo_registro    INTEGER         NOT NULL,
    id_token            BIGINT          NOT NULL,
    fecha_registro      DATE            NOT NULL DEFAULT CURRENT_DATE,
    hora_registro       TIME            NOT NULL DEFAULT CURRENT_TIME,
    timestamp_registro  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_by          INTEGER,        -- [REV-15] NULL=auto, FK a usuario si registro manual
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_asistencia_empleado    FOREIGN KEY (id_empleado)      REFERENCES empleado(id),
    CONSTRAINT fk_asistencia_tipo        FOREIGN KEY (id_tipo_registro) REFERENCES cat_tipo_registro(id),
    CONSTRAINT fk_asistencia_token       FOREIGN KEY (id_token)         REFERENCES token_qr(id),
    CONSTRAINT fk_asistencia_created_by  FOREIGN KEY (created_by)       REFERENCES usuario(id),
    CONSTRAINT uq_asistencia_empleado_dia UNIQUE (id_empleado, fecha_registro, id_tipo_registro)
);
COMMENT ON TABLE asistencia IS 'Registros de asistencia (RF-021). Sede y dispositivo se obtienen via JOIN a token_qr -> dispositivo -> sede.';
COMMENT ON COLUMN asistencia.id_token IS 'Cadena de trazabilidad: asistencia -> token_qr -> dispositivo -> sede. No se duplican FK.';
COMMENT ON COLUMN asistencia.created_by IS '[REV-15] NULL = registro automatico por QR. FK a usuario si un admin registra manualmente.';

CREATE INDEX idx_asistencia_empleado  ON asistencia(id_empleado, fecha_registro DESC);
CREATE INDEX idx_asistencia_fecha     ON asistencia(fecha_registro DESC);
CREATE INDEX idx_asistencia_tipo      ON asistencia(id_tipo_registro);
CREATE INDEX idx_asistencia_timestamp ON asistencia(timestamp_registro DESC);
CREATE INDEX idx_asistencia_token     ON asistencia(id_token);

-- 5.3 NOVEDAD (RF-054, RF-055, RF-072)
-- [REV-v3-01] Eliminado id_sede: para tardanzas se obtiene via asistencia->token->dispositivo->sede.
-- Para ausencias no hay sede (el empleado no registro).
CREATE TABLE novedad (
    id              BIGSERIAL       PRIMARY KEY,
    id_empleado     INTEGER         NOT NULL,
    id_tipo_novedad INTEGER         NOT NULL,
    id_asistencia   BIGINT,         -- NULL para ausencias (no hay registro)
    fecha           DATE            NOT NULL,
    observacion     VARCHAR(500),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_novedad_empleado FOREIGN KEY (id_empleado)     REFERENCES empleado(id),
    CONSTRAINT fk_novedad_tipo     FOREIGN KEY (id_tipo_novedad) REFERENCES cat_novedad(id),
    CONSTRAINT fk_novedad_asist    FOREIGN KEY (id_asistencia)   REFERENCES asistencia(id)
);
COMMENT ON TABLE novedad IS 'Novedades detectadas (RF-054, RF-055, RF-072). Sede se obtiene via asistencia->token chain.';
CREATE INDEX idx_novedad_empleado  ON novedad(id_empleado, fecha DESC);
CREATE INDEX idx_novedad_fecha     ON novedad(fecha DESC);
CREATE INDEX idx_novedad_tipo      ON novedad(id_tipo_novedad, fecha DESC);
CREATE INDEX idx_novedad_dashboard ON novedad(fecha, id_tipo_novedad);

-- ============================================================================
-- 6. AUDITORIA
-- [REV-10] Operaciones extendidas: LOGIN, LOGOUT, LOGIN_FALLIDO,
--          CAMBIO_CONTRASENA, CAMBIO_PERMISOS ademas de INSERT/UPDATE/DELETE.
-- ============================================================================

CREATE TABLE auditoria (
    id               BIGSERIAL       PRIMARY KEY,
    id_usuario       INTEGER,
    recurso          VARCHAR(100)    NOT NULL,
    id_recurso       VARCHAR(50),    -- NULL para LOGIN_FALLIDO (no hay recurso)
    operacion        VARCHAR(30)     NOT NULL,   -- [REV-10] Ampliado a 30 chars
    valor_anterior   JSONB,
    valor_nuevo      JSONB,
    ip_address       INET,
    detalle          VARCHAR(500),   -- [REV-10] Detalle adicional (ej: "Intento con usuario inexistente")
    timestamp_accion TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_auditoria_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id),
    CONSTRAINT ck_auditoria_operacion CHECK (operacion IN (
        'INSERT', 'UPDATE', 'DELETE',
        'LOGIN', 'LOGOUT', 'LOGIN_FALLIDO',
        'CAMBIO_CONTRASENA', 'CAMBIO_PERMISOS',
        'RESTABLECIMIENTO_PW'
    ))
);
COMMENT ON TABLE auditoria IS '[REV-10] Auditoria extendida: CRUD + acciones administrativas (login, logout, contrasena, permisos).';
COMMENT ON COLUMN auditoria.detalle IS '[REV-10] Contexto adicional para eventos de seguridad.';
COMMENT ON COLUMN auditoria.id_recurso IS 'NULL para LOGIN_FALLIDO donde no existe recurso identificado.';

CREATE INDEX idx_auditoria_recurso   ON auditoria(recurso, timestamp_accion DESC);
CREATE INDEX idx_auditoria_usuario   ON auditoria(id_usuario, timestamp_accion DESC);
CREATE INDEX idx_auditoria_timestamp ON auditoria(timestamp_accion DESC);
CREATE INDEX idx_auditoria_operacion ON auditoria(operacion, timestamp_accion DESC);

-- ============================================================================
-- 7. DATOS INICIALES (SEED)
-- ============================================================================

-- 7.1 Estados
INSERT INTO cat_estado (codigo, nombre, descripcion) VALUES
    ('ACTIVO',   'Activo',   'Registro habilitado y operativo'),
    ('INACTIVO', 'Inactivo', 'Registro deshabilitado, conserva historial');

-- 7.2 Roles
INSERT INTO cat_rol (codigo, nombre, id_estado, descripcion) VALUES
    ('SUPER_ADMIN', 'Super Usuario',  1, 'Acceso total al sistema.'),
    ('ADMIN',       'Administrador',  1, 'Acceso operativo.');

-- 7.3 Tipos de registro
INSERT INTO cat_tipo_registro (codigo, nombre, id_estado, descripcion) VALUES
    ('ENTRADA',  'Entrada',  1, 'Registro de entrada al punto de venta'),
    ('SALIDA',   'Salida',   1, 'Registro de salida del punto de venta'),
    ('ALMUERZO', 'Almuerzo', 1, 'Registro de salida/entrada a almuerzo'),
    ('DESCANSO', 'Descanso', 1, 'Registro de descanso');

-- 7.4 Novedades
INSERT INTO cat_novedad (codigo, nombre, id_estado, color, icono, descripcion) VALUES
    ('TARDANZA', 'Tardanza', 1, '#FF9800', 'clock-alert',    'Registro despues del horario + tolerancia'),
    ('AUSENCIA', 'Ausencia', 1, '#F44336', 'account-remove', 'Empleado activo sin registro en dia habil');

-- [REV-03] 7.5 Estados de token
INSERT INTO cat_estado_token (codigo, nombre, descripcion) VALUES
    ('GENERADO', 'Generado', 'Token recien creado, pendiente de activacion'),
    ('ACTIVO',   'Activo',   'Token visible en pantalla, disponible para uso'),
    ('EXPIRADO', 'Expirado', 'Token cuyo tiempo de vigencia finalizo sin ser usado'),
    ('CONSUMIDO','Consumido','Token utilizado para un registro de asistencia');

-- 7.6 Modulos del sistema
INSERT INTO modulo (codigo, nombre, descripcion) VALUES
    ('DASHBOARD',     'Dashboard',                'Panel principal con indicadores'),
    ('USUARIOS',      'Gestion de Usuarios',      'CRUD de usuarios administrativos'),
    ('ROLES',         'Gestion de Roles',         'Administracion de CAT_ROL'),
    ('CATALOGOS',     'Catalogos del Sistema',    'CAT_ESTADO, CAT_CARGO, CAT_TIPO_REGISTRO, CAT_NOVEDAD'),
    ('EMPLEADOS',     'Gestion de Empleados',     'CRUD de empleados'),
    ('CARGOS',        'Gestion de Cargos',        'CRUD de cargos'),
    ('SEDES',         'Gestion de Sedes',         'CRUD de sedes'),
    ('DISPOSITIVOS',  'Gestion de Dispositivos',  'CRUD de dispositivos autorizados'),
    ('HORARIOS',      'Config. de Horarios',      'Horarios por sede y tolerancia'),
    ('REPORTES',      'Reportes y Exportacion',   'Consulta y descarga de reportes'),
    ('AUDITORIA',     'Auditoria',                'Consulta del log de auditoria'),
    ('CONFIGURACION', 'Configuracion General',    'Parametros globales del sistema'),
    ('CALENDARIO',    'Calendario Laboral',       'Festivos y dias no laborales');

-- 7.7 Permisos (Super Usuario: todo con administrar)
INSERT INTO permiso_rol (id_rol, id_modulo, puede_leer, puede_escribir, puede_eliminar, puede_administrar)
SELECT 1, id, TRUE, TRUE, TRUE, TRUE FROM modulo;

-- Administrador: operativo sin admin avanzado
INSERT INTO permiso_rol (id_rol, id_modulo, puede_leer, puede_escribir, puede_eliminar, puede_administrar)
SELECT 2, id, TRUE, TRUE, TRUE, FALSE FROM modulo
WHERE codigo IN ('DASHBOARD', 'EMPLEADOS', 'CARGOS', 'SEDES', 'DISPOSITIVOS', 'HORARIOS', 'REPORTES');

-- 7.8 Parametros iniciales (RF-085 a RF-090) + Personalizacion (RF-066)
INSERT INTO config_general (categoria, clave, valor, tipo_dato, descripcion) VALUES
    ('SISTEMA', 'QR_EXPIRACION_SEG',  '30',             'INTEGER', 'Vigencia del QR en segundos (RF-085)'),
    ('SISTEMA', 'CODIGO_LONGITUD',    '6',              'INTEGER', 'Caracteres del codigo alfanumerico (RF-086)'),
    ('SISTEMA', 'CODIGO_FORMATO',     'ALFANUMERICO',   'STRING',  'Formato del codigo: NUMERICO, ALFABETICO, ALFANUMERICO (RF-087)'),
    ('SISTEMA', 'SESION_TIMEOUT_MIN', '15',             'INTEGER', 'Inactividad para cierre automatico (RF-088)'),
    ('SISTEMA', 'ZONA_HORARIA',       'America/Bogota', 'STRING',  'Zona horaria del sistema (RF-089)'),
    ('SISTEMA', 'FORMATO_FECHA',      'DD/MM/AAAA',     'STRING',  'Formato de fechas (RF-090)'),
    ('PERSONALIZACION', 'LOGO_PRINCIPAL',  '', 'STRING', 'URL del logo principal de Familia Pues'),
    ('PERSONALIZACION', 'COLOR_PRIMARIO',  '', 'STRING', 'Color primario corporativo (hex)'),
    ('PERSONALIZACION', 'COLOR_SECUNDARIO','', 'STRING', 'Color secundario corporativo (hex)');

-- 7.9 Calendario laboral Colombia 2026
INSERT INTO calendario_laboral (fecha, tipo, descripcion) VALUES
    ('2026-01-01', 'FESTIVO', 'Ano Nuevo'),
    ('2026-01-12', 'FESTIVO', 'Dia de los Reyes Magos'),
    ('2026-03-23', 'FESTIVO', 'Dia de San Jose'),
    ('2026-04-02', 'FESTIVO', 'Jueves Santo'),
    ('2026-04-03', 'FESTIVO', 'Viernes Santo'),
    ('2026-05-01', 'FESTIVO', 'Dia del Trabajo'),
    ('2026-05-18', 'FESTIVO', 'Ascension del Senor'),
    ('2026-06-08', 'FESTIVO', 'Corpus Christi'),
    ('2026-06-15', 'FESTIVO', 'Sagrado Corazon de Jesus'),
    ('2026-06-29', 'FESTIVO', 'San Pedro y San Pablo'),
    ('2026-07-20', 'FESTIVO', 'Dia de la Independencia'),
    ('2026-08-07', 'FESTIVO', 'Batalla de Boyaca'),
    ('2026-08-17', 'FESTIVO', 'Asuncion de la Virgen'),
    ('2026-10-12', 'FESTIVO', 'Dia de la Raza'),
    ('2026-11-02', 'FESTIVO', 'Todos los Santos'),
    ('2026-11-16', 'FESTIVO', 'Independencia de Cartagena'),
    ('2026-12-08', 'FESTIVO', 'Inmaculada Concepcion'),
    ('2026-12-25', 'FESTIVO', 'Navidad');

INSERT INTO calendario_laboral (fecha, tipo, descripcion)
SELECT d::DATE, 'DOMINGO', 'Domingo'
FROM generate_series('2026-01-04'::DATE, '2026-12-27'::DATE, '7 days'::INTERVAL) AS d
WHERE EXTRACT(DOW FROM d) = 0
ON CONFLICT (fecha) DO NOTHING;