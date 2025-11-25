import os
from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages






# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar el archivo .env
load_dotenv(BASE_DIR /'.env')


# ===========================
# SECURITY
# ===========================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-default')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")



# Allow all hosts for development; in production, specify allowed hosts

ALLOWED_HOSTS = ['*']



# ===========================
# APPLICATIONS
# ===========================
INSTALLED_APPS = [
    'dal',
    'dal_select2',
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
    'sistema_erp.middleware.PasswordChangeRequiredMiddleware',  # RQ-USR-04: Fuerza cambio de clave provisoria
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


DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            # ruta EXACTA al CA bundle que descargaste:
            'ssl': {'ca': '/etc/ssl/certs/aws-rds/rds-combined-ca-bundle.pem'},
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


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

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
# EMAIL CONFIGURATION
# ===========================
# Configuración de correo para Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 3  # Timeout de 3 segundos para envío más rápido

# IMPORTANTE: Usa CLAVE DE APLICACIÓN (no tu contraseña real)
EMAIL_HOST_USER = 'rm434308@gmail.com'
EMAIL_HOST_PASSWORD = 'eoab fqrd kgyr hrki'

DEFAULT_FROM_EMAIL = 'rm434308@gmail.com'

# ===========================
# DEFAULT
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
