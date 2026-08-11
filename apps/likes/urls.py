from django.urls import path

from apps.likes.views import LikeBatchView, LikePostView

urlpatterns = [
    path("like/batch", LikeBatchView.as_view(), name="like-batch"),
    path("like/batch/", LikeBatchView.as_view(), name="like-batch-slash"),
    path("like/<int:post_id>", LikePostView.as_view(), name="like-post"),
    path("like/<int:post_id>/", LikePostView.as_view(), name="like-post-slash"),
]
