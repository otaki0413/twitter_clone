from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from accounts.models import CustomUser, FollowRelation
from .models import Message
from .forms import MessageCreateForm


class MessageListView(LoginRequiredMixin, ListView):
    """メッセージ一覧ビュー"""

    model = FollowRelation
    template_name = "direct_messages/index.html"
    context_object_name = "followers"

    def get_queryset(self):
        user = self.request.user
        # ログインユーザーのフォロワー取得
        return FollowRelation.get_followers(user)


class MessageRoomView(LoginRequiredMixin, DetailView):
    """メッセージ部屋ビュー"""

    model = CustomUser
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "direct_messages/message_room.html"
    context_object_name = "follower"

    def get(self, request, *args, **kwargs):
        # パスパラメータを元に対象ユーザー取得
        user = get_object_or_404(CustomUser, username=self.kwargs["username"])
        # メッセージ部屋のユーザーがフォロワーでない場合はアクセスさせないようにする
        if not FollowRelation.is_following(follower=user, followee=request.user):
            messages.success(
                self.request,
                "フォロワーではないユーザーにメッセージは送信できません。",
                extra_tags="danger",
            )
            # 直前のページにリダイレクトする
            return redirect(
                request.META.get("HTTP_REFERER", "direct_messages:message_list")
            )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # メッセージ履歴をセット
        context["message_history"] = Message.get_messages(
            sender=self.request.user, receiver=self.object
        )
        # メッセージ送信フォームをセット
        context["form"] = MessageCreateForm
        return context


class MessageCreateView(LoginRequiredMixin, CreateView):
    """メッセージ送信ビュー"""

    model = Message
    form_class = MessageCreateForm
    template_name = "direct_messages/message_room.html"

    def get(self, request, *args, **kwargs):
        # GETリクエスト時には対象のメッセージ部屋へリダイレクト
        username = self.kwargs["username"]
        return redirect("direct_messages:message_room", username=username)

    def get_success_url(self):
        # 送信成功後は、該当のメッセージ部屋にリダイレクト
        return reverse_lazy(
            "direct_messages:message_room", kwargs={"username": self.kwargs["username"]}
        )

    def get_receiver(self):
        """メッセージ受信者を取得する"""
        return get_object_or_404(CustomUser, username=self.kwargs["username"])

    def form_valid(self, form):
        # フォームからインスタンス取得（※まだ保存しない）
        message = form.save(commit=False)

        # フォームインスタンスに送信者と受信者を設定
        message.sender = self.request.user
        message.receiver = self.get_receiver()
        # フォームデータ保存
        message.save()
        messages.success(
            self.request,
            "メッセージの送信に成功しました。",
            extra_tags="success",
        )

        # 親クラスの処理実行
        return super().form_valid(form)

    def form_invalid(self, form):
        # コンテキスト生成
        context = self.get_context_data()
        context["follower"] = get_object_or_404(
            CustomUser, username=self.kwargs["username"]
        )
        context["message_history"] = Message.get_messages(
            sender=self.request.user, receiver=self.get_receiver()
        )
        # メッセージ部屋ページ再描画
        return render(self.request, "direct_messages/message_room.html", context)
