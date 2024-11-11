from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView


class TimelineView(TemplateView):
    template_name = "tweets/index.html"

    def get(self, *args, **kwargs):
        # セッションが存在しない場合、ログイン画面へリダイレクト
        if self.request.session.session_key is None:
            return redirect("accounts:login")
        return super().get(*args, **kwargs)
