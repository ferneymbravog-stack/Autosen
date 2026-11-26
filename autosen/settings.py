"""
Configuración de AutoSen (migración de Spring Boot a Django).

Los valores sensibles se leen del archivo .env (ver .env.example).
Las decisiones de fidelidad con el proyecto Java están en
docs/superpowers/specs/2026-10-21-migracion-django-design.md.
"""
import os
import sys
import warnings
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

EN_PRUEBAS = "test" in sys.argv

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = os.environ.get("DEBUG", "False") == "True"

# 10.0.2.2 es la IP con la que el emulador de Android ve el PC (la app usa http://10.0.2.2:8080/).
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "10.0.2.2"] + [
    host.strip() for host in os.environ.get("ALLOWED_HOSTS_EXTRA", "").split(",") if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "core",
    "web",
    "panel",
    "reportes",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "core.middleware.TemaMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "autosen.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "core.context_processors.admin_correo",
            ],
        },
    },
]

WSGI_APPLICATION = "autosen.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "vehiculos"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# Hora local sin zona horaria, igual que LocalDateTime en Java.
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = False

# Estáticos (S3): servidos en /static/ por WhiteNoise, también con DEBUG=False y sin collectstatic.
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_USE_FINDERS = True
# staticfiles/ solo existe tras collectstatic; con WHITENOISE_USE_FINDERS no hace falta en desarrollo.
# Sin module=: WhiteNoise avisa con stacklevel=3 y el aviso se atribuye a quien carga el middleware.
warnings.filterwarnings("ignore", message="No directory at", category=UserWarning)

CSRF_FAILURE_VIEW = "core.errores.error_csrf"

# Sesiones: 30 minutos de inactividad y cookie de sesión del navegador, como Spring/Tomcat.
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Las rutas Java no llevan barra final.
APPEND_SLASH = False

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Servicios externos: en pruebas quedan vacíos por defecto para no hacer llamadas reales.
TELEGRAM_BOT_TOKEN = "" if EN_PRUEBAS else os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = "" if EN_PRUEBAS else os.environ.get("TELEGRAM_CHAT_ID", "").strip()

# Correo saliente (Gmail SMTP); sin credenciales se usa el backend de consola.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com").strip() or "smtp.gmail.com"
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587") or "587")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = "" if EN_PRUEBAS else os.environ.get("EMAIL_HOST_USER", "").strip()
EMAIL_HOST_PASSWORD = "" if EN_PRUEBAS else os.environ.get("EMAIL_HOST_PASSWORD", "").strip()
DEFAULT_FROM_EMAIL = (
    os.environ.get("DEFAULT_FROM_EMAIL", "").strip()
    or EMAIL_HOST_USER
    or "AutoSen Alertas <noreply@autosen.local>"
)
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", "10") or "10")
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if (EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)
    else "django.core.mail.backends.console.EmailBackend"
)
SITE_URL = os.environ.get("SITE_URL", "http://localhost:8080").strip().rstrip("/") or "http://localhost:8080"

# WhatsApp Cloud API de Meta
WHATSAPP_TOKEN = "" if EN_PRUEBAS else os.environ.get("WHATSAPP_TOKEN", "").strip()
WHATSAPP_PHONE_NUMBER_ID = "" if EN_PRUEBAS else os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()
WHATSAPP_API_VERSION = "" if EN_PRUEBAS else os.environ.get("WHATSAPP_API_VERSION", "").strip()

# Despacho asíncrono tras commit (False en pruebas para ejecución determinista).
NOTIFICACIONES_ASINCRONAS = False if EN_PRUEBAS else os.environ.get("NOTIFICACIONES_ASINCRONAS", "True") == "True"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "consola": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "autosen": {"handlers": ["consola"], "level": "INFO"},
    },
}
