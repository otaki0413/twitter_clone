from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class MessageListView(TemplateView):
    """メッセージ一覧ビュー"""

    template_name = "messages/index.html"


class MessageRoomView(TemplateView):
    """メッセージ部屋ビュー"""

    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "messages/message_room.html"
