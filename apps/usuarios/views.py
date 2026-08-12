from __future__ import annotations

from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import (
    LIST_LIMIT_DEFAULT,
    LIST_LIMIT_MAX,
    LIST_LIMIT_MIN,
    LIST_OFFSET_MIN,
    POSTS_PER_USER_DEFAULT,
    POSTS_PER_USER_MAX,
    POSTS_PER_USER_MIN,
    SEARCH_LIMIT_DEFAULT,
    SEARCH_LIMIT_MAX,
    SEARCH_LIMIT_MIN,
)
from apps.core.exceptions import APIError
from apps.core.query import query_int
from apps.core.storage import (
    remover_arquivo_local_se_houver,
    remover_foto_cloudinary_se_houver,
    salvar_foto_perfil,
)
from apps.core.throttles import LoginRateThrottle, RegistroRateThrottle
from apps.posts.serializers import PostResponseSerializer
from apps.posts.services import listar_posts_do_usuario
from apps.usuarios import services
from apps.usuarios.serializers import (
    UsuarioCreateSerializer,
    UsuarioOutSerializer,
    UsuarioUpdateSerializer,
)


class CriarUsuarioView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegistroRateThrottle]

    def post(self, request):
        serializer = UsuarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = services.criar_usuario(**serializer.validated_data)
        return Response(UsuarioOutSerializer(usuario).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """OAuth2 password grant: form `username` (e-mail) + `password` — contrato do front."""

    permission_classes = [AllowAny]
    parser_classes = [FormParser, MultiPartParser]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        username = request.data.get("username") or ""
        password = request.data.get("password") or ""
        return Response(services.autenticar_usuario(username, password))


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = services.buscar_por_id(request.user.id)
        return Response(UsuarioOutSerializer(usuario).data)

    def patch(self, request):
        serializer = UsuarioUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        usuario = services.atualizar_usuario(request.user, dict(serializer.validated_data))
        return Response(UsuarioOutSerializer(usuario).data)

    def delete(self, request):
        return Response(services.deletar_usuario(request.user))


class MeFotoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        arquivo = request.FILES.get("file")
        if arquivo is None:
            raise APIError("Arquivo inválido: nome ausente.", status_code=400)
        usuario = services.buscar_por_id(request.user.id)
        try:
            foto_url = salvar_foto_perfil(arquivo, usuario.id)
        except APIError:
            raise
        except Exception:
            raise APIError("Falha ao processar upload da foto.", status_code=502)

        antiga = usuario.foto_url
        if antiga and antiga != foto_url:
            remover_arquivo_local_se_houver(antiga)
        atualizado = services.atualizar_foto_url(usuario, foto_url)
        return Response(UsuarioOutSerializer(atualizado).data)

    def delete(self, request):
        usuario = services.buscar_por_id(request.user.id)
        remover_arquivo_local_se_houver(usuario.foto_url)
        remover_foto_cloudinary_se_houver(usuario.id)
        atualizado = services.atualizar_foto_url(usuario, None)
        return Response(UsuarioOutSerializer(atualizado).data)


class SearchUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get("q")
        if q is None:
            raise APIError("Parâmetro q é obrigatório.", status_code=422)
        limit = query_int(
            request, "limit", SEARCH_LIMIT_DEFAULT, minimo=SEARCH_LIMIT_MIN, maximo=SEARCH_LIMIT_MAX
        )
        posts_per_user = query_int(
            request,
            "posts_per_user",
            POSTS_PER_USER_DEFAULT,
            minimo=POSTS_PER_USER_MIN,
            maximo=POSTS_PER_USER_MAX,
        )
        hits = services.buscar_usuarios_com_posts(q, limit, posts_per_user)
        payload = [
            {
                "usuario": UsuarioOutSerializer(hit["usuario"]).data,
                "posts": PostResponseSerializer(hit["posts"], many=True).data,
            }
            for hit in hits
        ]
        return Response(payload)


class UsuarioDetalheView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, usuario_id: int):
        usuario = services.buscar_por_id(usuario_id)
        return Response(UsuarioOutSerializer(usuario).data)


class UsuarioStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, usuario_id: int):
        resultado = services.stats_usuario(usuario_id)
        return Response(
            {
                "usuario": UsuarioOutSerializer(resultado["usuario"]).data,
                "stats": resultado["stats"],
            }
        )


class UsuarioPostsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, usuario_id: int):
        limit = query_int(
            request, "limit", LIST_LIMIT_DEFAULT, minimo=LIST_LIMIT_MIN, maximo=LIST_LIMIT_MAX
        )
        offset = query_int(request, "offset", 0, minimo=LIST_OFFSET_MIN)
        posts = listar_posts_do_usuario(usuario_id=usuario_id, limit=limit, offset=offset)
        return Response(PostResponseSerializer(posts, many=True).data)
