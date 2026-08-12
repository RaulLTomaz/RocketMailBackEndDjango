from django.urls import path

from apps.usuarios.views import (
    CriarUsuarioView,
    LoginView,
    MeFotoView,
    MeView,
    SearchUsuarioView,
    UsuarioDetalheView,
    UsuarioPostsView,
    UsuarioStatsView,
)

urlpatterns = [
    # Cada rota com e sem barra final: APPEND_SLASH=False (front mistura os dois).
    path("usuario/login", LoginView.as_view(), name="usuario-login"),
    path("usuario/login/", LoginView.as_view(), name="usuario-login-slash"),
    path("usuario/me/foto", MeFotoView.as_view(), name="usuario-me-foto"),
    path("usuario/me/foto/", MeFotoView.as_view(), name="usuario-me-foto-slash"),
    path("usuario/me", MeView.as_view(), name="usuario-me"),
    path("usuario/me/", MeView.as_view(), name="usuario-me-slash"),
    path("usuario/search", SearchUsuarioView.as_view(), name="usuario-search"),
    path("usuario/search/", SearchUsuarioView.as_view(), name="usuario-search-slash"),
    path("usuario/<int:usuario_id>/stats", UsuarioStatsView.as_view(), name="usuario-stats"),
    path("usuario/<int:usuario_id>/stats/", UsuarioStatsView.as_view(), name="usuario-stats-slash"),
    path("usuario/<int:usuario_id>/posts", UsuarioPostsView.as_view(), name="usuario-posts"),
    path("usuario/<int:usuario_id>/posts/", UsuarioPostsView.as_view(), name="usuario-posts-slash"),
    path("usuario/<int:usuario_id>", UsuarioDetalheView.as_view(), name="usuario-detalhe"),
    path("usuario/<int:usuario_id>/", UsuarioDetalheView.as_view(), name="usuario-detalhe-slash"),
    path("usuario", CriarUsuarioView.as_view(), name="usuario-criar"),
    path("usuario/", CriarUsuarioView.as_view(), name="usuario-criar-slash"),
]
