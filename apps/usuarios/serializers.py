from __future__ import annotations

from rest_framework import serializers

from apps.core.constants import (
    EMAIL_MAX_LENGTH,
    NOME_MAX_LENGTH,
    SENHA_MAX_LENGTH,
)
from apps.usuarios.models import Usuario
from apps.usuarios.password import validar_politica_senha


class UsuarioCreateSerializer(serializers.Serializer):
    nome = serializers.CharField(min_length=1, max_length=NOME_MAX_LENGTH, trim_whitespace=True)
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)
    senha = serializers.CharField(
        max_length=SENHA_MAX_LENGTH,
        write_only=True,
        trim_whitespace=False,
    )

    def validate_nome(self, value: str) -> str:
        nome = value.strip()
        if not nome:
            raise serializers.ValidationError("O nome não pode ser vazio.")
        return nome

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_senha(self, value: str) -> str:
        return validar_politica_senha(value)


class UsuarioUpdateSerializer(serializers.Serializer):
    nome = serializers.CharField(
        min_length=1, max_length=NOME_MAX_LENGTH, required=False, trim_whitespace=True
    )
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH, required=False)
    senha = serializers.CharField(
        max_length=SENHA_MAX_LENGTH,
        required=False,
        write_only=True,
        trim_whitespace=False,
    )
    foto_url = serializers.CharField(required=False, allow_null=True, allow_blank=False)

    def validate_senha(self, value: str) -> str:
        return validar_politica_senha(value)

    def validate_nome(self, value: str) -> str:
        nome = value.strip()
        if not nome:
            raise serializers.ValidationError("O nome não pode ser vazio.")
        return nome

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_foto_url(self, value: str | None) -> str | None:
        if value is None:
            return None
        url = str(value).strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            raise serializers.ValidationError(
                "foto_url deve ser uma URL absoluta (http ou https)."
            )
        return url


class UsuarioOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ("id", "nome", "email", "foto_url")


class UsuarioSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ("id", "nome", "foto_url")
