-- ============================================================
-- Script: Limpiar TODAS las tablas excepto configuración/catálogos
-- Base de datos: PostgreSQL (FamiliaPuess)
-- ============================================================
-- Tablas que se CONSERVAN (configuración y catálogos):
--   cat_cargo, cat_estado, cat_estado_token, cat_novedad,
--   cat_rol, cat_tipo_documento, cat_tipo_registro,
--   config_general, modulo, permiso_rol
-- ============================================================

BEGIN;

-- Desactivar triggers temporalmente para evitar conflictos de FK
SET session_replication_role = 'replica';

-- 1. Tablas sin dependencias entrantes (hojas)
TRUNCATE TABLE reporte_semanal    RESTART IDENTITY CASCADE;
TRUNCATE TABLE novedad            RESTART IDENTITY CASCADE;
TRUNCATE TABLE auditoria          RESTART IDENTITY CASCADE;
TRUNCATE TABLE asistencia         RESTART IDENTITY CASCADE;
TRUNCATE TABLE token_qr           RESTART IDENTITY CASCADE;
TRUNCATE TABLE sesion_usuario     RESTART IDENTITY CASCADE;
TRUNCATE TABLE calendario_laboral RESTART IDENTITY CASCADE;

-- 2. Tablas intermedias
TRUNCATE TABLE empleado_sede      RESTART IDENTITY CASCADE;
TRUNCATE TABLE horario            RESTART IDENTITY CASCADE;
TRUNCATE TABLE dispositivo        RESTART IDENTITY CASCADE;

-- 3. Tablas principales
TRUNCATE TABLE empleado           RESTART IDENTITY CASCADE;
TRUNCATE TABLE usuario            RESTART IDENTITY CASCADE;
TRUNCATE TABLE sede               RESTART IDENTITY CASCADE;

-- Reactivar triggers
SET session_replication_role = 'origin';

COMMIT;

-- Verificación rápida
SELECT tablename AS tabla, n_live_tup AS filas
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY tablename;
