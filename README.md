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
python -m venv venv

# Activar el entorno virtual en PowerShell
.\venv\Scripts\Activate.ps1

# Si PowerShell bloquea la ejecución de scripts, habilita la política temporalmente:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process


# ============================================================
# 2️⃣ Actualizar pip y herramientas básicas
# ============================================================
pip install --upgrade pip setuptools wheel


# ============================================================
# 3️⃣ Instalar dependencias del proyecto
# ============================================================
pip install -r requirements.txt


# ============================================================
# 4️⃣ Aplicar migraciones y crear superusuario
# ============================================================
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser


# ============================================================
# 5️⃣ (Opcional) Cargar datos iniciales
# ============================================================
python manage.py seed_sistema_erp


# ============================================================
# 6️⃣ Ejecutar el servidor de desarrollo
# ============================================================
python manage.py runserver


# ============================================================
# 7️⃣ Acceso al panel de administración de Django
# ============================================================
# Abre en tu navegador:
# http://127.0.0.1:8000/admin/
# ============================================================

# 🚀 ¡Listo! Tu entorno de desarrollo está configurado y funcionando.
