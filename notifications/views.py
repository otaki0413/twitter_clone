from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """通知一覧ビュー"""

    model = Notification
    template_name = "notifications/index.html"
