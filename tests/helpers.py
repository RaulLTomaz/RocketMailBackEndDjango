from uuid import uuid4

from rest_framework.test import APIClient

from apps.usuarios.jwt import criar_token_acesso


def email_unico(prefixo: str = "user") -> str:
    return f"{prefixo}_{uuid4().hex[:12]}@example.com"


def auth_header(token: str) -> dict:
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


def cria_usuario(
    client: APIClient,
    nome: str | None = None,
    email: str | None = None,
    senha: str = "Senha123!",
) -> dict:
    payload = {
        "nome": nome or f"User {uuid4().hex[:6]}",
        "email": email or email_unico(),
        "senha": senha,
    }
    resp = client.post("/usuario/", payload, format="json")
    assert resp.status_code == 201, resp.content
    data = resp.json()
    data["_senha"] = senha
    return data


def login(client: APIClient, email: str, senha: str) -> str:
    resp = client.post(
        "/usuario/login",
        data=f"username={email}&password={senha}",
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == 200, resp.content
    return resp.json()["access_token"]


def cria_usuario_com_token(
    client: APIClient,
    nome: str | None = None,
    email: str | None = None,
    senha: str = "Senha123!",
) -> tuple[dict, str]:
    user = cria_usuario(client, nome=nome, email=email, senha=senha)
    token = criar_token_acesso(user["id"])
    return user, token


def cria_post(client: APIClient, token: str, conteudo: str):
    resp = client.post(
        "/post/",
        {"post": conteudo},
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )
    assert resp.status_code == 201, resp.content
    return resp


def seguir(client: APIClient, seguidor_token: str, seguido_id: int):
    return client.post(
        f"/seguir/?seguido_id={seguido_id}",
        HTTP_AUTHORIZATION=f"Bearer {seguidor_token}",
    )


def deixar_de_seguir(client: APIClient, seguidor_token: str, seguido_id: int):
    return client.delete(
        f"/seguir/?seguido_id={seguido_id}",
        HTTP_AUTHORIZATION=f"Bearer {seguidor_token}",
    )
