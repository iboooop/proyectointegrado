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

# Activar el entorno virtual en GitBash
```bash
   source venv/Scripts/activate
```

# Si PowerShell bloquea la ejecución de scripts, habilita la política temporalmente:
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
