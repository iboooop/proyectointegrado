#!/usr/bin/env python3
"""
create_database.py

Pequeño script para crear una base de datos MySQL vacía llamada "sistema_erp".

Soporta parámetros por línea de comandos y variables de entorno:
  - MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD

Por seguridad no sobrescribe una base de datos existente a menos que se use --force.
"""
from __future__ import annotations

import os
import argparse
import sys

DB_DRIVER = None
DB_MODULE = None
DB_ERROR = Exception

# Intentar usar mysqlclient (MySQLdb) primero — es lo que tienes en requirements.txt
try:
    import MySQLdb as _mysqldb
    import MySQLdb.cursors as _mysqldb_cursors
    DB_DRIVER = 'mysqldb'
    DB_MODULE = _mysqldb
    DB_ERROR = _mysqldb.Error
except Exception:
    # Caer a mysql-connector-python
    try:
        import mysql.connector as _mysql_connector
        from mysql.connector import errorcode as _errorcode
        DB_DRIVER = 'mysql-connector'
        DB_MODULE = _mysql_connector
        DB_ERROR = _mysql_connector.Error
        # Exponer errorcode para mensajes de ayuda
        errorcode = _errorcode
    except Exception:
        print("Error: no se pudo importar 'MySQLdb' ni 'mysql.connector'. Instala 'mysqlclient' o 'mysql-connector-python'.")
        raise


DEFAULT_DB_NAME = "sistema_erp"


def create_database(host: str, port: int, user: str, password: str, db_name: str, force: bool = False) -> bool:
    """Crea la base de datos db_name en el servidor MySQL indicado.

    Retorna True si la base de datos fue creada (o recreada). Retorna False si ya existía y no se usó --force.
    Lanza mysql.connector.Error en caso de problemas de conexión o permisos.
    """
    conn = None
    try:
        if DB_DRIVER == 'mysqldb':
            # mysqlclient / MySQLdb: connect uses 'passwd' for password and 'cursorclass' optional
            conn = DB_MODULE.connect(host=host, port=port, user=user, passwd=password)
            cursor = conn.cursor()
            # MySQLdb doesn't support parameter substitution in SHOW DATABASES LIKE %s reliably across versions,
            # so usamos formateo seguro para este caso controlado (db_name proviene de args/env del usuario)
            cursor.execute("SHOW DATABASES LIKE '%s'" % (db_name,))
            exists = cursor.fetchone() is not None
        else:
            # mysql-connector-python
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

        cursor.execute(f"CREATE DATABASE `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
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
    parser.add_argument("--host", default=os.getenv("MYSQL_HOST", "127.0.0.1"), help="Host de MySQL (env MYSQL_HOST)")
    parser.add_argument("--port", type=int, default=int(os.getenv("MYSQL_PORT", "3306")), help="Puerto de MySQL (env MYSQL_PORT)")
    parser.add_argument("--user", default=os.getenv("MYSQL_USER", "root"), help="Usuario de MySQL (env MYSQL_USER)")
    parser.add_argument("--password", default=os.getenv("MYSQL_PASSWORD", ""), help="Password de MySQL (env MYSQL_PASSWORD)")
    parser.add_argument("--db-name", default=os.getenv("MYSQL_DATABASE", DEFAULT_DB_NAME), help="Nombre de la base de datos a crear")
    parser.add_argument("--force", action="store_true", help="Si está presente, eliminar y recrear la base de datos si ya existe")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        ok = create_database(args.host, args.port, args.user, args.password, args.db_name, force=args.force)
        return 0 if ok else 2
    except DB_ERROR as e:
        # Mostrar información útil al usuario
        if DB_DRIVER == 'mysql-connector' and getattr(e, 'errno', None) == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error de autenticación: credenciales incorrectas o sin permisos para crear bases de datos.")
        else:
            print("Ocurrió un error al conectar/ejecutar en MySQL:", e)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
