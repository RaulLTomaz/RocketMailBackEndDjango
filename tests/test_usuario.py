from tests.helpers import (
    auth_header,
    cria_usuario,
    cria_usuario_com_token,
    email_unico,
    login,
)


def test_criar_usuario_sucesso(client):
    email = email_unico("criar")
    resp = client.post(
        "/usuario/",
        {"nome": "Novo User", "email": email, "senha": "senha123"},
        format="json",
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["nome"] == "Novo User"
    assert body["email"] == email
    assert "id" in body
    assert "senha" not in body
    assert "password" not in body
    assert body.get("foto_url") is None


def test_criar_usuario_email_duplicado(client):
    email = email_unico("dup")
    cria_usuario(client, email=email)
    resp = client.post(
        "/usuario/",
        {"nome": "Outro", "email": email, "senha": "senha123"},
        format="json",
    )
    assert resp.status_code == 409
    assert "e-mail" in resp.json()["detail"].lower() or "email" in resp.json()["detail"].lower()


def test_criar_usuario_senha_curta(client):
    resp = client.post(
        "/usuario/",
        {"nome": "Curto", "email": email_unico("curto"), "senha": "123"},
        format="json",
    )
    assert resp.status_code in (400, 422)


def test_criar_usuario_nome_vazio(client):
    resp = client.post(
        "/usuario/",
        {"nome": "", "email": email_unico("vazio"), "senha": "senha123"},
        format="json",
    )
    assert resp.status_code in (400, 422)


def test_login_sucesso(client):
    user = cria_usuario(client, email=email_unico("login"), senha="minhasenha")
    token = login(client, user["email"], "minhasenha")
    assert isinstance(token, str) and len(token) > 10

    resp = client.get("/usuario/me", **auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["id"] == user["id"]


def test_login_email_case_insensitive(client):
    email = email_unico("CaseLogin")
    cria_usuario(client, email=email.lower(), senha="senha123")
    token = login(client, email.upper(), "senha123")
    assert isinstance(token, str) and len(token) > 10


def test_login_credenciais_invalidas(client):
    user = cria_usuario(client, email=email_unico("badlogin"))
    resp = client.post(
        "/usuario/login",
        data=f"username={user['email']}&password=errada",
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Credenciais inválidas"


def test_buscar_usuario_por_id(client):
    user = cria_usuario(client)
    resp = client.get(f"/usuario/{user['id']}")
    assert resp.status_code == 200
    assert resp.json()["email"] == user["email"]


def test_buscar_usuario_inexistente(client):
    resp = client.get("/usuario/99999999")
    assert resp.status_code == 404


def test_me_sem_token(client):
    resp = client.get("/usuario/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Não autorizado"
    assert resp.headers.get("WWW-Authenticate") == "Bearer"


def test_me_token_invalido(client):
    resp = client.get("/usuario/me", **auth_header("token.invalido.aqui"))
    assert resp.status_code == 401


def test_me_fluxo_completo(client):
    email = email_unico("me")
    user = cria_usuario(client, nome="Usuario Me", email=email, senha="senha123")
    token = login(client, email, "senha123")
    headers = auth_header(token)

    resp_me = client.get("/usuario/me", **headers)
    assert resp_me.status_code == 200
    assert resp_me.json()["id"] == user["id"]

    resp_patch = client.patch(
        "/usuario/me",
        {"nome": "Nome Novo", "email": email_unico("me_novo")},
        format="json",
        **headers,
    )
    assert resp_patch.status_code == 200
    assert resp_patch.json()["nome"] == "Nome Novo"

    resp_delete = client.delete("/usuario/me", **headers)
    assert resp_delete.status_code == 200
    assert resp_delete.json()["deleted"] is True

    assert client.get(f"/usuario/{user['id']}").status_code == 404
    assert client.get("/usuario/me", **headers).status_code == 401


def test_patch_me_email_duplicado(client):
    a = cria_usuario(client, email=email_unico("a"))
    _, token_b = cria_usuario_com_token(client, email=email_unico("b"))

    resp = client.patch(
        "/usuario/me",
        {"email": a["email"]},
        format="json",
        **auth_header(token_b),
    )
    assert resp.status_code == 409
