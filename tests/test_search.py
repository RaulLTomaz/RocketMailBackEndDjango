from tests.helpers import auth_header, cria_post, cria_usuario_com_token


def test_search_requer_auth(client):
    resp = client.get("/usuario/search", {"q": "a"})
    assert resp.status_code == 401


def test_search_q_vazio_400(client):
    _, token = cria_usuario_com_token(client)
    resp = client.get("/usuario/search", {"q": " "}, **auth_header(token))
    assert resp.status_code == 400


def test_search_sem_match_retorna_lista_vazia(client):
    _, token = cria_usuario_com_token(client)
    resp = client.get(
        "/usuario/search",
        {"q": "zzzz_inexistente_xyz"},
        **auth_header(token),
    )
    assert resp.status_code == 200
    assert resp.json() == []


def test_search_parcial_case_insensitive_com_posts(client):
    a, token_a = cria_usuario_com_token(client, nome="Ana Maria")
    b, token_b = cria_usuario_com_token(client, nome="carla silva")
    cria_usuario_com_token(client, nome="Bruno Costa")

    cria_post(client, token_a, "post antigo ana")
    cria_post(client, token_a, "post novo ana")
    cria_post(client, token_b, "post da carla")

    resp = client.get(
        "/usuario/search",
        {"q": "ANA", "limit": 20, "posts_per_user": 5},
        **auth_header(token_a),
    )
    assert resp.status_code == 200, resp.content
    hits = resp.json()
    assert len(hits) == 1
    assert hits[0]["usuario"]["id"] == a["id"]
    assert hits[0]["usuario"]["nome"] == "Ana Maria"
    assert "senha" not in hits[0]["usuario"]
    assert "email" in hits[0]["usuario"]
    assert len(hits[0]["posts"]) == 2
    assert hits[0]["posts"][0]["post"] == "post novo ana"
    assert hits[0]["posts"][0]["usuario"]["id"] == a["id"]
    assert "foto_url" in hits[0]["posts"][0]["usuario"]

    resp2 = client.get("/usuario/search", {"q": "Sil"}, **auth_header(token_a))
    assert resp2.status_code == 200
    nomes = [h["usuario"]["nome"] for h in resp2.json()]
    assert "carla silva" in nomes


def test_search_limita_posts_por_usuario(client):
    user, token = cria_usuario_com_token(client, nome="Posts Limit User")
    for i in range(6):
        cria_post(client, token, f"p{i}")

    resp = client.get(
        "/usuario/search",
        {"q": "Posts Limit", "posts_per_user": 2},
        **auth_header(token),
    )
    assert resp.status_code == 200
    hits = resp.json()
    assert len(hits) == 1
    assert len(hits[0]["posts"]) == 2


def test_search_nao_conflita_com_id(client):
    user, token = cria_usuario_com_token(client, nome="Search Route")
    resp = client.get("/usuario/search", {"q": "Search"}, **auth_header(token))
    assert resp.status_code == 200
    assert any(h["usuario"]["id"] == user["id"] for h in resp.json())

    by_id = client.get(f"/usuario/{user['id']}")
    assert by_id.status_code == 200
    assert by_id.json()["id"] == user["id"]
