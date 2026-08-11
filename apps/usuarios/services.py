from __future__ import annotations

import logging

from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from rest_framework import status

from apps.core.exceptions import APIError
from apps.usuarios.jwt import criar_token_acesso
from apps.usuarios.models import Usuario

logger = logging.getLogger("rocketmail")


def queryset_publico():
    return Usuario.objects.publico()


def criar_usuario(*, nome: str, email: str, senha: str) -> Usuario:
    usuario = Usuario(nome=nome, email=email, foto_url=None)
    usuario.set_password(senha)
    try:
        with transaction.atomic():
            usuario.save()
    except IntegrityError as exc:
        raise APIError("E-mail já cadastrado.", status_code=status.HTTP_409_CONFLICT) from exc
    except Exception:
        logger.exception("Falha ao criar usuário")
        raise APIError("Não foi possível criar o usuário.", status_code=500)
    return usuario


def autenticar_usuario(email: str, senha: str) -> dict:
    email_norm = str(email).strip().lower()
    usuario = Usuario.objects.filter(email=email_norm).first()
    if usuario is None or not usuario.check_password(senha):
        raise APIError("Credenciais inválidas", status_code=status.HTTP_401_UNAUTHORIZED)
    return {
        "access_token": criar_token_acesso(usuario.id),
        "token_type": "bearer",
    }


def buscar_por_id(usuario_id: int) -> Usuario:
    usuario = queryset_publico().filter(pk=usuario_id).first()
    if usuario is None:
        raise APIError("Usuário não encontrado", status_code=status.HTTP_404_NOT_FOUND)
    return usuario


def atualizar_usuario(usuario: Usuario, dados: dict) -> Usuario:
    if "nome" in dados:
        usuario.nome = dados["nome"]
    if "email" in dados:
        usuario.email = dados["email"]
    if "senha" in dados:
        usuario.set_password(dados["senha"])
    if "foto_url" in dados:
        usuario.foto_url = dados["foto_url"]
    try:
        with transaction.atomic():
            usuario.save()
    except IntegrityError as exc:
        raise APIError("E-mail já cadastrado.", status_code=status.HTTP_409_CONFLICT) from exc
    except Exception:
        logger.exception("Falha ao atualizar usuário %s", usuario.id)
        raise APIError("Não foi possível atualizar o usuário.", status_code=500)
    return usuario


def atualizar_foto_url(usuario: Usuario, foto_url: str | None) -> Usuario:
    usuario.foto_url = foto_url
    usuario.save(update_fields=["foto_url"])
    return usuario


def deletar_usuario(usuario: Usuario) -> dict:
    from apps.likes.models import Like
    from apps.posts.models import Post
    from apps.seguir.models import Seguir

    with transaction.atomic():
        posts_ids = Post.objects.filter(usuario=usuario).values("id")
        Like.objects.filter(post_id__in=posts_ids).delete()
        Like.objects.filter(usuario=usuario).delete()
        Post.objects.filter(usuario=usuario).delete()
        Seguir.objects.filter(Q(seguidor=usuario) | Q(seguido=usuario)).delete()
        usuario.delete()
    return {"deleted": True}


def stats_usuario(usuario_id: int) -> dict:
    usuario = buscar_por_id(usuario_id)
    agregado = (
        Usuario.objects.filter(pk=usuario_id)
        .annotate(
            posts_count=Count("posts", distinct=True),
            seguidores_count=Count("seguidores_rel", distinct=True),
            seguindo_count=Count("seguindo_rel", distinct=True),
        )
        .values("posts_count", "seguidores_count", "seguindo_count")
        .first()
    ) or {"posts_count": 0, "seguidores_count": 0, "seguindo_count": 0}
    return {
        "usuario": usuario,
        "stats": {
            "posts": int(agregado["posts_count"]),
            "seguidores": int(agregado["seguidores_count"]),
            "seguindo": int(agregado["seguindo_count"]),
        },
    }


def buscar_usuarios_com_posts(q: str, limit: int, posts_per_user: int) -> list[dict]:
    from apps.posts.services import posts_recentes_por_usuarios

    termo = (q or "").strip()
    if not termo:
        raise APIError("Parâmetro q é obrigatório.", status_code=status.HTTP_400_BAD_REQUEST)

    usuarios = list(
        queryset_publico().filter(nome__icontains=termo).order_by("nome", "id")[:limit]
    )
    if not usuarios:
        return []

    posts_por_usuario = posts_recentes_por_usuarios(
        [u.id for u in usuarios], posts_per_user, autores=usuarios
    )
    return [
        {"usuario": usuario, "posts": posts_por_usuario.get(usuario.id, [])}
        for usuario in usuarios
    ]
