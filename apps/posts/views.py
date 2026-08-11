from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import LIST_LIMIT_DEFAULT, LIST_LIMIT_MAX, LIST_LIMIT_MIN, LIST_OFFSET_MIN
from apps.core.exceptions import APIError
from apps.core.query import query_int
from apps.posts.serializers import PostCreateSerializer, PostResponseSerializer
from apps.posts.services import criar_post, deletar_post, listar_feed, listar_posts


class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = criar_post(texto=serializer.validated_data["post"], usuario=request.user)
        return Response(PostResponseSerializer(post).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        limit = query_int(
            request, "limit", LIST_LIMIT_DEFAULT, minimo=LIST_LIMIT_MIN, maximo=LIST_LIMIT_MAX
        )
        offset = query_int(request, "offset", 0, minimo=LIST_OFFSET_MIN)
        sort = request.query_params.get("sort", "-data")
        if sort not in ("-data", "data"):
            raise APIError("Parâmetro sort inválido.", status_code=422)
        posts = listar_posts(limit=limit, offset=offset, sort=sort)
        return Response(PostResponseSerializer(posts, many=True).data)


class PostFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = query_int(
            request, "limit", LIST_LIMIT_DEFAULT, minimo=LIST_LIMIT_MIN, maximo=LIST_LIMIT_MAX
        )
        offset = query_int(request, "offset", 0, minimo=LIST_OFFSET_MIN)
        posts = listar_feed(viewer_id=request.user.id, limit=limit, offset=offset)
        return Response(PostResponseSerializer(posts, many=True).data)


class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id: int):
        return Response(deletar_post(post_id=post_id, usuario_id=request.user.id))
