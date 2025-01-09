from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class MessageListView(TemplateView):
    """メッセージ一覧ビュー"""

    template_name = "messages/index.html"
