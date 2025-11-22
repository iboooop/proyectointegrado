import os
from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages

# ===========================
# BASE DIR & ENV
# ===========================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ===========================
# SECURITY
# ===========================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-default')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")


# ===========================
# APPLICATIONS
# ===========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tus apps locales
    'transacciones',
    'productos',
    'proveedores',
    'usuarios',
    'autenticacion',
    'sistema_erp',
    'django_extensions',
    'bodegas',
    'clientes',
]

# ===========================
# MIDDLEWARE
# ===========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'sistema_erp.middleware.LoginRequiredMiddleware',
]

# ===========================
# URLS & WSGI
# ===========================
ROOT_URLCONF = 'sistema_erp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'sistema_erp' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema_erp.wsgi.application'

# ===========================
# DATABASES: MySQL local (WAMP/XAMPP)
# ===========================
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DB_NAME', 'sistema_erp'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# ===========================
# EJEMPLO DESACTIVADO: Conexión a AWS RDS (NO ACTIVO)
# ---------------------------------------------------
# Este bloque es SOLO de referencia para una base de datos MySQL en AWS RDS.
# No se ejecuta ni afecta al entorno local porque está completamente comentado.
# Para usarlo, copia y reemplaza el bloque DATABASES anterior y define
# las variables de entorno AWS_* en tu .env (ver .env.example).
#
# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('AWS_DB_ENGINE', 'django.db.backends.mysql'),
#         'NAME': os.getenv('AWS_DB_NAME', 'sistema_erp_prod'),
#         'USER': os.getenv('AWS_DB_USER', ''),
#         'PASSWORD': os.getenv('AWS_DB_PASSWORD', ''),
#         'HOST': os.getenv('AWS_DB_HOST', 'xxxxx.rds.amazonaws.com'),
#         'PORT': os.getenv('AWS_DB_PORT', '3306'),
#         'OPTIONS': {
#             'charset': 'utf8mb4',
#         },
#     }
# }


# ===========================
# PASSWORD VALIDATION
# ===========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===========================
# INTERNATIONALIZATION
# ===========================
LANGUAGE_CODE = os.getenv("DJANGO_LANGUAGE_CODE", "es-cl")
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "America/Santiago")
USE_I18N = True
USE_TZ = True

# ===========================
# STATIC & MEDIA FILES
# ===========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static"
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===========================
# MESSAGES & LOGIN
# ===========================
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

LOGIN_URL = '/autenticacion/login/'

# ===========================
# DEFAULT
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
