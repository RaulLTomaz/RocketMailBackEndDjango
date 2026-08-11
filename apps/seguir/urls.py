from django.urls import path

from apps.seguir.views import SeguidosView, SeguirView

urlpatterns = [
    path("seguir/seguidos", SeguidosView.as_view(), name="seguir-seguidos"),
    path("seguir/seguidos/", SeguidosView.as_view(), name="seguir-seguidos-slash"),
    path("seguir", SeguirView.as_view(), name="seguir"),
    path("seguir/", SeguirView.as_view(), name="seguir-slash"),
]
