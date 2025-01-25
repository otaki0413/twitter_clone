from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, resolve_url


class TweetListMixin:
    """ツイート一覧表示用の共通処理をまとめるMixin"""

    def get_tweet_context(self, current_user):
        """ツイート一覧表示に必要なコンテキストを取得する"""
        return {
            # ログインユーザーがフォローしているか設定
            "is_followed_by_user": current_user.is_followed_by_user(self.request.user),
            # ユーザーがフォロワーかどうか設定
            "is_following": self.request.user.is_followed_by_user(current_user),
            # ツイート一覧
            "tweet_list": self.get_tweet_queryset(current_user),
        }

    def get_tweet_queryset(self, user):
        """ツイート一覧を取得する（サブクラスでの実装必須）"""
        raise NotImplementedError("Subclasses must implement get_tweet_queryset()")


# TODO:プロフィールページに関するすべてのビューでこのmixinを継承したいが、なぜか処理が呼ばれないので一旦コメントアウト
# class FollowStatusMixin:
#     """ログインユーザーがフォローしているかどうかを設定する処理"""

#     def get_context_data(self, *args, **kwargs):
#         """フォロー関係をチェックし、コンテキストに設定する処理"""
#         context = super().get_context_data(*args, **kwargs)
#         # ログインユーザーを取得
#         current_user = self.object
#         # ログインユーザーがフォローしているか設定
#         context["is_followed_by_user"] = current_user.is_followed_by_user(
#             self.request.user
#         )
#         return context


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
