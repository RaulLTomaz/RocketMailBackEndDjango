from __future__ import annotations

from django.db.models import QuerySet

from apps.comentarios.models import Comentario
from apps.core.exceptions import APIError
from apps.posts.models import Post


def _com_autor() -> QuerySet[Comentario]:
    return Comentario.objects.select_related("usuario")


def _garantir_post_existe(post_id: int) -> None:
    if not Post.objects.filter(pk=post_id).exists():
        raise APIError("Post não encontrado", status_code=404)


def criar_comentario(*, texto: str, post_id: int, usuario) -> Comentario:
    _garantir_post_existe(post_id)
    comentario = Comentario.objects.create(
        comentario=texto,
        post_id=post_id,
        usuario=usuario,
    )
    return _com_autor().get(pk=comentario.pk)


def listar_comentarios(*, post_id: int, limit: int, offset: int) -> list[Comentario]:
    _garantir_post_existe(post_id)
    return list(
        _com_autor()
        .filter(post_id=post_id)
        .order_by("data_criacao")[offset : offset + limit]
    )


def deletar_comentario(*, comentario_id: int, usuario_id: int) -> dict:
    comentario = Comentario.objects.filter(pk=comentario_id).only("id", "usuario_id").first()
    if comentario is None:
        raise APIError("Comentário não encontrado", status_code=404)
    if comentario.usuario_id != usuario_id:
        raise APIError("Sem permissão para deletar este comentário", status_code=403)
    comentario.delete()
    return {"deleted": True, "id": comentario_id}
