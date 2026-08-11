from django.urls import path

from apps.posts.views import PostDeleteView, PostFeedView, PostListCreateView

urlpatterns = [
    path("post/feed", PostFeedView.as_view(), name="post-feed"),
    path("post/feed/", PostFeedView.as_view(), name="post-feed-slash"),
    path("post/<int:post_id>", PostDeleteView.as_view(), name="post-delete"),
    path("post/<int:post_id>/", PostDeleteView.as_view(), name="post-delete-slash"),
    path("post", PostListCreateView.as_view(), name="post-list-create"),
    path("post/", PostListCreateView.as_view(), name="post-list-create-slash"),
]
