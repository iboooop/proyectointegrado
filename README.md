# 🧩 SISTEMA ERP - PROYECTO INTEGRADO

Motor de Base de Datos: Este proyecto utiliza MySQL como motor principal.
Asegúrate de tener MySQL activo (por ejemplo, con WampServer o XAMPP) y una base de datos creada con el nombre: sistema_erp

# 1️⃣ Crear y activar el entorno virtual
Crear el entorno virtual (solo la primera vez)
```bash
   python -m venv venv
```

En Git Bash (Windows) *usa la ruta Scripts* del venv:
Ejecuta desde la raíz del proyecto (Git Bash)
```bash
source venv/Scripts/activate
```
Si PowerShell bloquea la ejecución de scripts, habilita la política temporalmente (ejecutar en PowerShell):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process


# 2️⃣ Actualizar pip y herramientas básicas
```bash
   pip install --upgrade pip setuptools wheel
   ```

```bash
   pip install pyotp
   ```


# 3️⃣ Instalar dependencias del proyecto
```bash
   pip install -r requirements.txt
   ```

# 4️⃣ Creae Base de Datos MySQL
```bash
   cd sistema_erp
   ```
```bash
   python create_db.py --force
   ```
# 5️⃣ Aplicar migraciones y crear superusuario
```bash
   python manage.py makemigrations
   ```
```bash
   python manage.py migrate
   ```
```bash
   #Opcional, vamos a cargar usuarios en seed
   python manage.py createsuperuser
   ```


# 6️⃣ Cargar datos iniciales
```bash
   python manage.py seed_sistema_erp
```


# 7️⃣ Ejecutar el servidor de desarrollo
```bash
   python manage.py runserver
```


# Acceso al panel de administración de Django

Abre en tu navegador: http://127.0.0.1:8000/admin/

# Acceso al panel de administración de MYSQL

http://localhost/phpmyadmin/
usuario: root


🚀 ¡Listo! Tu entorno de desarrollo está configurado y funcionando.


# Usuarios creados por el seed

Credenciales por defecto que genera el seed:
- admin / admin123
- compras / compras123
- bodega / bodega123
