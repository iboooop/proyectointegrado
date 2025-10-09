# SISTEMA ERP - PROYECTO INTEGRADO

Motor de Base de Datos 
Este proyecto utiliza **SQLite** como base de datos por defecto. No requiere configuración adicional.

## Cómo correr el proyecto:
1. Aplicar migraciones:  
   ```bash
   python manage.py makemigrations
   python manage.py migrate

## Cargar datos iniciales (semillas) con: 
```bash
python manage.py seed_sistema_erp
```
Esto crea datos de prueba y genera archivos JSON en la carpeta fixtures/.

## Los datos pueden cargarse posteriormente con:
```bash
python manage.py loaddata fixtures/<archivo>.json
```
## Crear superusuario si es necesario para acceder al admin.

Credenciales de prueba del superusuario:

Usuario: tais

Contraseña: abcd123#

## Acceso al admin de Django:

http://127.0.0.1:8000/admin/
