"""Política de senha espelhada em `src/utils/password.ts` do front."""

from __future__ import annotations

import re

from rest_framework import serializers

from apps.core.constants import SENHA_MAX_LENGTH, SENHA_MIN_LENGTH

_SIMBOLO_RE = re.compile(r"[^A-Za-z0-9]")


def validar_politica_senha(senha: str) -> str:
    faltando: list[str] = []
    if len(senha) < SENHA_MIN_LENGTH:
        faltando.append(f"pelo menos {SENHA_MIN_LENGTH} caracteres")
    if not re.search(r"[A-Z]", senha):
        faltando.append("uma letra maiúscula")
    if not re.search(r"[0-9]", senha):
        faltando.append("um número")
    if not _SIMBOLO_RE.search(senha):
        faltando.append("um símbolo (ex.: !@#$%)")
    if faltando:
        raise serializers.ValidationError(
            f"A senha precisa ter {', '.join(faltando)}."
        )
    if len(senha) > SENHA_MAX_LENGTH:
        raise serializers.ValidationError(
            f"A senha deve ter no máximo {SENHA_MAX_LENGTH} caracteres."
        )
    return senha
