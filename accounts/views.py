from django.contrib.auth import login
from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import SignupForm


class SignupView(CreateView):
    template_name = "accounts/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        """ユーザー登録後に自動でログインさせる"""

        # self.objectにsave()されたUserオブジェクトが入る
        valid = super().form_valid(form)
        # user = form.save()
        login(self.request, self.object)
        return valid


class LoginView:
    pass


class LogoutView:
    pass
