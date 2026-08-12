import logging
import sys

from django.apps import AppConfig

logger = logging.getLogger("rocketmail")


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
    verbose_name = "Core"

    def ready(self) -> None:
        from django.conf import settings

        # Sem log de boot durante migrate/collectstatic no deploy nem nos testes.
        if any(cmd in sys.argv for cmd in ("makemigrations", "migrate", "collectstatic")):
            return
        if getattr(settings, "PYTHON_ENV", "") == "test":
            return
        self._log_boot()

    def _log_boot(self) -> None:
        from django.conf import settings

        from apps.core.storage import cloudinary_config_error, cloudinary_enabled, cloudinary_url

        db = settings.DATABASES.get("default", {})
        logger.info(
            "Django boot host=%s name=%s",
            db.get("HOST") or "localhost",
            db.get("NAME"),
        )
        if cloudinary_enabled():
            err = cloudinary_config_error()
            if err:
                logger.error("%s", err)
            else:
                url = cloudinary_url()
                hint = url.split("@")[-1] if url and "@" in url else "vars CLOUDINARY_*"
                logger.info("Cloudinary configurado (%s)", hint)
        elif settings.PYTHON_ENV in ("production", "prod"):
            logger.error(
                "CLOUDINARY_URL ausente em produção. "
                "POST /usuario/me/foto retornará 503 até configurar Cloudinary no Render."
            )
        else:
            logger.warning("Cloudinary não configurado — usando disco local (dev/test)")
