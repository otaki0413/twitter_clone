from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, resolve_url


class FollowStatusMixin:
    """フォロー関係をまとめるMixin"""

    def get_follow_context(self, user):
        """フォロー関係のコンテキストを取得する"""
        return {
            # ログインユーザーがフォローしているか設定
            "is_followed_by_user": user.is_followed_by_user(self.request.user),
            # ユーザーがフォロワーかどうか設定
            "is_following": self.request.user.is_followed_by_user(user),
        }


class TweetListMixin:
    """ツイート一覧表示用の共通処理をまとめるMixin"""

    def get_tweet_context(self, user):
        """ツイート一覧表示に必要なコンテキストを取得する"""
        return {"tweet_list": self.get_tweet_queryset(user)}

    def get_tweet_queryset(self, user):
        """ツイート一覧を取得する（サブクラスでの実装必須）"""
        raise NotImplementedError("Subclasses must implement get_tweet_queryset()")


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
