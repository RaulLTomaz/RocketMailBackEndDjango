import time

from tests.helpers import cria_post, cria_usuario_com_token, seguir


def test_stats_usuario_contadores(client):
    a, token_a = cria_usuario_com_token(client, nome="AliceStats")
    b, _ = cria_usuario_com_token(client, nome="BobStats")
    c, token_c = cria_usuario_com_token(client, nome="CarolStats")

    cria_post(client, token_a, "post 1 da Alice")
    time.sleep(0.01)
    cria_post(client, token_a, "post 2 da Alice")

    assert seguir(client, token_a, b["id"]).status_code == 200
    assert seguir(client, token_c, a["id"]).status_code == 200

    resp = client.get(f"/usuario/{a['id']}/stats")
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["usuario"]["id"] == a["id"]
    assert body["stats"]["posts"] == 2
    assert body["stats"]["seguidores"] == 1
    assert body["stats"]["seguindo"] == 1


def test_stats_usuario_inexistente(client):
    resp = client.get("/usuario/99999999/stats")
    assert resp.status_code == 404


def test_timeline_usuario_paginada(client):
    a, token_a = cria_usuario_com_token(client, nome="AliceTL")
    b, token_b = cria_usuario_com_token(client, nome="BobTL")

    cria_post(client, token_a, "A_post_1")
    time.sleep(0.01)
    cria_post(client, token_a, "A_post_2")
    time.sleep(0.01)
    cria_post(client, token_a, "A_post_3")
    cria_post(client, token_b, "B_post_1")

    resp_all = client.get(f"/usuario/{a['id']}/posts")
    assert resp_all.status_code == 200
    items = resp_all.json()
    assert len(items) == 3
    assert all(p["usuario"]["id"] == a["id"] for p in items)
    assert [p["post"] for p in items] == ["A_post_3", "A_post_2", "A_post_1"]

    page1 = client.get(f"/usuario/{a['id']}/posts", {"limit": 2, "offset": 0}).json()
    assert [p["post"] for p in page1] == ["A_post_3", "A_post_2"]

    page2 = client.get(f"/usuario/{a['id']}/posts", {"limit": 2, "offset": 2}).json()
    assert [p["post"] for p in page2] == ["A_post_1"]
