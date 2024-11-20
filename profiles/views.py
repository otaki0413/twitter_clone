from django.views.generic import DetailView
from accounts.models import CustomUser


class UserProfileView(DetailView):
    """ユーザーのプロフィール詳細ビュー"""

    model = CustomUser
    template_name = "profiles/profile.html"
    context_object_name = "user_profile"
    slug_field = "username"  # モデルのフィールド名
    slug_url_kwarg = "username"  # urls.pyでのキーワード名
