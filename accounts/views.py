from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView

from allauth.account.views import SignupView, LoginView

from .forms import CustomSignupForm


class CustomSignupView(SignupView):
    """カスタムサインアップビュー"""

    def get_form_class(self):
        return CustomSignupForm

    # def post(self, request, *args, **kwargs):
    #     print("POSTリクエストが送信されました")
    #     form = self.get_form()
    #     if form.is_valid():
    #         print("フォームは有効です")
    #         return self.form_valid(form)
    #     else:
    #         print("フォームは無効です")
    #         print(form.errors)  # エラー内容を表示
    #         return self.form_invalid(form)

    def form_valid(self, form):
        # フォーム有効時に実行
        print("form_validが呼ばれました")
        user = form.save(self.request)

        # ユーザーを自動的にログイン
        login(
            self.request,
            user,
            backend="allauth.account.auth_backends.AuthenticationBackend",
        )

        # リダイレクト
        return redirect(self.get_success_url())
        # return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:hoge")


# class CustomLoginView(LoginView):
#     def get_success_url(self):
#         # サインアップ成功後のリダイレクト先
#         return reverse_lazy("accounts:hoge")


class HogeView(TemplateView):
    template_name = "account/hoge.html"


class LogoutView:
    pass
