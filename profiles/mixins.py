from django.db.models import QuerySet
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, resolve_url

from config.utils import get_resized_image_url


class TweetListMixin:
    """ツイート一覧を取得し、画像リサイズやログインユーザーのいいね/リツイート情報を付与する処理"""

    def get_tweet_list(
        self, tweet_queryset: QuerySet, order_by: str = "-created_at"
    ) -> QuerySet | None:
        """対象のクエリセットに並び替えオプション追加、リサイズ済みの画像URLを付与する"""
        if tweet_queryset:
            tweet_queryset = tweet_queryset.order_by(order_by)
            # ログインユーザがいいねしているツイートID取得
            liked_tweet_ids = self.request.user.likes.values_list("tweet_id", flat=True)
            # ログインユーザがリツイートしているツイートID取得
            retweeted_tweet_ids = self.request.user.retweets.values_list(
                "tweet_id", flat=True
            )
            for tweet in tweet_queryset:
                if tweet.image:
                    tweet.resized_image_url = get_resized_image_url(
                        tweet.image.url, 150, 150
                    )
                # ログインユーザがいいねしているか設定
                tweet.is_liked_by_user = tweet.id in liked_tweet_ids
                # ログインユーザがリツイートしているか設定
                tweet.is_retweeted_by_user = tweet.id in retweeted_tweet_ids
            return tweet_queryset
        return None


class LoginUserIsUserMixin(UserPassesTestMixin):
    """ログインユーザーと対象ユーザーが一致しているかをチェックする処理"""

    raise_exception = False

    def test_func(self):
        """権限チェック処理"""
        user = self.request.user
        # ログインユーザーと対象ユーザーを比較
        return user.username == self.kwargs.get("username")

    def handle_no_permission(self):
        """権限がない場合の処理"""
        username = self.kwargs.get("username")
        # デフォルトのリダイレクト先は対象ユーザーのプロフィールページ
        default_url = resolve_url("profiles:my_tweet_list", username=username)
        redirect_url = self.get_no_permission_redirect_url() or default_url
        return redirect(redirect_url)

    def get_no_permission_redirect_url(self):
        """権限がない場合のリダイレクト先を取得する処理"""
        # MEMO: 今回は使用していないが、必要に応じて継承先でオーバーライドできる形を取っている
        return None
