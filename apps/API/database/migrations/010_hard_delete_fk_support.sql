-- Adjust FK constraints to support hard-delete for usuarios, roles, sedes, dispositivos.

-- sesion_usuario: cascade delete when usuario is deleted
ALTER TABLE sesion_usuario DROP CONSTRAINT IF EXISTS fk_sesion_usuario;
ALTER TABLE sesion_usuario
    ADD CONSTRAINT fk_sesion_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuario(id) ON DELETE CASCADE;

-- auditoria: set null when usuario is deleted (keep audit trail)
ALTER TABLE auditoria DROP CONSTRAINT IF EXISTS fk_auditoria_usuario;
ALTER TABLE auditoria
    ADD CONSTRAINT fk_auditoria_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuario(id) ON DELETE SET NULL;

-- asistencia.created_by: set null on delete (already nullable)
ALTER TABLE asistencia DROP CONSTRAINT IF EXISTS fk_asistencia_created_by;
ALTER TABLE asistencia
    ADD CONSTRAINT fk_asistencia_created_by FOREIGN KEY (created_by)
    REFERENCES usuario(id) ON DELETE SET NULL;

-- configuracion.updated_by: set null on delete
ALTER TABLE configuracion DROP CONSTRAINT IF EXISTS fk_config_updated_by;
ALTER TABLE configuracion
    ADD CONSTRAINT fk_config_updated_by FOREIGN KEY (updated_by)
    REFERENCES usuario(id) ON DELETE SET NULL;

-- dispositivo.id_sede: set null when sede is deleted (already nullable)
ALTER TABLE dispositivo DROP CONSTRAINT IF EXISTS fk_dispositivo_sede;
ALTER TABLE dispositivo
    ADD CONSTRAINT fk_dispositivo_sede FOREIGN KEY (id_sede)
    REFERENCES sede(id) ON DELETE SET NULL;

-- empleado_sede: cascade delete when sede is deleted
ALTER TABLE empleado_sede DROP CONSTRAINT IF EXISTS fk_emp_sede_sede;
ALTER TABLE empleado_sede
    ADD CONSTRAINT fk_emp_sede_sede FOREIGN KEY (id_sede)
    REFERENCES sede(id) ON DELETE CASCADE;

-- horario: cascade delete when sede is deleted
ALTER TABLE horario DROP CONSTRAINT IF EXISTS fk_horario_sede;
ALTER TABLE horario
    ADD CONSTRAINT fk_horario_sede FOREIGN KEY (id_sede)
    REFERENCES sede(id) ON DELETE CASCADE;

-- token_qr.id_sede: make nullable and set null on delete
ALTER TABLE token_qr ALTER COLUMN id_sede DROP NOT NULL;
ALTER TABLE token_qr DROP CONSTRAINT IF EXISTS fk_token_sede;
ALTER TABLE token_qr
    ADD CONSTRAINT fk_token_sede FOREIGN KEY (id_sede)
    REFERENCES sede(id) ON DELETE SET NULL;

-- token_qr.id_dispositivo: make nullable and set null on delete
ALTER TABLE token_qr ALTER COLUMN id_dispositivo DROP NOT NULL;
ALTER TABLE token_qr DROP CONSTRAINT IF EXISTS fk_token_dispositivo;
ALTER TABLE token_qr
    ADD CONSTRAINT fk_token_dispositivo FOREIGN KEY (id_dispositivo)
    REFERENCES dispositivo(id) ON DELETE SET NULL;

-- asistencia.id_sede: make nullable and set null on delete
ALTER TABLE asistencia ALTER COLUMN id_sede DROP NOT NULL;
ALTER TABLE asistencia DROP CONSTRAINT IF EXISTS fk_asistencia_sede;
-- Also try dropping the auto-generated name from migration 008
DO $$
BEGIN
    ALTER TABLE asistencia DROP CONSTRAINT IF EXISTS asistencia_id_sede_fkey;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;
ALTER TABLE asistencia
    ADD CONSTRAINT fk_asistencia_sede FOREIGN KEY (id_sede)
    REFERENCES sede(id) ON DELETE SET NULL;
