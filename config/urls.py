from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("hello/", TemplateView.as_view(template_name="hello.html")),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
]

# 開発環境でdebug_toolbarを使用する設定
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
