from rest_framework import serializers

from apps.core.constants import COMENTARIO_MAX_LENGTH
from apps.comentarios.models import Comentario
from apps.usuarios.serializers import UsuarioSimplesSerializer


class ComentarioCreateSerializer(serializers.Serializer):
    comentario = serializers.CharField(min_length=1, max_length=COMENTARIO_MAX_LENGTH)

    def validate_comentario(self, value: str) -> str:
        texto = value.strip()
        if not texto:
            raise serializers.ValidationError(
                "O comentário não pode ser vazio ou apenas espaços."
            )
        return texto


class ComentarioResponseSerializer(serializers.ModelSerializer):
    usuario = UsuarioSimplesSerializer(read_only=True)

    class Meta:
        model = Comentario
        fields = ("id", "comentario", "data_criacao", "usuario", "post_id")
