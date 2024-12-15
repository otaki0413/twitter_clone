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
    path("tweets/<int:pk>/", views.TweetDetailView.as_view(), name="tweet_detail"),
]
