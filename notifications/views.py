from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """通知一覧ビュー"""

    model = Notification
    template_name = "notifications/index.html"
    context_object_name = "notification_list"

    def get_queryset(self):
        # ログインユーザーへの通知情報を返す
        user = self.request.user
        return user.get_notifications()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context
