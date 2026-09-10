-- Agrega la columna id_sede a la tabla asistencia.
-- El modelo ORM la define pero faltaba en el esquema de base de datos.
ALTER TABLE asistencia
  ADD COLUMN IF NOT EXISTS id_sede integer
    REFERENCES sede(id) ON UPDATE CASCADE ON DELETE RESTRICT;

-- Si no hay filas, se puede aplicar NOT NULL directamente.
-- Si hay filas existentes, primero se deben poblar con la sede del token_qr.
DO $$
BEGIN
  IF (SELECT count(*) FROM asistencia WHERE id_sede IS NULL) = 0 THEN
    ALTER TABLE asistencia ALTER COLUMN id_sede SET NOT NULL;
  END IF;
END $$;
