from django.urls import path

from apps.seguir.views import SeguidoresView, SeguidosView, SeguirView

urlpatterns = [
    path("seguir/seguidos", SeguidosView.as_view(), name="seguir-seguidos"),
    path("seguir/seguidos/", SeguidosView.as_view(), name="seguir-seguidos-slash"),
    path("seguir/seguidores", SeguidoresView.as_view(), name="seguir-seguidores"),
    path("seguir/seguidores/", SeguidoresView.as_view(), name="seguir-seguidores-slash"),
    path("seguir", SeguirView.as_view(), name="seguir"),
    path("seguir/", SeguirView.as_view(), name="seguir-slash"),
]
