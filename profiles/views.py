from django.views.generic import DetailView, UpdateView
from django.db.models import QuerySet
from django.urls import reverse_lazy

from config.utils import get_resized_image_url
from accounts.models import CustomUser
from tweets.models import Tweet
from .forms import ProfileEditForm


class TweetListMixin:
    """ツイート一覧を取得し、画像のリサイズを設定する共通処理"""

    def get_tweet_list(
        self, tweet_queryset: QuerySet, order_by: str = "-created_at"
    ) -> QuerySet:
        """対象のクエリセットに並び替えオプション追加、リサイズ済みの画像URLを付与する"""
        tweet_queryset = tweet_queryset.order_by(order_by)
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
        context["tweet_list"] = self.get_tweet_list(current_user.tweets)
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
        liked_tweet_ids = current_user.likes.values_list("tweet_id", flat=True)
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
        retweeted_tweet_ids = current_user.retweets.values_list("tweet_id", flat=True)
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
        commented_tweet_ids = current_user.comments.values_list("tweet_id", flat=True)
        # コメントしたツイートを取得
        context["tweet_list"] = self.get_tweet_list(
            Tweet.objects.filter(id__in=commented_tweet_ids).select_related("user")
        )
        return context


class ProfileEditView(UpdateView):
    """プロフィール編集用のビュー"""

    model = CustomUser
    form_class = ProfileEditForm
    template_name = "profiles/profile_edit.html"
    context_object_name = "user_profile"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_success_url(self):
        # get_success_urlをオーバーライドして動的なパスに遷移させる
        return reverse_lazy(
            "profiles:my_tweet_list", kwargs={"username": self.kwargs["username"]}
        )
