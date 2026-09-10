-- Grant USUARIOS permissions to the Administrador role (id=2).
-- Previously only SUPER_ADMIN could manage users; this allows admin too.
INSERT INTO permiso_rol (id_rol, id_modulo, puede_leer, puede_escribir, puede_eliminar, puede_administrar)
SELECT 2, id, TRUE, TRUE, FALSE, FALSE
FROM modulo
WHERE codigo = 'USUARIOS'
ON CONFLICT (id_rol, id_modulo) DO UPDATE
  SET puede_leer = TRUE, puede_escribir = TRUE;
