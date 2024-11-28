from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from config.utils import get_resized_image_url


from .models import Tweet
from accounts.models import FollowRelation


class TimelineView(LoginRequiredMixin, ListView):
    """おすすめのツイート一覧ビュー"""

    model = Tweet
    template_name = "tweets/index.html"
    context_object_name = "tweet_list"
    queryset = Tweet.objects.prefetch_related("user")
    ordering = "-created_at"
    paginate_by = 2
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 各ツイートに対してリサイズ済みの画像URLを設定
        for tweet in context["tweet_list"]:
            if tweet.image:
                tweet.resized_image_url = get_resized_image_url(
                    tweet.image.url, 150, 150
                )
        return context

    # def get(self, *args, **kwargs):
    #     # セッションが存在しない場合、ログイン画面へリダイレクト
    #     if self.request.session.session_key is None:
    #         return redirect("accounts:login")
    #     return super().get(*args, **kwargs)


class FollowingTweetListView(LoginRequiredMixin, ListView):
    """フォロー中のツイート一覧ビュー"""

    model = Tweet
    template_name = "tweets/following.html"
    context_object_name = "tweet_list"
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        # ログインユーザ取得
        user = self.request.user
        # フォロー中のユーザIDを取得するクエリセット作成
        inner_qs = FollowRelation.objects.filter(follower_id=user.id).values_list(
            "followee_id", flat=True
        )
        # フォロー中のユーザのツイートを取得するクエリセットを返す
        return Tweet.objects.filter(user_id__in=inner_qs).prefetch_related("user")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 各ツイートに対してリサイズ済みの画像URLを設定
        for tweet in context["tweet_list"]:
            if tweet.image:
                tweet.resized_image_url = get_resized_image_url(
                    tweet.image.url, 150, 150
                )
        return context
