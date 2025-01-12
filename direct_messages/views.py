from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.models import CustomUser, FollowRelation


class MessageListView(LoginRequiredMixin, ListView):
    """メッセージ一覧ビュー"""

    model = FollowRelation
    template_name = "direct_messages/index.html"
    context_object_name = "followers"

    def get_queryset(self):
        # ログインユーザ取得
        user = self.request.user
        # ログインユーザーのフォロワー取得
        return FollowRelation.get_followers(user)


class MessageRoomView(LoginRequiredMixin, DetailView):
    """メッセージ部屋ビュー"""

    model = CustomUser
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "direct_messages/message_room.html"
    context_object_name = "follower"
