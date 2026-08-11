from django.conf import settings
from django.db import models


class Like(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="likes",
        db_index=True,
    )

    class Meta:
        db_table = "like"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "post"],
                name="like_usuario_post_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["post"], name="ix_like_post_id"),
        ]
