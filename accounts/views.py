from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.contrib import messages

from allauth.account.views import SignupView, LoginView


class CustomSignupView(SignupView):
    """カスタムサインアップビュー"""

    def form_valid(self, form):
        # 親のform_valid()を呼ぶことで、内部的にユーザー登録からリダイレクトまで行う
        response = super().form_valid(form)
        messages.success(
            self.request, "ユーザー登録に成功しました。", extra_tags="success"
        )
        return response


class CustomLoginView(LoginView):
    """カスタムログインビュー"""

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class HomeView(TemplateView):
    template_name = "account/home.html"

    def get(self, *args, **kwargs):
        # セッションが存在しない場合、ログイン画面へリダイレクト
        if self.request.session.session_key is None:
            return redirect("accounts:login")
        return super().get(*args, **kwargs)
