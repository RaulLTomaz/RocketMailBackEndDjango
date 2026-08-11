from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import LIKE_BATCH_MAX, LIKE_BATCH_MIN
from apps.core.exceptions import APIError
from apps.likes import services


class LikeBatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        brutos = request.query_params.getlist("post_ids")
        if len(brutos) < LIKE_BATCH_MIN:
            raise APIError("Parâmetro post_ids é obrigatório.", status_code=422)
        if len(brutos) > LIKE_BATCH_MAX:
            raise APIError(
                f"No máximo {LIKE_BATCH_MAX} post_ids por requisição.",
                status_code=422,
            )
        try:
            post_ids = [int(x) for x in brutos]
        except (TypeError, ValueError) as exc:
            raise APIError("post_ids deve conter inteiros.", status_code=422) from exc
        return Response(
            services.batch_resumo_like(usuario_id=request.user.id, post_ids=post_ids)
        )


class LikePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id: int):
        return Response(services.dar_like(usuario_id=request.user.id, post_id=post_id))

    def delete(self, request, post_id: int):
        return Response(services.remover_like(usuario_id=request.user.id, post_id=post_id))

    def get(self, request, post_id: int):
        return Response(services.resumo_like(usuario_id=request.user.id, post_id=post_id))
