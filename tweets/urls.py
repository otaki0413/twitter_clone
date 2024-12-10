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
]
