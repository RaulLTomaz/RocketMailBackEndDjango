from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import APIError
from apps.seguir import services
from apps.usuarios.serializers import UsuarioOutSerializer


def _seguido_id(request) -> int:
    bruto = request.query_params.get("seguido_id")
    if bruto is None or bruto == "":
        raise APIError("Parâmetro seguido_id é obrigatório.", status_code=422)
    try:
        return int(bruto)
    except (TypeError, ValueError) as exc:
        raise APIError("Parâmetro seguido_id inválido.", status_code=422) from exc


class SeguidosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuarios = services.listar_seguidos(seguidor_id=request.user.id)
        return Response(UsuarioOutSerializer(usuarios, many=True).data)


class SeguidoresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuarios = services.listar_seguidores(seguido_id=request.user.id)
        return Response(UsuarioOutSerializer(usuarios, many=True).data)


class SeguirView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            services.seguir_usuario(
                seguidor_id=request.user.id,
                seguido_id=_seguido_id(request),
            )
        )

    def delete(self, request):
        return Response(
            services.deixar_de_seguir(
                seguidor_id=request.user.id,
                seguido_id=_seguido_id(request),
            )
        )
