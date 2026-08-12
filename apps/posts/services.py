from __future__ import annotations

from collections import defaultdict

from django.db import transaction
from django.db.models import Case, IntegerField, QuerySet, Value, When

from apps.core.exceptions import APIError
from apps.likes.models import Like
from apps.posts.models import Post
from apps.seguir.models import Seguir


def _com_autor() -> QuerySet[Post]:
    return Post.objects.select_related("usuario")


def criar_post(*, texto: str, usuario) -> Post:
    post = Post.objects.create(post=texto, usuario=usuario)
    return _com_autor().get(pk=post.pk)


def listar_posts(*, limit: int, offset: int, sort: str) -> list[Post]:
    qs = _com_autor()
    if sort == "data":
        qs = qs.order_by("data_criacao")
    else:
        qs = qs.order_by("-data_criacao")
    return list(qs[offset : offset + limit])


def listar_posts_do_usuario(*, usuario_id: int, limit: int, offset: int) -> list[Post]:
    return list(
        _com_autor()
        .filter(usuario_id=usuario_id)
        .order_by("-data_criacao")[offset : offset + limit]
    )


def listar_feed(*, viewer_id: int, limit: int, offset: int) -> list[Post]:
    """Prioriza posts de quem o viewer segue; depois o restante por data decrescente."""
    seguidos = Seguir.objects.filter(seguidor_id=viewer_id).values("seguido_id")
    qs = (
        _com_autor()
        .annotate(
            prioridade=Case(
                When(usuario_id__in=seguidos, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by("prioridade", "-data_criacao")
    )
    return list(qs[offset : offset + limit])


def posts_recentes_por_usuarios(
    user_ids: list[int], per_user: int, autores=None
) -> dict[int, list[Post]]:
    """Window function (ROW_NUMBER) em uma query — evita N+1 no Explore/search."""
    if not user_ids or per_user <= 0:
        return {}

    placeholders = ", ".join(["%s"] * len(user_ids))
    sql = f"""
        SELECT p.id, p.post, p.data_criacao, p.usuario_id
        FROM (
            SELECT id, post, data_criacao, usuario_id,
                   ROW_NUMBER() OVER (
                       PARTITION BY usuario_id ORDER BY data_criacao DESC
                   ) AS rn
            FROM post
            WHERE usuario_id IN ({placeholders})
        ) p
        WHERE p.rn <= %s
        ORDER BY p.usuario_id, p.rn
    """
    rows = list(Post.objects.raw(sql, [*user_ids, per_user]))
    if autores is None:
        from apps.usuarios.models import Usuario

        autores = Usuario.objects.filter(pk__in=user_ids).only(
            "id", "nome", "email", "foto_url"
        )
    by_autor = {u.id: u for u in autores}
    agrupado: dict[int, list[Post]] = defaultdict(list)
    for post in rows:
        post.usuario = by_autor.get(post.usuario_id)
        agrupado[post.usuario_id].append(post)
    return agrupado


def deletar_post(*, post_id: int, usuario_id: int) -> dict:
    post = Post.objects.filter(pk=post_id).only("id", "usuario_id").first()
    if post is None:
        raise APIError("Post não encontrado", status_code=404)
    if post.usuario_id != usuario_id:
        raise APIError("Sem permissão para deletar este post", status_code=403)

    with transaction.atomic():
        Like.objects.filter(post_id=post_id).delete()
        post.delete()
    return {"deleted": True, "id": post_id}
