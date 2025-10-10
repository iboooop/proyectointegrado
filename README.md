# ============================================================
# 🧩 SISTEMA ERP - PROYECTO INTEGRADO
# ============================================================

# Motor de Base de Datos:
# Este proyecto utiliza MySQL como motor principal.
# Asegúrate de tener MySQL activo (por ejemplo, con WampServer o XAMPP)
# y una base de datos creada con el nombre: sistema_erp
# ============================================================


# ============================================================
# 1️⃣ Crear y activar el entorno virtual
# ============================================================

# Crear el entorno virtual (solo la primera vez)
```bash
   python -m venv venv
```

# Activar el entorno virtual
# En Bash (WSL, macOS, Linux):
```bash
# Ejecuta desde la raíz del proyecto
source venv/bin/activate
```

# En Git Bash (Windows) *usa la ruta Scripts* del venv:
```bash
# Ejecuta desde la raíz del proyecto (Git Bash)
source venv/Scripts/activate
```

# Si PowerShell bloquea la ejecución de scripts, habilita la política temporalmente (ejecutar en PowerShell):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process


# ============================================================
# 2️⃣ Actualizar pip y herramientas básicas
# ============================================================
```bash
   pip install --upgrade pip setuptools wheel
   ```

# ============================================================
# 3️⃣ Instalar dependencias del proyecto
# ============================================================
```bash
   pip install -r requirements.txt
   ```

# ============================================================
# 4️⃣ Aplicar migraciones y crear superusuario
# ============================================================
```bash
   cd sistema_erp
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py makemigrations
```

# ============================================================
# 5️⃣ Cargar datos iniciales
# ============================================================
```bash
   python manage.py seed_sistema_erp
```

# ============================================================
# 6️⃣ Ejecutar el servidor de desarrollo
# ============================================================
```bash
   python manage.py runserver
```

# ============================================================
# 7️⃣ Acceso al panel de administración de Django
# ============================================================
# Abre en tu navegador:
# http://127.0.0.1:8000/admin/
# ============================================================

# 🚀 ¡Listo! Tu entorno de desarrollo está configurado y funcionando.

# ============================================================
# 8️⃣ Usuarios creados por el seed
# ============================================================
# El comando `python manage.py seed_sistema_erp` crea 3 usuarios de prueba.
# Credenciales por defecto que genera el seed:
# - admin / admin123  -> is_staff=True, is_superuser=True
# - compras / compras123 -> is_staff=True, is_superuser=False
# - bodega / bodega123 -> is_staff=True, is_superuser=False
#
# Nota: si ya existen usuarios con esos usernames el seed hace `get_or_create` y
# actualizará sus grupos/flags según la lógica del script. Para (re)crear/actualizar
# ejecuta:
```bash
python manage.py seed_sistema_erp
```

# Después puedes entrar al admin con cualquiera de los usuarios `is_staff` o con
# `admin` para revisar/grabar permisos.
