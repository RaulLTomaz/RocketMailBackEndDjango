from __future__ import annotations

from django.db.models import Count

from apps.core.exceptions import APIError
from apps.likes.models import Like
from apps.posts.models import Post


def _garantir_post_existe(post_id: int) -> None:
    if not Post.objects.filter(pk=post_id).exists():
        raise APIError("Post não encontrado", status_code=404)


def dar_like(*, usuario_id: int, post_id: int) -> dict:
    _garantir_post_existe(post_id)
    Like.objects.get_or_create(usuario_id=usuario_id, post_id=post_id)
    return {"liked": True, "post_id": int(post_id)}


def remover_like(*, usuario_id: int, post_id: int) -> dict:
    Like.objects.filter(usuario_id=usuario_id, post_id=post_id).delete()
    return {"liked": False, "post_id": int(post_id)}


def resumo_like(*, usuario_id: int, post_id: int) -> dict:
    count = Like.objects.filter(post_id=post_id).count()
    liked = Like.objects.filter(usuario_id=usuario_id, post_id=post_id).exists()
    return {"post_id": int(post_id), "count": count, "liked_by_me": liked}


def batch_resumo_like(*, usuario_id: int, post_ids: list[int]) -> dict[int, dict]:
    if not post_ids:
        return {}

    counts = {
        row["post_id"]: row["cnt"]
        for row in Like.objects.filter(post_id__in=post_ids)
        .values("post_id")
        .annotate(cnt=Count("id"))
    }
    mine = set(
        Like.objects.filter(usuario_id=usuario_id, post_id__in=post_ids).values_list(
            "post_id", flat=True
        )
    )
    out: dict[int, dict] = {}
    for pid in post_ids:
        ident = int(pid)
        out[ident] = {
            "post_id": ident,
            "count": int(counts.get(ident, 0)),
            "liked_by_me": ident in mine,
        }
    return out
