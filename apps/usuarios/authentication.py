from __future__ import annotations

import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from apps.usuarios.jwt import decodificar_token
from apps.usuarios.models import Usuario


class JWTAuthentication(BaseAuthentication):
    """Bearer JWT; token inválido ou usuário inexistente → 401 (mensagem fixa do contrato)."""

    def authenticate(self, request: Request):
        header = request.headers.get("Authorization") or ""
        if not header:
            return None
        partes = header.split()
        if len(partes) != 2 or partes[0].lower() != "bearer":
            raise AuthenticationFailed("Não autorizado")
        token = partes[1]
        try:
            usuario_id = decodificar_token(token)
        except (jwt.PyJWTError, TypeError, ValueError) as exc:
            raise AuthenticationFailed("Não autorizado") from exc

        usuario = Usuario.objects.filter(pk=usuario_id).first()
        if usuario is None:
            raise AuthenticationFailed("Não autorizado")
        return (usuario, token)

    def authenticate_header(self, request: Request) -> str:
        return "Bearer"
