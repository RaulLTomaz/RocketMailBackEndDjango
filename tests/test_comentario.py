from apps.comentarios.models import Comentario
from tests.helpers import (
    auth_header,
    cria_post,
    cria_usuario_com_token,
)


def test_comentar_requer_auth(client):
    a, token_a = cria_usuario_com_token(client)
    post_id = cria_post(client, token_a, "post para comentar").json()["id"]
    resp = client.post(
        f"/comentario/post/{post_id}",
        {"comentario": "olá"},
        format="json",
    )
    assert resp.status_code == 401


def test_criar_e_listar_comentario(client):
    a, token_a = cria_usuario_com_token(client, nome="AutorPost")
    b, token_b = cria_usuario_com_token(client, nome="Comentador")
    post_id = cria_post(client, token_a, "post comentável").json()["id"]

    resp = client.post(
        f"/comentario/post/{post_id}",
        {"comentario": "  primeiro comentário  "},
        format="json",
        **auth_header(token_b),
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body["comentario"] == "primeiro comentário"
    assert body["post_id"] == post_id
    assert body["usuario"]["id"] == b["id"]
    assert body["usuario"]["nome"] == "Comentador"
    assert "email" not in body["usuario"]
    assert "senha" not in body["usuario"]
    assert "data_criacao" in body

    lista = client.get(f"/comentario/post/{post_id}", **auth_header(token_a))
    assert lista.status_code == 200
    itens = lista.json()
    assert len(itens) == 1
    assert itens[0]["id"] == body["id"]
    assert itens[0]["comentario"] == "primeiro comentário"


def test_comentario_vazio_422(client):
    _, token = cria_usuario_com_token(client)
    post_id = cria_post(client, token, "post").json()["id"]
    for texto in ("", " ", "\n\t"):
        resp = client.post(
            f"/comentario/post/{post_id}",
            {"comentario": texto},
            format="json",
            **auth_header(token),
        )
        assert resp.status_code == 422, f"texto={texto!r} -> {resp.content}"


def test_comentario_post_inexistente_404(client):
    _, token = cria_usuario_com_token(client)
    resp = client.post(
        "/comentario/post/99999999",
        {"comentario": "x"},
        format="json",
        **auth_header(token),
    )
    assert resp.status_code == 404


def test_deletar_proprio_comentario(client):
    a, token_a = cria_usuario_com_token(client)
    post_id = cria_post(client, token_a, "post").json()["id"]
    criado = client.post(
        f"/comentario/post/{post_id}",
        {"comentario": "apagar"},
        format="json",
        **auth_header(token_a),
    ).json()

    resp = client.delete(f"/comentario/{criado['id']}", **auth_header(token_a))
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True
    assert client.get(f"/comentario/post/{post_id}", **auth_header(token_a)).json() == []


def test_nao_pode_deletar_comentario_alheio(client):
    a, token_a = cria_usuario_com_token(client)
    _, token_b = cria_usuario_com_token(client)
    post_id = cria_post(client, token_a, "post").json()["id"]
    criado = client.post(
        f"/comentario/post/{post_id}",
        {"comentario": "meu"},
        format="json",
        **auth_header(token_a),
    ).json()

    resp = client.delete(f"/comentario/{criado['id']}", **auth_header(token_b))
    assert resp.status_code == 403


def test_deletar_post_remove_comentarios(client):
    a, token_a = cria_usuario_com_token(client)
    post_id = cria_post(client, token_a, "post com comentário").json()["id"]
    criado = client.post(
        f"/comentario/post/{post_id}",
        {"comentario": "some junto"},
        format="json",
        **auth_header(token_a),
    ).json()
    cid = criado["id"]

    assert client.delete(f"/post/{post_id}", **auth_header(token_a)).status_code == 200
    assert not Comentario.objects.filter(pk=cid).exists()
