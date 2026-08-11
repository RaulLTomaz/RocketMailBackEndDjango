"""Erros da API no formato FastAPI: {"detail": "mensagem em português"}."""

from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler


class APIError(APIException):
    """Erro de negócio com status HTTP explícito e `detail` string."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        self.detail = detail
        self.default_code = "error"


def _primeiro_detail(detail: Any) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail:
        return _primeiro_detail(detail[0])
    if isinstance(detail, dict):
        for valor in detail.values():
            return _primeiro_detail(valor)
        return "Dados inválidos."
    return str(detail) if detail else "Dados inválidos."


def api_exception_handler(exc: Exception, context: dict) -> Response | None:
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return Response(
            {"detail": "Não autorizado"},
            status=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if isinstance(exc, APIError):
        return Response({"detail": str(exc.detail)}, status=exc.status_code)

    if isinstance(exc, ValidationError):
        return Response(
            {"detail": _primeiro_detail(exc.detail)},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    response = exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data.get("detail") if isinstance(response.data, dict) else response.data
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return Response(
            {"detail": "Não autorizado"},
            status=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )
    if isinstance(detail, str):
        response.data = {"detail": detail}
    elif response.data is not None and "detail" not in response.data:
        response.data = {"detail": _primeiro_detail(response.data)}
    return response
