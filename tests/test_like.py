from tests.helpers import auth_header, cria_post, cria_usuario_com_token


def test_like_flows(client):
    a, token_a = cria_usuario_com_token(client, nome="AliceLike")
    _, token_b = cria_usuario_com_token(client, nome="BobLike")

    resp_post = cria_post(client, token_a, "post curtível")
    assert resp_post.status_code == 201
    post_id = resp_post.json()["id"]

    r = client.get(f"/like/{post_id}", **auth_header(token_a))
    assert r.status_code == 200
    assert r.json() == {"post_id": post_id, "count": 0, "liked_by_me": False}

    r = client.post(f"/like/{post_id}", **auth_header(token_a))
    assert r.status_code == 200
    assert r.json()["liked"] is True

    r = client.get(f"/like/{post_id}", **auth_header(token_a))
    assert r.json()["count"] == 1
    assert r.json()["liked_by_me"] is True

    client.post(f"/like/{post_id}", **auth_header(token_a))
    r = client.get(f"/like/{post_id}", **auth_header(token_a))
    assert r.json()["count"] == 1

    r = client.get(f"/like/{post_id}", **auth_header(token_b))
    assert r.json()["count"] == 1
    assert r.json()["liked_by_me"] is False

    r = client.delete(f"/like/{post_id}", **auth_header(token_b))
    assert r.status_code == 200
    assert r.json()["liked"] is False
    assert client.get(f"/like/{post_id}", **auth_header(token_a)).json()["count"] == 1

    r = client.delete(f"/like/{post_id}", **auth_header(token_a))
    assert r.status_code == 200
    body = client.get(f"/like/{post_id}", **auth_header(token_a)).json()
    assert body["count"] == 0
    assert body["liked_by_me"] is False


def test_like_batch(client):
    a, token_a = cria_usuario_com_token(client)
    p1 = cria_post(client, token_a, "post 1").json()["id"]
    p2 = cria_post(client, token_a, "post 2").json()["id"]

    client.post(f"/like/{p1}", **auth_header(token_a))
    client.post(f"/like/{p2}", **auth_header(token_a))

    r = client.get(
        f"/like/batch?post_ids={p1}&post_ids={p2}",
        **auth_header(token_a),
    )
    assert r.status_code == 200, r.content
    batch = r.json()
    assert batch[str(p1)]["count"] == 1
    assert batch[str(p1)]["liked_by_me"] is True
    assert batch[str(p2)]["count"] == 1
    assert batch[str(p2)]["liked_by_me"] is True


def test_like_post_inexistente(client):
    _, token = cria_usuario_com_token(client)
    r = client.post("/like/99999999", **auth_header(token))
    assert r.status_code == 404


def test_like_requer_auth(client):
    a, token_a = cria_usuario_com_token(client)
    post_id = cria_post(client, token_a, "x").json()["id"]
    assert client.post(f"/like/{post_id}").status_code == 401
    assert client.get(f"/like/{post_id}").status_code == 401
    assert client.delete(f"/like/{post_id}").status_code == 401
