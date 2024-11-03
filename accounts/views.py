from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView

from allauth.account.views import SignupView, LoginView


class CustomSignupView(SignupView):
    """カスタムサインアップビュー"""

    def form_valid(self, form):
        # 親のform_valid()を呼ぶことで、内部的にユーザー登録からリダイレクトまで行う
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse_lazy("accounts:home")


class CustomLoginView(LoginView):
    """カスタムログインビュー"""

    def get_success_url(self):
        return reverse_lazy("accounts:home")


class HogeView(TemplateView):
    template_name = "account/home.html"


class LogoutView:
    pass
