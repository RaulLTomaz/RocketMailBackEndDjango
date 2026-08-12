from django.urls import path

from apps.comentarios.views import ComentarioDeleteView, ComentarioPorPostView

urlpatterns = [
    # Rotas estáticas/aninhadas antes de <comentario_id>
    path(
        "comentario/post/<int:post_id>",
        ComentarioPorPostView.as_view(),
        name="comentario-por-post",
    ),
    path(
        "comentario/post/<int:post_id>/",
        ComentarioPorPostView.as_view(),
        name="comentario-por-post-slash",
    ),
    path(
        "comentario/<int:comentario_id>",
        ComentarioDeleteView.as_view(),
        name="comentario-delete",
    ),
    path(
        "comentario/<int:comentario_id>/",
        ComentarioDeleteView.as_view(),
        name="comentario-delete-slash",
    ),
]
