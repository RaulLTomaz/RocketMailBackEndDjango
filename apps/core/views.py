from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthzView(APIView):
    """Health check do Render — sem auth e sem bater no banco."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok"})
