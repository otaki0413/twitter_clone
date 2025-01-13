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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # メーセージ送信先を取得して、メッセージ履歴をセット
        receiver = get_object_or_404(CustomUser, username=self.kwargs["username"])
        context["message_history"] = Message.get_messages(
            sender=self.request.user, receiver=receiver
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

    def form_valid(self, form):
        # フォームからインスタンス取得（※まだ保存しない）
        message = form.save(commit=False)

        # フォームインスタンスに送信者と受信者を設定
        message.sender = self.request.user
        message.receiver = get_object_or_404(
            CustomUser, username=self.kwargs["username"]
        )
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
        # メッセージ部屋ページ再描画
        return render(self.request, "direct_messages/message_room.html", context)
