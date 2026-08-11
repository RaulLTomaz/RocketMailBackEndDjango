from django.core.files.uploadedfile import SimpleUploadedFile

from tests.helpers import auth_header, cria_post, cria_usuario, cria_usuario_com_token

PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
)


def test_criar_usuario_foto_url_null(client):
    user = cria_usuario(client)
    assert user.get("foto_url") is None

    resp = client.get(f"/usuario/{user['id']}")
    assert resp.status_code == 200
    assert resp.json()["foto_url"] is None


def test_upload_foto_e_aparece_em_me_e_posts(client):
    user, token = cria_usuario_com_token(client)

    resp = client.post(
        "/usuario/me/foto",
        {"file": SimpleUploadedFile("avatar.png", PNG_1X1, content_type="image/png")},
        format="multipart",
        **auth_header(token),
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["id"] == user["id"]
    assert body["foto_url"]
    assert "/media/avatars/" in body["foto_url"] or body["foto_url"].startswith("http")

    me = client.get("/usuario/me", **auth_header(token))
    assert me.status_code == 200
    assert me.json()["foto_url"] == body["foto_url"]

    post_resp = cria_post(client, token, "post com avatar")
    assert post_resp.status_code == 201
    assert post_resp.json()["usuario"]["foto_url"] == body["foto_url"]

    feed = client.get("/post/feed", **auth_header(token))
    assert feed.status_code == 200
    meu = next(p for p in feed.json() if p["usuario"]["id"] == user["id"])
    assert meu["usuario"]["foto_url"] == body["foto_url"]


def test_upload_arquivo_invalido(client):
    _, token = cria_usuario_com_token(client)
    resp = client.post(
        "/usuario/me/foto",
        {"file": SimpleUploadedFile("nota.txt", b"nao sou imagem", content_type="text/plain")},
        format="multipart",
        **auth_header(token),
    )
    assert resp.status_code == 400


def test_delete_foto(client):
    _, token = cria_usuario_com_token(client)
    up = client.post(
        "/usuario/me/foto",
        {"file": SimpleUploadedFile("avatar.png", PNG_1X1, content_type="image/png")},
        format="multipart",
        **auth_header(token),
    )
    assert up.status_code == 200
    assert up.json()["foto_url"]

    deleted = client.delete("/usuario/me/foto", **auth_header(token))
    assert deleted.status_code == 200
    assert deleted.json()["foto_url"] is None


def test_patch_foto_url_externa(client):
    _, token = cria_usuario_com_token(client)
    url = "https://example.com/avatar.jpg"
    resp = client.patch(
        "/usuario/me",
        {"foto_url": url},
        format="json",
        **auth_header(token),
    )
    assert resp.status_code == 200
    assert resp.json()["foto_url"] == url


def test_producao_sem_cloudinary_retorna_503(client, monkeypatch):
    import apps.core.storage as storage

    monkeypatch.setenv("PYTHON_ENV", "production")
    monkeypatch.delenv("CLOUDINARY_URL", raising=False)
    monkeypatch.delenv("CLOUDINARY_CLOUD_NAME", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_KEY", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_SECRET", raising=False)

    _, token = cria_usuario_com_token(client)
    resp = client.post(
        "/usuario/me/foto",
        {"file": SimpleUploadedFile("avatar.png", PNG_1X1, content_type="image/png")},
        format="multipart",
        **auth_header(token),
    )
    assert resp.status_code == 503
    assert "CLOUDINARY" in resp.json()["detail"].upper()
    assert storage.cloudinary_enabled() is False


def test_cloudinary_erro_vira_502_nao_crash(client, monkeypatch):
    import apps.core.storage as storage

    monkeypatch.setenv("CLOUDINARY_URL", "cloudinary://key:secret@demo")

    def boom(*_a, **_k):
        raise RuntimeError("Invalid API Key")

    monkeypatch.setattr(storage, "_upload_cloudinary_sync", boom)

    _, token = cria_usuario_com_token(client)
    resp = client.post(
        "/usuario/me/foto",
        {"file": SimpleUploadedFile("avatar.png", PNG_1X1, content_type="image/png")},
        format="multipart",
        HTTP_ORIGIN="http://localhost:8081",
        **auth_header(token),
    )
    assert resp.status_code in (502, 503)
    detail = resp.json()["detail"]
    assert "Cloudinary" in detail or "upload" in detail.lower()
    assert resp.headers.get("Access-Control-Allow-Origin") in (
        "*",
        "http://localhost:8081",
    )
