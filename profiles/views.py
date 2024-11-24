from django.views.generic import DetailView

from accounts.models import CustomUser
from tweets.models import Tweet, Like, Retweet, Comment


class MyTweetListView(DetailView):
    """自身のツイート一覧ビュー（プロフィール詳細ページのデフォルトビュー）"""

    model = CustomUser
    template_name = "profiles/my_tweets.html"
    context_object_name = "user_profile"
    slug_field = "username"  # モデルのフィールド名
    slug_url_kwarg = "username"  # urls.pyでのキーワード名

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 現在のユーザー取得
        current_user = self.get_object()
        # 投稿したツイートを取得
        context["tweet_list"] = Tweet.objects.filter(user=current_user).select_related(
            "user"
        )
        return context


class LikedTweetListView(DetailView):
    """いいねしたツイート一覧ビュー"""

    model = CustomUser
    template_name = "profiles/liked_tweets.html"
    context_object_name = "user_profile"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 現在のユーザー取得
        current_user = self.get_object()
        # いいねしたツイートIDを取得するクエリセット作成
        liked_tweet_ids = Like.objects.filter(user=current_user).values_list(
            "tweet_id", flat=True
        )
        # いいねしたツイートを取得
        context["tweet_list"] = Tweet.objects.filter(
            id__in=liked_tweet_ids
        ).select_related("user")
        return context


class RetweetedTweetListView(DetailView):
    """リツイートしたツイート一覧ビュー"""

    model = CustomUser
    template_name = "profiles/retweeted_tweets.html"
    context_object_name = "user_profile"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 現在のユーザー取得
        current_user = self.get_object()
        # リツイートしたツイートIDを取得するクエリセット作成
        retweeted_tweet_ids = Retweet.objects.filter(user=current_user).values_list(
            "tweet_id", flat=True
        )
        # リツイートしたツイートを取得
        context["tweet_list"] = Tweet.objects.filter(
            id__in=retweeted_tweet_ids
        ).select_related("user")
        return context


class CommentedTweetListView(DetailView):
    """コメントしたツイート一覧ビュー"""

    model = CustomUser
    template_name = "profiles/commented_tweets.html"
    context_object_name = "user_profile"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 現在のユーザー取得
        current_user = self.get_object()
        # コメントしたツイートIDを取得するクエリセット作成
        commented_tweet_ids = Comment.objects.filter(user=current_user).values_list(
            "tweet_id", flat=True
        )
        # コメントしたツイートを取得
        context["tweet_list"] = Tweet.objects.filter(
            id__in=commented_tweet_ids
        ).select_related("user")
        return context
