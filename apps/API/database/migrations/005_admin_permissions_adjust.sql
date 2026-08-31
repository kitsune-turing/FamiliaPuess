-- Adjust Administrador (id=2) permissions:
-- - Add AUDITORIA (read-only) and ROLES (read-only)
-- - Ensure NO access to CATALOGOS, CONFIGURACION, CALENDARIO, NOVEDADES

-- Grant read-only AUDITORIA
INSERT INTO permiso_rol (id_rol, id_modulo, puede_leer, puede_escribir, puede_eliminar, puede_administrar)
SELECT 2, id, TRUE, FALSE, FALSE, FALSE
FROM modulo WHERE codigo = 'AUDITORIA'
ON CONFLICT (id_rol, id_modulo) DO UPDATE
  SET puede_leer = TRUE, puede_escribir = FALSE, puede_eliminar = FALSE;

-- Grant read-only ROLES
INSERT INTO permiso_rol (id_rol, id_modulo, puede_leer, puede_escribir, puede_eliminar, puede_administrar)
SELECT 2, id, TRUE, FALSE, FALSE, FALSE
FROM modulo WHERE codigo = 'ROLES'
ON CONFLICT (id_rol, id_modulo) DO UPDATE
  SET puede_leer = TRUE, puede_escribir = FALSE, puede_eliminar = FALSE;

-- Remove CATALOGOS access from admin
DELETE FROM permiso_rol
WHERE id_rol = 2
  AND id_modulo = (SELECT id FROM modulo WHERE codigo = 'CATALOGOS');

-- Remove CONFIGURACION access from admin
DELETE FROM permiso_rol
WHERE id_rol = 2
  AND id_modulo = (SELECT id FROM modulo WHERE codigo = 'CONFIGURACION');

-- Remove CALENDARIO access from admin
DELETE FROM permiso_rol
WHERE id_rol = 2
  AND id_modulo = (SELECT id FROM modulo WHERE codigo = 'CALENDARIO');

-- Remove NOVEDADES access from admin
DELETE FROM permiso_rol
WHERE id_rol = 2
  AND id_modulo = (SELECT id FROM modulo WHERE codigo = 'NOVEDADES');
