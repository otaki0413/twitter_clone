from django.urls import path

from .views import (
    MyTweetListView,
    LikedTweetListView,
    RetweetedTweetListView,
    CommentedTweetListView,
)

app_name = "profiles"
urlpatterns = [
    path("<str:username>/", MyTweetListView.as_view(), name="my_tweet_list"),
    path(
        "<str:username>/likes/", LikedTweetListView.as_view(), name="liked_tweet_list"
    ),
    path(
        "<str:username>/retweets/",
        RetweetedTweetListView.as_view(),
        name="retweeted_tweet_list",
    ),
    path(
        "<str:username>/comments/",
        CommentedTweetListView.as_view(),
        name="commented_tweet_list",
    ),
]
