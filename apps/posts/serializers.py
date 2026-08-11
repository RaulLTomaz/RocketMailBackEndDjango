from rest_framework import serializers

from apps.core.constants import POST_MAX_LENGTH
from apps.posts.models import Post
from apps.usuarios.serializers import UsuarioSimplesSerializer


class PostCreateSerializer(serializers.Serializer):
    post = serializers.CharField(min_length=1, max_length=POST_MAX_LENGTH)

    def validate_post(self, value: str) -> str:
        texto = value.strip()
        if not texto:
            raise serializers.ValidationError(
                "O conteúdo do post não pode ser vazio ou apenas espaços."
            )
        return texto


class PostResponseSerializer(serializers.ModelSerializer):
    usuario = UsuarioSimplesSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "post", "data_criacao", "usuario")
