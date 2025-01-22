from django.db import models
from accounts.models import CustomUser
from tweets.models import Tweet


class AbstractCommon(models.Model):
    """共通フィールド用の抽象基底クラス"""

    class Meta:
        abstract = True

    created_at = models.DateTimeField("登録日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)


class NotificationType(AbstractCommon):
    """通知種別の格納用モデル"""

    class Meta:
        db_table = "notification_type"

    name = models.CharField("通知種別名", max_length=30, null=False, blank=False)
    description = models.CharField("説明", max_length=100, null=True, blank=False)

    def __str__(self):
        return f"{self.id}：{self.name}"


class Notification(AbstractCommon):
    """通知情報の格納用モデル"""

    class Meta:
        db_table = "notification"

    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="通知種別",
    )
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        verbose_name="送信者",
    )
    receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="received_notifications",
        verbose_name="受信者",
    )
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    is_read = models.BooleanField("既読フラグ", default=False)

    def __str__(self):
        return f"{self.notification_type}：{self.sender} -> {self.receiver}"

    @classmethod
    def create_notification(cls, notification_type_name, sender, receiver, tweet):
        """通知情報を作成する処理"""
        notification_type = NotificationType.objects.get(name=notification_type_name)
        return cls.objects.create(
            notification_type=notification_type,
            sender=sender,
            receiver=receiver,
            tweet=tweet,
        )
