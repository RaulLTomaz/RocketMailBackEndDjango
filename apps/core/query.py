"""Parsing de query params numéricos alinhado ao FastAPI (422 fora da faixa)."""

from __future__ import annotations

from rest_framework.request import Request

from apps.core.exceptions import APIError


def query_int(
    request: Request,
    nome: str,
    default: int,
    *,
    minimo: int | None = None,
    maximo: int | None = None,
) -> int:
    bruto = request.query_params.get(nome)
    if bruto is None or bruto == "":
        return default
    try:
        valor = int(bruto)
    except (TypeError, ValueError) as exc:
        raise APIError(f"Parâmetro {nome} inválido.", status_code=422) from exc
    if minimo is not None and valor < minimo:
        raise APIError(f"Parâmetro {nome} deve ser ≥ {minimo}.", status_code=422)
    if maximo is not None and valor > maximo:
        raise APIError(f"Parâmetro {nome} deve ser ≤ {maximo}.", status_code=422)
    return valor
