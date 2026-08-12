from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.comentarios.serializers import ComentarioCreateSerializer, ComentarioResponseSerializer
from apps.comentarios import services
from apps.core.constants import LIST_LIMIT_DEFAULT, LIST_LIMIT_MAX, LIST_LIMIT_MIN, LIST_OFFSET_MIN
from apps.core.query import query_int


class ComentarioPorPostView(APIView):
    """GET lista / POST cria comentários de um post."""

    permission_classes = [IsAuthenticated]

    def get(self, request, post_id: int):
        limit = query_int(
            request, "limit", LIST_LIMIT_DEFAULT, minimo=LIST_LIMIT_MIN, maximo=LIST_LIMIT_MAX
        )
        offset = query_int(request, "offset", 0, minimo=LIST_OFFSET_MIN)
        comentarios = services.listar_comentarios(
            post_id=post_id, limit=limit, offset=offset
        )
        return Response(ComentarioResponseSerializer(comentarios, many=True).data)

    def post(self, request, post_id: int):
        serializer = ComentarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comentario = services.criar_comentario(
            texto=serializer.validated_data["comentario"],
            post_id=post_id,
            usuario=request.user,
        )
        return Response(
            ComentarioResponseSerializer(comentario).data,
            status=status.HTTP_201_CREATED,
        )


class ComentarioDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comentario_id: int):
        return Response(
            services.deletar_comentario(
                comentario_id=comentario_id,
                usuario_id=request.user.id,
            )
        )
