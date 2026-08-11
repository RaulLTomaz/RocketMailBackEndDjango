from django.conf import settings
from django.db import models


class Seguir(models.Model):
    seguidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seguindo_rel",
    )
    seguido = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seguidores_rel",
        db_index=True,
    )

    class Meta:
        db_table = "seguir"
        constraints = [
            models.UniqueConstraint(
                fields=["seguidor", "seguido"],
                name="seguir_seguidor_seguido_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["seguido"], name="ix_seguir_seguido_id"),
        ]
