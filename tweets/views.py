from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth import get_user_model

from .models import Tweet
from accounts.models import CustomUser, FollowRelation


class TimelineView(ListView):
    """おすすめのツイート一覧ビュー"""

    model = Tweet
    template_name = "tweets/index.html"
    context_object_name = "tweet_list"
    queryset = Tweet.objects.prefetch_related("user")
    ordering = "-created_at"
    # paginate_by = 2

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


class FollowingTweetListView(ListView):
    """フォロー中のツイート一覧ビュー"""

    model = Tweet
    template_name = "tweets/following.html"
    context_object_name = "tweet_list"

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


def get_resized_image_url(
    image_url, width=None, height=None, crop="fill", gravity="auto"
):
    """
    Cloudinaryの画像URLをリサイズ用URLに変換する処理

    Args:
        image_url (str): 元の画像URL
        width (int): リサイズ後の幅（オプショナル）
        height (int): リサイズ後の高さ（オプショナル）
        crop (str): クロップ方法（デフォルトは"fill")
        gravity (str): クロップ位置（デフォルトは"auto"）

    Returns:
        str: リサイズ後の画像URL
    """
    if not image_url:
        return None

    # URLを分割してリサイズ用のトランスフォーメーションを挿入
    parts = image_url.split("/image/upload/")
    if len(parts) != 2:
        # URLの形式が期待と異なる場合、元のURLを返す
        return image_url

    # 動的なリサイズ設定（引数のパラメータを含める）
    transformation_list = [f"c_{crop}", f"g_{gravity}"]
    if width is not None:
        transformation_list.append(f"w_{width}")
    if height is not None:
        transformation_list.append(f"h_{height}")

    # リサイズ設定用の文字列作成
    transformation_str = ",".join(transformation_list)

    # リサイズ後のURL整形
    resized_url = f"{parts[0]}/image/upload/{transformation_str}/{parts[1]}"
    return resized_url
