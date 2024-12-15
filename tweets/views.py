from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import QuerySet
from django.core.paginator import Paginator

from config.utils import get_resized_image_url

from .models import Tweet
from accounts.models import FollowRelation
from .forms import TweetCreateForm


class TimelineView(LoginRequiredMixin, ListView):
    """おすすめのツイート一覧ビュー"""

    model = Tweet
    template_name = "tweets/index.html"
    queryset = Tweet.objects.prefetch_related("user")
    ordering = "-created_at"
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        queryset = self.get_queryset()
        # ページネーション、画像リサイズを適用したツイートリストやツイート投稿フォームを含むコンテキストに更新
        context.update(create_tweet_context_with_form(self.request, queryset))

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
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        # ログインユーザ取得
        user = self.request.user
        # フォロー中のユーザIDを取得するクエリセット作成
        inner_qs = FollowRelation.objects.filter(follower_id=user.id).values_list(
            "followee_id", flat=True
        )
        # フォロー中のユーザのツイートを取得するクエリセットを返す
        return (
            Tweet.objects.filter(user_id__in=inner_qs)
            .prefetch_related("user")
            .order_by("-created_at")
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        queryset = self.get_queryset()
        context.update(create_tweet_context_with_form(self.request, queryset))
        return context


class TweetCreateView(CreateView):
    """ツイート投稿用のビュー"""

    model = Tweet
    form_class = TweetCreateForm
    template_name = "tweets/_tweetform.html"
    success_url = reverse_lazy("tweets:timeline")

    def get(self, request, *args, **kwargs):
        # GETリクエスト時には一覧へリダイレクトさせる
        return redirect("tweets:timeline")

    def form_valid(self, form):
        # フォームからインスタンス取得（※まだ保存しない）
        tweet = form.save(commit=False)
        # ユーザーの設定
        tweet.user = self.request.user
        tweet.save()
        messages.success(
            self.request,
            "ツイートの投稿に成功しました。",
            extra_tags="success",
        )
        # 親クラスの保存処理を実行
        return super().form_valid(form)

    def form_invalid(self, form):
        # ツイート一覧のクエリセット
        tweet_queryset = Tweet.objects.prefetch_related("user").order_by("-created_at")
        # バリデーションエラー時の再描画用のコンテキスト生成
        context = create_tweet_context_with_form(self.request, tweet_queryset)
        # フォームのエラー情報を設定
        context["form"] = form
        # タイムラインページ再描画
        return render(self.request, "tweets/index.html", context)


def create_tweet_context_with_form(request, tweet_queryset: QuerySet = None):
    """ページネーションや画像リサイズを適用したツイートリストとツイート投稿フォームを含むコンテキストを生成する処理"""

    # コンテキスト初期化
    context = {}

    # ツイート投稿フォームのコンテキスト設定
    context["form"] = TweetCreateForm

    if tweet_queryset:
        # ページネーター設定（とりあえず5件表示）
        paginator = Paginator(tweet_queryset, 5)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # 各ツイートに対して、リサイズ適用した画像URLを設定
        for tweet in page_obj.object_list:
            if tweet.image:
                tweet.resized_image_url = get_resized_image_url(
                    tweet.image.url, 150, 150
                )

        # ページネーション済みデータをコンテキスト設定
        context["page_obj"] = page_obj
        context["tweet_list"] = page_obj.object_list

    return context
