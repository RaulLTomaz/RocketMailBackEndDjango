"""Produção: SECRET_KEY obrigatória, DEBUG off, SSL no Postgres."""

from .base import *  # noqa: F401,F403
from .base import SECRET_KEY

DEBUG = False

_INSECURE_SECRETS = {
    "",
    "changeme",
    "super-secret",
    "changeme_super_secret",
    "dev-insecure-secret-key-nao-usar-em-producao",
    "secret",
    "insecure",
}

if not SECRET_KEY or SECRET_KEY.strip().lower() in _INSECURE_SECRETS:
    raise RuntimeError(
        "SECRET_KEY deve ser definida com um valor forte em produção."
    )

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
