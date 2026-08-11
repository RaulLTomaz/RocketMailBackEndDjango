"""Settings comuns a todos os ambientes."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from corsheaders.defaults import default_headers
from dotenv import load_dotenv

from apps.core.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES_DEFAULT,
    FOTO_MAX_BYTES_DEFAULT,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PYTHON_ENV = os.getenv("PYTHON_ENV", "dev").lower()

if PYTHON_ENV == "test":
    load_dotenv(BASE_DIR / ".env.test", override=False)
elif PYTHON_ENV in ("dev", "development"):
    load_dotenv(BASE_DIR / ".env", override=False)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-secret-key-nao-usar-em-producao")

DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "apps.core.apps.CoreConfig",
    "apps.usuarios.apps.UsuariosConfig",
    "apps.posts.apps.PostsConfig",
    "apps.seguir.apps.SeguirConfig",
    "apps.likes.apps.LikesConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

# API JWT stateless: sem SessionAuthentication e sem redirect de barra final
# (o front mistura paths com e sem `/`).
APPEND_SLASH = False
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = []

AUTH_USER_MODEL = "usuarios.Usuario"

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", BASE_DIR / "media")).resolve()

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")

FOTO_MAX_BYTES = int(os.getenv("FOTO_MAX_BYTES", str(FOTO_MAX_BYTES_DEFAULT)))
FILE_UPLOAD_MAX_MEMORY_SIZE = FOTO_MAX_BYTES
DATA_UPLOAD_MAX_MEMORY_SIZE = FOTO_MAX_BYTES + 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]


def _database_url() -> str:
    url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_URL_TEST")
    if not url:
        raise ValueError("DATABASE_URL não definida.")
    return url.replace("postgres://", "postgresql://", 1)


def _use_ssl() -> bool:
    return PYTHON_ENV in ("production", "prod") or os.getenv("DATABASE_SSL", "0") == "1"


def _ssl_verify() -> bool:
    return os.getenv("DATABASE_SSL_VERIFY", "0") == "1"


def build_databases() -> dict:
    url = _database_url()
    config = dj_database_url.parse(url, conn_max_age=600)
    config["ATOMIC_REQUESTS"] = False
    config["CONN_HEALTH_CHECKS"] = True
    if _use_ssl():
        options = dict(config.get("OPTIONS") or {})
        options["sslmode"] = "verify-full" if _ssl_verify() else "require"
        config["OPTIONS"] = options
    return {"default": config}


DATABASES = build_databases()

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(ACCESS_TOKEN_EXPIRE_MINUTES_DEFAULT))
)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "sub",
    "UPDATE_LAST_LOGIN": False,
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.usuarios.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "apps.core.renderers.UTF8JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "EXCEPTION_HANDLER": "apps.core.exceptions.api_exception_handler",
    "UNAUTHENTICATED_USER": None,
    "DATETIME_FORMAT": None,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

_DEFAULT_PROD_ORIGINS = [
    "https://rocket-mail-site.vercel.app",
    "http://localhost:8081",
    "http://localhost:3000",
    "http://127.0.0.1:8081",
    "http://127.0.0.1:3000",
]

ALLOWED_ORIGINS_RAW = os.getenv(
    "ALLOWED_ORIGINS",
    "https://rocket-mail-site.vercel.app,http://localhost:8081,http://localhost:3000",
)
ALLOWED_ORIGIN_REGEX = os.getenv(
    "ALLOWED_ORIGIN_REGEX",
    r"https://([\w-]+\.)*vercel\.app",
)

CORS_ALLOW_METHODS = ["GET", "POST", "PATCH", "DELETE", "OPTIONS", "PUT", "HEAD"]
# Inclui content-type para preflight de multipart (boundary no POST /usuario/me/foto).
CORS_ALLOW_HEADERS = list(
    dict.fromkeys(
        [
            *default_headers,
            "authorization",
            "content-type",
            "accept",
            "origin",
        ]
    )
)
CORS_PREFLIGHT_MAX_AGE = 86400


def configure_cors() -> None:
    """CORS explícito em produção; wildcard só em dev quando ALLOWED_ORIGINS=*."""
    global CORS_ALLOW_ALL_ORIGINS, CORS_ALLOWED_ORIGINS, CORS_ALLOWED_ORIGIN_REGEXES
    global CORS_ALLOW_CREDENTIALS

    raw = [o.strip() for o in ALLOWED_ORIGINS_RAW.split(",") if o.strip()]
    wants_wildcard = (not raw) or ("*" in raw)
    regex = (ALLOWED_ORIGIN_REGEX or "").strip()

    if PYTHON_ENV in ("production", "prod"):
        explicit = [o for o in raw if o != "*"]
        origins = list(dict.fromkeys([*explicit, *_DEFAULT_PROD_ORIGINS]))
        CORS_ALLOW_ALL_ORIGINS = False
        CORS_ALLOWED_ORIGINS = origins
        CORS_ALLOWED_ORIGIN_REGEXES = [regex] if regex else []
        CORS_ALLOW_CREDENTIALS = True
        return

    if wants_wildcard:
        CORS_ALLOW_ALL_ORIGINS = True
        CORS_ALLOWED_ORIGINS = []
        CORS_ALLOWED_ORIGIN_REGEXES = []
        CORS_ALLOW_CREDENTIALS = False
        return

    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = raw
    CORS_ALLOWED_ORIGIN_REGEXES = [regex] if regex else []
    CORS_ALLOW_CREDENTIALS = True


configure_cors()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[{levelname}] {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "rocketmail": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
