from django.views.generic import DetailView
from django.db.models import QuerySet

from config.utils import get_resized_image_url
from accounts.models import CustomUser
from tweets.models import Tweet, Like, Retweet, Comment


class TweetListMixin:
    """ツイート一覧を取得し、画像のリサイズを設定する共通処理"""

    def get_tweet_list(self, tweet_queryset: QuerySet) -> QuerySet:
        """対象のクエリセットにリサイズ済みの画像URLを付与する"""
        for tweet in tweet_queryset:
            if tweet.image:
                tweet.resized_image_url = get_resized_image_url(
                    tweet.image.url, 150, 150
                )
        return tweet_queryset


class MyTweetListView(DetailView, TweetListMixin):
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
        context["tweet_list"] = self.get_tweet_list(
            Tweet.objects.filter(user=current_user).select_related("user")
        )
        return context


class LikedTweetListView(DetailView, TweetListMixin):
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
        context["tweet_list"] = self.get_tweet_list(
            Tweet.objects.filter(id__in=liked_tweet_ids).select_related("user")
        )
        return context


class RetweetedTweetListView(DetailView, TweetListMixin):
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
        context["tweet_list"] = self.get_tweet_list(
            Tweet.objects.filter(id__in=retweeted_tweet_ids).select_related("user")
        )
        return context


class CommentedTweetListView(DetailView, TweetListMixin):
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
        context["tweet_list"] = self.get_tweet_list(
            Tweet.objects.filter(id__in=commented_tweet_ids).select_related("user")
        )
        return context
