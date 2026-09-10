-- 009: Empleados ya no pertenecen a una sede fija.
-- La sede se determina por el dispositivo donde registran asistencia.
ALTER TABLE empleado ALTER COLUMN id_sede_actual DROP NOT NULL;
UPDATE empleado SET id_sede_actual = NULL;
