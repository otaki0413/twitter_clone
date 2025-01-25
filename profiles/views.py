from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.contrib import messages

import cloudinary.uploader

from accounts.models import CustomUser
from tweets.models import Tweet
from .forms import ProfileEditForm
from .mixins import TweetListMixin, LoginUserIsUserMixin


class MyTweetListView(LoginRequiredMixin, DetailView, TweetListMixin):
    """自身のツイート一覧ビュー（プロフィール詳細ページのデフォルトビュー）"""

    model = CustomUser
    template_name = "profiles/my_tweets.html"
    context_object_name = "user_profile"
    slug_field = "username"  # モデルのフィールド名
    slug_url_kwarg = "username"  # urls.pyでのキーワード名
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tweet_context = self.get_tweet_context(current_user=self.object)
        context.update(tweet_context)
        return context

    def get_tweet_queryset(self, user):
        return Tweet.get_my_tweets(user=user, requesting_user=self.request.user)


class LikedTweetListView(LoginRequiredMixin, DetailView, TweetListMixin):
    """いいねしたツイート一覧ビュー"""

    model = CustomUser
    template_name = "profiles/liked_tweets.html"
    context_object_name = "user_profile"
    slug_field = "username"
    slug_url_kwarg = "username"
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tweet_context = self.get_tweet_context(current_user=self.object)
        context.update(tweet_context)
        return context

    def get_tweet_queryset(self, user):
        return Tweet.get_liked_tweets(user=user, requesting_user=self.request.user)


class RetweetedTweetListView(LoginRequiredMixin, DetailView, TweetListMixin):
    """リツイートしたツイート一覧ビュー"""

    model = CustomUser
    template_name = "profiles/retweeted_tweets.html"
    context_object_name = "user_profile"
    slug_field = "username"
    slug_url_kwarg = "username"
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tweet_context = self.get_tweet_context(current_user=self.object)
        context.update(tweet_context)
        return context

    def get_tweet_queryset(self, user):
        return Tweet.get_retweeted_tweets(user=user, requesting_user=self.request.user)


class CommentedTweetListView(LoginRequiredMixin, DetailView, TweetListMixin):
    """コメントしたツイート一覧ビュー"""

    model = CustomUser
    template_name = "profiles/commented_tweets.html"
    context_object_name = "user_profile"
    slug_field = "username"
    slug_url_kwarg = "username"
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tweet_context = self.get_tweet_context(current_user=self.object)
        context.update(tweet_context)
        return context

    def get_tweet_queryset(self, user):
        return Tweet.get_commented_tweets(user=user, requesting_user=self.request.user)


class ProfileEditView(
    LoginUserIsUserMixin,
    LoginRequiredMixin,
    UpdateView,
):
    """プロフィール編集用のビュー"""

    model = CustomUser
    form_class = ProfileEditForm
    template_name = "profiles/profile_edit.html"
    context_object_name = "user_profile"
    slug_field = "username"
    slug_url_kwarg = "username"
    login_url = reverse_lazy("accounts:login")

    def get_success_url(self):
        # get_success_urlをオーバーライドして動的なパスに遷移させる
        return resolve_url("profiles:my_tweet_list", username=self.kwargs["username"])
        # MEMO:下記でもいける
        # return reverse_lazy(
        #     "profiles:my_tweet_list", kwargs={"username": self.kwargs["username"]}
        # )

    def form_valid(self, form):
        # 現在のユーザー取得
        user = self.request.user
        # フォームからインスタンス取得（※まだ保存しない）
        profile = form.save(commit=False)

        # アップロードされたアイコン画像を取得
        icon_image = self.request.FILES.get("icon_image")
        if icon_image is not None:
            # 既存のアイコン画像があればCloudinaryから削除
            if user.icon_image:
                cloudinary.uploader.destroy(user.icon_image.name, invalidate=True)
            # 新しいアイコン画像を設定
            profile.icon_image = icon_image

        # アップロードされたヘッダー画像を取得
        header_image = self.request.FILES.get("header_image")
        if header_image is not None:
            # 既存のヘッダー画像があればCloudinaryから削除
            if user.header_image:
                cloudinary.uploader.destroy(user.header_image.name, invalidate=True)
            # 新しいヘッダー画像を設定
            profile.header_image = header_image

        messages.success(
            self.request, "プロフィールを更新しました", extra_tags="success"
        )
        # 親クラス側で保存処理を実行
        return super().form_valid(form)
