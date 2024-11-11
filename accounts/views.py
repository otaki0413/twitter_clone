from django.shortcuts import render, redirect
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
