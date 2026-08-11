"""Tarefas de boot do processo WSGI/ASGI — fora de AppConfig.ready()."""

from __future__ import annotations

import logging

logger = logging.getLogger("rocketmail")


def limpar_foto_urls_efemeras() -> None:
    """Disco do Render é efêmero: zera foto_url locais sem tocar URLs Cloudinary."""
    from django.conf import settings

    if getattr(settings, "PYTHON_ENV", "") == "test":
        return

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
