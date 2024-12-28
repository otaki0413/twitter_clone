from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages

from allauth.account.views import SignupView, LoginView

from .models import CustomUser, FollowRelation


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


class FollowToggleView(LoginRequiredMixin, View):
    """フォロー・フォロー解除を切り替えるビュー"""

    def post(self, request, *args, **kwargs):
        # ログインユーザーを取得
        user = request.user
        # フォロー対象となるユーザーを取得
        followee = CustomUser.objects.get(pk=request.POST.get("user_id"))

        # フォロー関係が自分自身の場合はエラー（UI側で非表示にしているため、基本的にここを通ることはない）
        if user == followee:
            messages.error(
                self.request,
                "自分自身をフォローすることはできません。",
                extra_tags="danger",
            )
            return redirect(request.META.get("HTTP_REFERER", "tweets:timeline"))

        # 対象のフォロー関係を取得
        try:
            target_follow = user.following_relations.get(followee=followee)
        except FollowRelation.DoesNotExist:
            target_follow = None

        # フォローの切り替え処理
        if target_follow is None:
            # フォローする
            user.following_relations.create(followee=followee)
            messages.success(
                self.request,
                f"{followee.username}をフォローしました。",
                extra_tags="success",
            )
        else:
            # フォロー解除
            target_follow.delete()
            messages.success(
                self.request,
                f"{followee.username}のフォローを解除しました。",
                extra_tags="success",
            )

        # 直前のページにリダイレクトする
        return redirect(request.META.get("HTTP_REFERER", "tweets:timeline"))
