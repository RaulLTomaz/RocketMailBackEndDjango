from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from apps.core.views import HealthzView

urlpatterns = [
    path("", HealthzView.as_view(), name="root"),
    path("healthz", HealthzView.as_view(), name="healthz"),
    path("healthz/", HealthzView.as_view(), name="healthz-slash"),
    path("", include("apps.usuarios.urls")),
    path("", include("apps.posts.urls")),
    path("", include("apps.seguir.urls")),
    path("", include("apps.likes.urls")),
]

# Disco local só em dev/test — em produção as fotos vão para o Cloudinary.
if settings.PYTHON_ENV not in ("production", "prod"):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
