def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


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
