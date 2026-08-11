from django.conf import settings
from django.db import models

from apps.core.constants import POST_MAX_LENGTH


class Post(models.Model):
    post = models.CharField(max_length=POST_MAX_LENGTH)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        db_index=True,
    )
    data_criacao = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "post"
        indexes = [
            models.Index(fields=["usuario"], name="ix_post_usuario_id"),
            models.Index(fields=["-data_criacao"], name="ix_post_data_criacao"),
        ]

    def __str__(self) -> str:
        return f"Post {self.pk}"
