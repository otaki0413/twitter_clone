from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.models import CustomUser


class MessageListView(LoginRequiredMixin, ListView):
    """メッセージ一覧ビュー"""

    template_name = "direct_messages/index.html"
    context_object_name = "followers"

    def get_queryset(self):
        # ログインユーザ取得
        user = self.request.user
        # ログインユーザのフォロワー取得
        return CustomUser.objects.filter(following_relations__followee=user)


class MessageRoomView(LoginRequiredMixin, DetailView):
    """メッセージ部屋ビュー"""

    model = CustomUser
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "direct_messages/message_room.html"
    context_object_name = "follower"
