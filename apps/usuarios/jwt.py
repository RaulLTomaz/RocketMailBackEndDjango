"""
JWT no contrato do front: HS256 com `sub`, `iat` e `exp` (sem e-mail no payload).

Não usamos TokenObtainPair do SimpleJWT: ele devolve access/refresh e espera JSON
{username, password}, incompatível com o login OAuth2 password do RocketMail.
O SimpleJWT entra só para lifetime, algoritmo e chave de assinatura.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from rest_framework_simplejwt.settings import api_settings

from apps.core.constants import JWT_ALGORITHM


def criar_token_acesso(usuario_id: int) -> str:
    agora = datetime.now(timezone.utc)
    lifetime: timedelta = api_settings.ACCESS_TOKEN_LIFETIME
    payload = {
        "sub": str(usuario_id),
        "iat": int(agora.timestamp()),
        "exp": int((agora + lifetime).timestamp()),
    }
    return jwt.encode(
        payload,
        api_settings.SIGNING_KEY or settings.SECRET_KEY,
        algorithm=api_settings.ALGORITHM or JWT_ALGORITHM,
    )


def decodificar_token(token: str) -> int:
    payload = jwt.decode(
        token,
        api_settings.SIGNING_KEY or settings.SECRET_KEY,
        algorithms=[api_settings.ALGORITHM or JWT_ALGORITHM],
    )
    sub = payload.get("sub")
    if sub is None:
        raise jwt.InvalidTokenError("sub ausente")
    return int(sub)
