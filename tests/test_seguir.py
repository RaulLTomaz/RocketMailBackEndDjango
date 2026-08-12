from tests.helpers import (
    auth_header,
    cria_usuario_com_token,
    deixar_de_seguir,
    seguir,
)


def test_seguir_requer_auth(client):
    _, _ = cria_usuario_com_token(client)
    b, _ = cria_usuario_com_token(client)
    resp = client.post(f"/seguir/?seguido_id={b['id']}")
    assert resp.status_code == 401


def test_seguir_e_deixar_de_seguir(client):
    a, token_a = cria_usuario_com_token(client, nome="Seguidor")
    b, _ = cria_usuario_com_token(client, nome="Seguido")

    resp = seguir(client, token_a, b["id"])
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["seguidor_id"] == a["id"]
    assert body["seguido_id"] == b["id"]

    resp2 = seguir(client, token_a, b["id"])
    assert resp2.status_code == 200

    stats = client.get(f"/usuario/{a['id']}/stats")
    assert stats.status_code == 200
    assert stats.json()["stats"]["seguindo"] == 1

    resp_un = deixar_de_seguir(client, token_a, b["id"])
    assert resp_un.status_code == 200
    assert resp_un.json()["deleted"] is True

    stats2 = client.get(f"/usuario/{a['id']}/stats")
    assert stats2.json()["stats"]["seguindo"] == 0


def test_nao_pode_seguir_a_si_mesmo(client):
    a, token_a = cria_usuario_com_token(client)
    resp = seguir(client, token_a, a["id"])
    assert resp.status_code == 400


def test_seguir_usuario_inexistente(client):
    _, token = cria_usuario_com_token(client)
    resp = seguir(client, token, 99999999)
    assert resp.status_code == 404


def test_seguir_nao_usa_seguidor_id_da_query(client):
    a, token_a = cria_usuario_com_token(client)
    b, _ = cria_usuario_com_token(client)
    c, _ = cria_usuario_com_token(client)

    resp = client.post(
        f"/seguir/?seguidor_id={c['id']}&seguido_id={b['id']}",
        **auth_header(token_a),
    )
    assert resp.status_code == 200
    assert resp.json()["seguidor_id"] == a["id"]
    assert resp.json()["seguido_id"] == b["id"]


def test_listar_seguidos(client):
    a, token_a = cria_usuario_com_token(client, nome="SeguidorLista")
    b, _ = cria_usuario_com_token(client, nome="SeguidoLista")
    seguir(client, token_a, b["id"])

    resp = client.get("/seguir/seguidos", **auth_header(token_a))
    assert resp.status_code == 200
    ids = [u["id"] for u in resp.json()]
    assert b["id"] in ids


def test_unfollow_idempotente(client):
    a, token_a = cria_usuario_com_token(client)
    b, _ = cria_usuario_com_token(client)
    seguir(client, token_a, b["id"])
    assert deixar_de_seguir(client, token_a, b["id"]).status_code == 200
    resp = deixar_de_seguir(client, token_a, b["id"])
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True
