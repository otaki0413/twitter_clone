from django.utils import timezone
from django.db import models
from django.db.models import Q
from accounts.models import CustomUser


class AbstractCommon(models.Model):
    """共通フィールド用の抽象基底クラス"""

    class Meta:
        abstract = True

    created_at = models.DateTimeField("登録日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)


class Message(AbstractCommon):
    """メッセージ情報の格納用モデル"""

    class Meta:
        db_table = "message"

    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField("メッセージ内容", null=False, blank=False)

    def __str__(self):
        format_time = timezone.localtime(self.created_at).strftime("%Y/%M/%d %H:%M:%S")
        return f"[{self.sender} -> {self.receiver}] {self.content} ({format_time})"

    @classmethod
    def get_messages(cls, sender, receiver):
        """送信者と受信者のメッセージ履歴を取得する"""
        return cls.objects.filter(
            Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
        ).order_by("created_at")
