from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from rest_framework_simplejwt.settings import api_settings

from apps.likes.models import Like
from apps.posts.models import Post
from apps.seguir.models import Seguir
from apps.usuarios.jwt import criar_token_acesso
from tests.helpers import (
    auth_header,
    cria_post,
    cria_usuario,
    cria_usuario_com_token,
    email_unico,
    login,
    seguir,
)


def test_jwt_payload_sub_iat_exp_sem_email(client):
    user = cria_usuario(client, email=email_unico("jwtclaims"), senha="Senha123!")
    token = login(client, user["email"], "Senha123!")
    payload = jwt.decode(
        token,
        api_settings.SIGNING_KEY or settings.SECRET_KEY,
        algorithms=[api_settings.ALGORITHM or "HS256"],
    )
    assert set(payload.keys()) == {"sub", "iat", "exp"}
    assert payload["sub"] == str(user["id"])
    assert "email" not in payload
    assert payload["exp"] > payload["iat"]


def test_jwt_expirado_401(client):
    user, _ = cria_usuario_com_token(client)
    agora = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": str(user["id"]),
            "iat": int((agora - timedelta(hours=2)).timestamp()),
            "exp": int((agora - timedelta(hours=1)).timestamp()),
        },
        api_settings.SIGNING_KEY or settings.SECRET_KEY,
        algorithm=api_settings.ALGORITHM or "HS256",
    )
    resp = client.get("/usuario/me", **auth_header(token))
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Não autorizado"


def test_authorization_malformado_401(client):
    assert client.get("/usuario/me", HTTP_AUTHORIZATION="Bearer").status_code == 401
    assert client.get("/usuario/me", HTTP_AUTHORIZATION="Token abc").status_code == 401
    assert (
        client.get("/usuario/me", HTTP_AUTHORIZATION="Bearer a b c").status_code == 401
    )


def test_deletar_conta_remove_posts_likes_e_follows(client):
    a, token_a = cria_usuario_com_token(client, nome="ParaDeletar")
    b, token_b = cria_usuario_com_token(client, nome="Vizinho")

    post_id = cria_post(client, token_a, "vai sumir").json()["id"]
    client.post(f"/like/{post_id}", **auth_header(token_b))
    seguir(client, token_b, a["id"])
    seguir(client, token_a, b["id"])

    resp = client.delete("/usuario/me", **auth_header(token_a))
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    assert not Post.objects.filter(pk=post_id).exists()
    assert not Like.objects.filter(post_id=post_id).exists()
    assert not Seguir.objects.filter(seguidor_id=a["id"]).exists()
    assert not Seguir.objects.filter(seguido_id=a["id"]).exists()
    assert client.get(f"/usuario/{a['id']}").status_code == 404


def test_patch_me_senha_e_login_novo(client):
    email = email_unico("novasenha")
    user = cria_usuario(client, email=email, senha="Senha123!")
    token = login(client, email, "Senha123!")

    resp = client.patch(
        "/usuario/me",
        {"senha": "OutraSenha9!"},
        format="json",
        **auth_header(token),
    )
    assert resp.status_code == 200

    assert (
        client.post(
            "/usuario/login",
            data=f"username={email}&password=Senha123!",
            content_type="application/x-www-form-urlencoded",
        ).status_code
        == 401
    )
    novo = login(client, email, "OutraSenha9!")
    assert client.get("/usuario/me", **auth_header(novo)).status_code == 200


def test_patch_me_senha_fraca_422(client):
    _, token = cria_usuario_com_token(client)
    resp = client.patch(
        "/usuario/me",
        {"senha": "fraca"},
        format="json",
        **auth_header(token),
    )
    assert resp.status_code == 422


def test_token_acesso_helper_ainda_funciona(client):
    user, token = cria_usuario_com_token(client)
    assert criar_token_acesso(user["id"])
    assert client.get("/usuario/me", **auth_header(token)).status_code == 200
