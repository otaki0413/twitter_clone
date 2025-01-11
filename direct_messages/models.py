from django.db import models
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
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"],
                name="unique_message_relation",
            )
        ]

    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField("メッセージ内容", null=False, blank=False)
