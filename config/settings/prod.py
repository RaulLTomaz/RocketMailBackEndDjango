"""Produção: SECRET_KEY forte obrigatória, DEBUG off e SSL no Postgres."""

import os

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

_raw_hosts = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "").split(",")
    if host.strip() and host.strip() != "*"
]
if not _raw_hosts:
    raise RuntimeError(
        "ALLOWED_HOSTS deve listar hosts explícitos em produção "
        "(ex.: rocketmail-django.onrender.com)."
    )
ALLOWED_HOSTS = _raw_hosts

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "1") == "1"
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
