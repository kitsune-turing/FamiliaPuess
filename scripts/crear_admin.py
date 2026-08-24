"""
Crea el primer usuario administrador del sistema.

La base de datos se instala sin ningún usuario, de modo que nadie podría
iniciar sesión por primera vez. Este script cubre ese arranque en frío.

No se incluye un INSERT con contraseña en `database.sql` a propósito: ese
archivo se versiona en Git y una credencial ahí quedaría expuesta a todo el
equipo y a cualquiera que clone el repositorio.

Uso:
    python -m scripts.crear_admin

    # o de forma no interactiva (útil en CI):
    python -m scripts.crear_admin --username admin --correo admin@familiapuess.com \\
        --nombre "Admin General" --password "..."

El usuario se crea con `debe_cambiar_pw = TRUE`, así que la API obligará a
cambiar la contraseña en el primer inicio de sesión.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from apps.API.core.config import get_settings
from apps.API.security.password import hash_password

LONGITUD_MINIMA = 12


def _parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crea el primer usuario administrador.")
    parser.add_argument("--username", help="Nombre de usuario para iniciar sesión.")
    parser.add_argument("--correo", help="Correo electrónico del administrador.")
    parser.add_argument("--nombre", help="Nombre completo mostrado en el panel.")
    parser.add_argument("--password", help="Contraseña. Si se omite, se pide por consola.")
    return parser.parse_args()


def _pedir(valor: str | None, etiqueta: str, defecto: str) -> str:
    if valor:
        return valor
    respuesta = input(f"{etiqueta} [{defecto}]: ").strip()
    return respuesta or defecto


def _pedir_password(valor: str | None) -> str:
    if valor:
        return valor
    while True:
        clave = getpass.getpass("Contraseña: ")
        if len(clave) < LONGITUD_MINIMA:
            print(f"  La contraseña debe tener al menos {LONGITUD_MINIMA} caracteres.")
            continue
        if clave != getpass.getpass("Repite la contraseña: "):
            print("  Las contraseñas no coinciden.")
            continue
        return clave


async def crear_admin(username: str, correo: str, nombre: str, password: str) -> None:
    engine = create_async_engine(get_settings().database_url)

    try:
        async with engine.begin() as conexion:
            existentes = await conexion.scalar(text("SELECT COUNT(*) FROM usuario"))
            if existentes:
                print(
                    f"La tabla `usuario` ya tiene {existentes} registro(s). "
                    "Este script solo se usa para el arranque inicial.",
                )
                sys.exit(1)

            rol_id = await conexion.scalar(
                text("SELECT id FROM cat_rol WHERE codigo = 'SUPER_ADMIN'")
            )
            estado_id = await conexion.scalar(
                text("SELECT id FROM cat_estado WHERE codigo = 'ACTIVO'")
            )
            if rol_id is None or estado_id is None:
                print(
                    "No se encontraron los catálogos base. "
                    "Ejecuta primero `apps/API/database/database.sql`.",
                )
                sys.exit(1)

            await conexion.execute(
                text(
                    """
                    INSERT INTO usuario
                        (id_rol, id_estado, nombre, correo, username,
                         password_hash, debe_cambiar_pw)
                    VALUES
                        (:rol, :estado, :nombre, :correo, :username, :hash, TRUE)
                    """
                ),
                {
                    "rol": rol_id,
                    "estado": estado_id,
                    "nombre": nombre,
                    "correo": correo,
                    "username": username,
                    "hash": hash_password(password),
                },
            )
    finally:
        await engine.dispose()

    print(f"\nUsuario «{username}» creado con rol SUPER_ADMIN.")
    print("La API pedirá cambiar la contraseña en el primer inicio de sesión.")


def main() -> None:
    args = _parsear_argumentos()
    username = _pedir(args.username, "Usuario", "admin")
    correo = _pedir(args.correo, "Correo", "admin@familiapuess.com")
    nombre = _pedir(args.nombre, "Nombre completo", "Admin General")
    password = _pedir_password(args.password)
    asyncio.run(crear_admin(username, correo, nombre, password))


if __name__ == "__main__":
    main()
