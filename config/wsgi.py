import os

from django.core.wsgi import get_wsgi_application

_env = os.getenv("PYTHON_ENV", "dev").lower()
_mapping = {
    "production": "config.settings.prod",
    "prod": "config.settings.prod",
    "test": "config.settings.test",
    "dev": "config.settings.dev",
    "development": "config.settings.dev",
}
os.environ.setdefault("DJANGO_SETTINGS_MODULE", _mapping.get(_env, "config.settings.dev"))

application = get_wsgi_application()

# Após o setup do Django: queries em AppConfig.ready() geram RuntimeWarning.
from apps.core.boot import limpar_foto_urls_efemeras  # noqa: E402

limpar_foto_urls_efemeras()
