from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import QuerySet
from django.core.paginator import Paginator

from config.utils import get_resized_image_url

from .models import Tweet, Comment, Like, Retweet
from accounts.models import FollowRelation
from .forms import TweetCreateForm, CommentCreateForm


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

        # ログインユーザがいいねしているツイートID取得
        liked_tweet_ids = request.user.likes.values_list("tweet_id", flat=True)
        # ログインユーザがリツイートしているツイートID取得
        retweeted_tweet_ids = request.user.retweets.values_list("tweet_id", flat=True)

        for tweet in page_obj.object_list:
            # 画像リサイズ適用
            if tweet.image:
                tweet.resized_image_url = get_resized_image_url(
                    tweet.image.url, 150, 150
                )
            # ログインユーザがいいねしているか設定
            tweet.is_liked_by_user = tweet.id in liked_tweet_ids
            # ログインユーザがリツイートしているか設定
            tweet.is_retweeted_by_user = tweet.id in retweeted_tweet_ids

        # ページネーション済みデータをコンテキスト設定
        context["page_obj"] = page_obj
        context["tweet_list"] = page_obj.object_list

    return context


class TimelineView(LoginRequiredMixin, ListView):
    """おすすめのツイート一覧ビュー"""

    model = Tweet
    template_name = "tweets/index.html"
    queryset = (
        Tweet.objects.select_related("user")
        .prefetch_related("likes")
        .prefetch_related("retweets")
    )
    ordering = "-created_at"
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        queryset = self.get_queryset()
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
            .select_related("user")
            .prefetch_related("likes")
            .prefetch_related("retweets")
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
        tweet_queryset = (
            Tweet.objects.select_related("user")
            .order_by("-created_at")
            .prefetch_related("likes")
            .prefetch_related("retweets")
        )
        # バリデーションエラー時の再描画用のコンテキスト生成
        context = create_tweet_context_with_form(self.request, tweet_queryset)
        # フォームのエラー情報を設定
        context["form"] = form
        # タイムラインページ再描画
        return render(self.request, "tweets/index.html", context)


class TweetDetailView(DetailView):
    """ツイート詳細ビュー"""

    model = Tweet
    template_name = "tweets/detail.html"
    queryset = (
        Tweet.objects.select_related("user")
        .prefetch_related("comments__user")
        .prefetch_related("likes")
        .prefetch_related("retweets")
    )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tweet = self.object
        # 画像リサイズ適用
        if tweet.image:
            tweet.resized_image_url = get_resized_image_url(tweet.image.url, 300, 300)
        # ログインユーザがいいねしているか設定
        tweet.is_liked_by_user = tweet.is_liked_by_user(self.request.user)
        # ログインユーザがリツイートしているか設定
        tweet.is_retweeted_by_user = tweet.is_retweeted_by_user(self.request.user)
        context["tweet"] = tweet
        context["form"] = CommentCreateForm()
        return context


class CommentCreateView(CreateView):
    """コメント投稿ビュー"""

    model = Comment
    form_class = CommentCreateForm
    template_name = "tweets/detail.html"

    def get_success_url(self):
        # ツイート詳細ページへリダイレクト
        return reverse_lazy("tweets:tweet_detail", kwargs={"pk": self.kwargs["pk"]})

    def form_valid(self, form):
        # フォームからインスタンス取得（※まだ保存しない）
        comment = form.save(commit=False)
        # ユーザーの設定
        comment.user = self.request.user
        # ツイートの設定
        comment.tweet = Tweet.objects.get(pk=self.kwargs["pk"])
        comment.save()
        messages.success(
            self.request,
            "コメントの投稿に成功しました。",
            extra_tags="success",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        # ツイート詳細のクエリセット
        tweet = (
            Tweet.objects.select_related("user")
            .prefetch_related("comments__user")
            .get(pk=self.kwargs["pk"])
        )
        # 画像リサイズ適用
        if tweet.image:
            tweet.resized_image_url = get_resized_image_url(tweet.image.url, 300, 300)
        # ログインユーザがいいねしているか設定
        tweet.is_liked_by_user = tweet.is_liked_by_user(self.request.user)
        # ログインユーザがリツイートしているか設定
        tweet.is_retweeted_by_user = tweet.is_retweeted_by_user(self.request.user)

        # バリデーションエラー時の再描画用のコンテキスト生成
        context = {
            "tweet": tweet,
            "form": form,
        }
        # ツイート詳細ページ再描画
        return render(self.request, "tweets/detail.html", context)


class LikeToggleView(LoginRequiredMixin, View):
    """いいね・いいね解除を切り替えるビュー"""

    def post(self, request, *args, **kwargs):
        # リクエストをもとにツイート情報を取得
        tweet = Tweet.objects.get(pk=request.POST.get("tweet_id"))
        # ログインユーザを取得
        user = request.user

        # 対象のいいね情報を取得
        try:
            target_like = Like.objects.get(user=user, tweet=tweet)
        except Like.DoesNotExist:
            target_like = None

        # いいねの切り替え処理
        if target_like is None:
            # いいね追加
            tweet.likes.create(user=user)
            messages.success(
                self.request,
                "いいねをしました。",
                extra_tags="success",
            )
        else:
            # いいね削除
            target_like.delete()
            messages.success(
                self.request,
                "いいねを解除しました。",
                extra_tags="success",
            )

        # 直前のページにリダイレクトする
        return redirect(request.META.get("HTTP_REFERER", "tweets:timeline"))


class RetweetToggleView(LoginRequiredMixin, View):
    """リツイート・リツイート解除を切り替えるビュー"""

    def post(self, request, *args, **kwargs):
        # リクエストをもとにツイート情報を取得
        tweet = Tweet.objects.get(pk=request.POST.get("tweet_id"))
        # ログインユーザを取得
        user = request.user

        # 対象のリツイート情報を取得
        try:
            target_retweet = tweet.retweets.get(user=user)
        except Retweet.DoesNotExist:
            target_retweet = None

        # リツイートの切り替え処理
        if target_retweet is None:
            # リツイート
            tweet.retweets.create(user=user)
            messages.success(
                self.request,
                "リツイートしました。",
                extra_tags="success",
            )
        else:
            # リツイート解除
            target_retweet.delete()
            messages.success(
                self.request,
                "リツイートを解除しました。",
                extra_tags="success",
            )

        # 直前のページにリダイレクトする
        return redirect(request.META.get("HTTP_REFERER", "tweets:timeline"))
