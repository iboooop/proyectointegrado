#!/usr/bin/env python3
"""
create_database.py

Pequeño script para crear una base de datos MySQL vacía llamada "sistema_erp".

Soporta parámetros por línea de comandos y variables de entorno:
  - DB_HOST / MYSQL_HOST, DB_PORT / MYSQL_PORT, DB_USER / MYSQL_USER, DB_PASSWORD / MYSQL_PASSWORD, DB_NAME / MYSQL_DATABASE

Si está disponible DJANGO_SETTINGS_MODULE y el módulo de settings se puede importar,
se intentará leer DATABASES['default'] para obtener valores por defecto.
Por seguridad no sobrescribe una base de datos existente a menos que se use --force.
"""
from __future__ import annotations

import os
import argparse
import sys
import importlib
from pathlib import Path

DB_DRIVER = None
DB_MODULE = None
DB_ERROR = Exception
errorcode = None

# Intentar cargar .env si existe (usa python-dotenv si está instalado)
try:
    from dotenv import load_dotenv  # type: ignore

    script_dir = Path(__file__).resolve().parent
    candidates = [script_dir / ".env", script_dir.parent / ".env"]
    for c in candidates:
        if c.exists():
            load_dotenv(dotenv_path=str(c))
            print(f"Cargado .env desde: {c}")
            break
except Exception:
    pass


def _discover_django_db_settings() -> dict:
    """Si DJANGO_SETTINGS_MODULE está disponible, intenta importar el módulo y devolver DATABASES['default']."""
    dj_module = os.getenv("DJANGO_SETTINGS_MODULE")
    if not dj_module:
        return {}
    try:
        settings_mod = importlib.import_module(dj_module)
        db = getattr(settings_mod, "DATABASES", {}).get("default", {}) or {}
        # convertir claves comunes a nombres de entorno usados aquí
        return {
            "NAME": db.get("NAME"),
            "USER": db.get("USER"),
            "PASSWORD": db.get("PASSWORD"),
            "HOST": db.get("HOST"),
            "PORT": db.get("PORT"),
        }
    except Exception:
        return {}


# Intentar usar mysqlclient (MySQLdb) primero — es lo que tienes en requirements.txt
try:
    import MySQLdb as _mysqldb  # type: ignore

    DB_DRIVER = "mysqldb"
    DB_MODULE = _mysqldb
    DB_ERROR = _mysqldb.Error  # type: ignore
except Exception:
    try:
        import mysql.connector as _mysql_connector  # type: ignore
        from mysql.connector import errorcode as _errorcode  # type: ignore

        DB_DRIVER = "mysql-connector"
        DB_MODULE = _mysql_connector
        DB_ERROR = _mysql_connector.Error  # type: ignore
        errorcode = _errorcode
    except Exception:
        print(
            "Error: no se pudo importar 'MySQLdb' ni 'mysql.connector'. "
            "Instala 'mysqlclient' o 'mysql-connector-python'."
        )
        raise

DEFAULT_DB_NAME = "sistema_erp"


def _env_prefixed(*names):
    """Devuelve el primer valor de entorno encontrado entre los nombres dados."""
    for n in names:
        v = os.getenv(n)
        if v is not None and v != "":
            return v
    return None


def create_database(host: str, port: int, user: str, password: str, db_name: str, force: bool = False) -> bool:
    """Crea la base de datos db_name en el servidor MySQL indicado."""
    conn = None
    try:
        if DB_DRIVER == "mysqldb":
            conn = DB_MODULE.connect(host=host, port=port, user=user, passwd=password)
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES LIKE '%s'" % (db_name,))
            exists = cursor.fetchone() is not None
        else:
            conn = DB_MODULE.connect(host=host, port=port, user=user, password=password)
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
            exists = cursor.fetchone() is not None

        if exists and not force:
            print(f"La base de datos '{db_name}' ya existe. Use --force para eliminarla y recrearla.")
            return False

        if exists and force:
            cursor.execute(f"DROP DATABASE `{db_name}`")
            print(f"Base de datos '{db_name}' eliminada (force).")

        cursor.execute(
            f"CREATE DATABASE `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
        )
        print(f"Base de datos '{db_name}' creada correctamente.")
        return True

    finally:
        try:
            if conn is not None:
                conn.close()
        except Exception:
            pass


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crear base de datos MySQL vacía para el proyecto (sistema_erp)")

    # Defaults: primero variables DB_/MYSQL_, luego settings Django si existe, luego valores fijos.
    dj_db = _discover_django_db_settings()

    default_host = _env_prefixed("DB_HOST", "MYSQL_HOST", "MYSQL_HOSTNAME") or dj_db.get("HOST") or "127.0.0.1"
    default_port = int(_env_prefixed("DB_PORT", "MYSQL_PORT") or (dj_db.get("PORT") or os.getenv("PORT", "3306")))
    default_user = _env_prefixed("DB_USER", "MYSQL_USER") or dj_db.get("USER") or "root"
    default_password = _env_prefixed("DB_PASSWORD", "MYSQL_PASSWORD") or dj_db.get("PASSWORD") or ""
    default_db_name = _env_prefixed("DB_NAME", "MYSQL_DATABASE", "MYSQL_DB") or dj_db.get("NAME") or DEFAULT_DB_NAME

    parser.add_argument("--host", default=default_host, help="Host de MySQL (env DB_HOST / MYSQL_HOST)")
    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
        help="Puerto de MySQL (env DB_PORT / MYSQL_PORT)",
    )
    parser.add_argument("--user", default=default_user, help="Usuario de MySQL (env DB_USER / MYSQL_USER)")
    parser.add_argument(
        "--password", default=default_password, help="Password de MySQL (env DB_PASSWORD / MYSQL_PASSWORD)"
    )
    parser.add_argument("--db-name", default=default_db_name, help="Nombre de la base de datos a crear (env DB_NAME)")
    parser.add_argument("--force", action="store_true", help="Si está presente, eliminar y recrear la base de datos si ya existe")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    print(f"Usando driver: {DB_DRIVER}")
    print(f"Conexión: {args.user}@{args.host}:{args.port} -> base de datos objetivo: {args.db_name}")

    try:
        ok = create_database(args.host, args.port, args.user, args.password, args.db_name, force=args.force)
        return 0 if ok else 2
    except DB_ERROR as e:
        if DB_DRIVER == "mysql-connector" and errorcode and getattr(e, "errno", None) == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error de autenticación: credenciales incorrectas o sin permisos para crear bases de datos.")
        else:
            print("Ocurrió un error al conectar/ejecutar en MySQL:", e)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
