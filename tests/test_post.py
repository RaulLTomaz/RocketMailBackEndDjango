import time

from tests.helpers import (
    auth_header,
    cria_post,
    cria_usuario_com_token,
    seguir,
)


def test_criar_post(client):
    user, token = cria_usuario_com_token(client, nome="Autor")
    resp = cria_post(client, token, "Olá, este é um post de teste")
    assert resp.status_code == 201, resp.content
    data = resp.json()
    assert data["post"] == "Olá, este é um post de teste"
    assert data["usuario"]["id"] == user["id"]
    assert "email" not in data["usuario"]
    assert "id" in data
    assert "data_criacao" in data


def test_criar_post_sem_auth(client):
    resp = client.post("/post/", {"post": "sem token"}, format="json")
    assert resp.status_code == 401


def test_criar_post_vazio_ou_espacos(client):
    _, token = cria_usuario_com_token(client)
    for conteudo in ("", " ", "\n\t"):
        resp = client.post(
            "/post/",
            {"post": conteudo},
            format="json",
            **auth_header(token),
        )
        assert resp.status_code == 422, f"conteudo={conteudo!r} -> {resp.content}"


def test_listar_posts(client):
    user, token = cria_usuario_com_token(client)
    texto = "post único do listador"
    cria_post(client, token, texto)

    resp_list = client.get("/post/", **auth_header(token))
    assert resp_list.status_code == 200, resp_list.content
    itens = resp_list.json()
    assert any(p["post"] == texto and p["usuario"]["id"] == user["id"] for p in itens)


def test_listar_posts_paginacao_e_ordenacao(client):
    _, token = cria_usuario_com_token(client)
    for i in range(3):
        cria_post(client, token, f"p{i}")
        time.sleep(0.01)

    resp_desc = client.get(
        "/post/",
        {"limit": 2, "offset": 0, "sort": "-data"},
        **auth_header(token),
    )
    assert resp_desc.status_code == 200
    assert len(resp_desc.json()) == 2

    resp_asc = client.get(
        "/post/",
        {"limit": 50, "sort": "data"},
        **auth_header(token),
    )
    assert resp_asc.status_code == 200
    datas = [p["data_criacao"] for p in resp_asc.json()]
    assert datas == sorted(datas)


def test_feed_prioriza_seguidos(client):
    a, token_a = cria_usuario_com_token(client, nome="Alice")
    b, token_b = cria_usuario_com_token(client, nome="Bob")
    c, token_c = cria_usuario_com_token(client, nome="Carol")

    assert seguir(client, token_a, b["id"]).status_code == 200

    txt_b = "post do Bob (seguido)"
    txt_c = "post da Carol (não seguido)"
    cria_post(client, token_b, txt_b)
    cria_post(client, token_c, txt_c)

    resp_feed = client.get("/post/feed", **auth_header(token_a))
    assert resp_feed.status_code == 200, resp_feed.content
    feed = resp_feed.json()
    assert len(feed) >= 2

    ids = [item["usuario"]["id"] for item in feed]
    textos = [item["post"] for item in feed]
    assert ids[0] == b["id"]

    first_non_b = next((i for i, uid in enumerate(ids) if uid != b["id"]), None)
    if first_non_b is not None:
        assert all(uid != b["id"] for uid in ids[first_non_b:])

    assert txt_b in textos
    assert txt_c in textos


def test_feed_ordem_temporal_dentro_dos_grupos(client):
    a, token_a = cria_usuario_com_token(client)
    b, token_b = cria_usuario_com_token(client)
    c, token_c = cria_usuario_com_token(client)

    assert seguir(client, token_a, b["id"]).status_code == 200

    cria_post(client, token_b, "B_old")
    time.sleep(0.01)
    cria_post(client, token_c, "C_newer_than_B_old")
    time.sleep(0.01)
    cria_post(client, token_b, "B_newest")

    feed = client.get("/post/feed", **auth_header(token_a)).json()

    assert feed[0]["usuario"]["id"] == b["id"]
    assert feed[0]["post"] == "B_newest"
    assert feed[1]["usuario"]["id"] == b["id"]
    assert feed[1]["post"] == "B_old"
    assert feed[2]["usuario"]["id"] == c["id"]
    assert feed[2]["post"] == "C_newer_than_B_old"


def test_deletar_post_autorizado_e_nao_autorizado(client):
    dono, token_dono = cria_usuario_com_token(client, nome="Dono")
    _, token_intruso = cria_usuario_com_token(client, nome="Intruso")

    resp_create = cria_post(client, token_dono, "post que só o dono pode deletar")
    assert resp_create.status_code == 201
    post_id = resp_create.json()["id"]

    resp_unauth = client.delete(f"/post/{post_id}", **auth_header(token_intruso))
    assert resp_unauth.status_code == 403

    resp_delete = client.delete(f"/post/{post_id}", **auth_header(token_dono))
    assert resp_delete.status_code == 200
    assert resp_delete.json()["deleted"] is True

    resp_list = client.get("/post/", **auth_header(token_dono))
    assert all(p["id"] != post_id for p in resp_list.json())


def test_deletar_post_inexistente(client):
    _, token = cria_usuario_com_token(client)
    resp = client.delete("/post/99999999", **auth_header(token))
    assert resp.status_code == 404
