def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_root_json(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_json_charset_utf8(client):
    resp = client.get("/usuario/99999999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Usuário não encontrado"
    content_type = resp.headers.get("Content-Type", "").lower()
    assert "application/json" in content_type
    assert "charset=utf-8" in content_type


def test_cors_preflight_login(client):
    resp = client.options(
        "/usuario/login",
        HTTP_ORIGIN="https://rocket-mail-site.vercel.app",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,authorization",
    )
    assert resp.status_code in (200, 204)
    assert (
        resp.headers.get("Access-Control-Allow-Origin")
        == "https://rocket-mail-site.vercel.app"
    )


def test_cors_preflight_upload_foto(client):
    resp = client.options(
        "/usuario/me/foto",
        HTTP_ORIGIN="https://rocket-mail-site.vercel.app",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type",
    )
    assert resp.status_code in (200, 204)
    assert (
        resp.headers.get("Access-Control-Allow-Origin")
        == "https://rocket-mail-site.vercel.app"
    )
    allow_headers = (resp.headers.get("Access-Control-Allow-Headers") or "").lower()
    assert "content-type" in allow_headers
    assert "authorization" in allow_headers
