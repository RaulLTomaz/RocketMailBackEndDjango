from django.conf import settings
from django.db import models

from apps.core.constants import COMENTARIO_MAX_LENGTH


class Comentario(models.Model):
    comentario = models.CharField(max_length=COMENTARIO_MAX_LENGTH)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comentarios",
    )
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="comentarios",
        db_index=True,
    )
    data_criacao = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "comentario"
        indexes = [
            models.Index(fields=["post", "-data_criacao"], name="ix_comentario_post_data"),
        ]

    def __str__(self) -> str:
        return f"Comentario {self.pk}"
