from django.urls import path

from . import views

app_name = "tweets"
urlpatterns = [
    path("", views.TimelineView.as_view(), name="timeline"),
    path(
        "following/",
        views.FollowingTweetListView.as_view(),
        name="following",
    ),
    path("create/", views.TweetCreateView.as_view(), name="tweet_create"),
    path("tweets/<int:pk>/", views.TweetDetailView.as_view(), name="tweet_detail"),
    path(
        "tweets/<int:pk>/comment/",
        views.CommentCreateView.as_view(),
        name="comment_create",
    ),
]
