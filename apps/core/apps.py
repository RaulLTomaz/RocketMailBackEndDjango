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

        if any(cmd in sys.argv for cmd in ("makemigrations", "migrate", "collectstatic")):
            return
        if getattr(settings, "PYTHON_ENV", "") == "test":
            return
        self._log_boot()
        self._limpar_foto_urls_efemeras()

    def _log_boot(self) -> None:
        from django.conf import settings

        from apps.core.storage import cloudinary_config_error, cloudinary_enabled, cloudinary_url

        db = settings.DATABASES.get("default", {})
        logger.info(
            "Conectando no banco host=%s name=%s",
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

    def _limpar_foto_urls_efemeras(self) -> None:
        """Disco do Render é efêmero: zera foto_url locais sem tocar URLs Cloudinary."""
        try:
            from apps.usuarios.models import Usuario

            atualizados = Usuario.objects.filter(
                foto_url__isnull=False,
                foto_url__contains="/media/avatars/",
            ).update(foto_url=None)
            if atualizados:
                logger.warning(
                    "Limpou %s foto_url efêmera(s) apontando para /media/avatars/",
                    atualizados,
                )
        except Exception:
            logger.exception("Falha ao limpar foto_url efêmeras")
