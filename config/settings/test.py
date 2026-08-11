"""Testes: Postgres via DATABASE_URL_TEST, CORS com a origin do front."""

import os
from pathlib import Path

from dotenv import load_dotenv

os.environ["PYTHON_ENV"] = "test"
_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_ROOT / ".env.test", override=False)
if os.getenv("DATABASE_URL_TEST") and not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.environ["DATABASE_URL_TEST"]

from .base import *  # noqa: E402,F401,F403
from .base import ALLOWED_ORIGIN_REGEX, _DEFAULT_PROD_ORIGINS  # noqa: E402

DEBUG = False

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = list(
    dict.fromkeys(
        [
            "https://rocket-mail-site.vercel.app",
            "http://localhost:8081",
            "http://localhost:3000",
            "http://127.0.0.1:8081",
            "http://127.0.0.1:3000",
            *_DEFAULT_PROD_ORIGINS,
        ]
    )
)
CORS_ALLOWED_ORIGIN_REGEXES = [ALLOWED_ORIGIN_REGEX] if ALLOWED_ORIGIN_REGEX else []

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
