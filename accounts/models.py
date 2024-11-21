from django.contrib.auth.models import AbstractUser
from django.db import models


def icon_image_path(instance, filename):
    """アイコン画像のアップロード先を生成"""
    return f"profiles/{instance.id}/icon/{filename}"


def header_image_path(instance, filename):
    """ヘッダー画像のアップロード先を生成"""
    return f"profiles/{instance.id}/header/{filename}"


class AbstractCommon(models.Model):
    """共通フィールド用の抽象基底クラス"""

    class Meta:
        abstract = True

    created_at = models.DateTimeField("登録日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)


class CustomUser(AbstractUser, AbstractCommon):
    """拡張ユーザーモデル"""

    class Meta:
        db_table = "custom_user"
        verbose_name = verbose_name_plural = "カスタムユーザー"

    name = models.CharField("名前", max_length=50, blank=True)
    email = models.EmailField("メールアドレス", unique=True, null=False, blank=False)
    description = models.TextField("自己紹介", blank=True)
    tel_number = models.CharField("電話番号", max_length=15, null=True, blank=True)
    birth_date = models.DateField("生年月日", null=True, blank=True)
    icon_image = models.ImageField(
        "アイコン画像", upload_to=icon_image_path, blank=True
    )
    header_image = models.ImageField(
        "ヘッダー画像", upload_to=header_image_path, blank=True
    )
    location = models.CharField("場所", max_length=100, blank=True)
    website = models.CharField("ウェブサイト", max_length=255, blank=True)
    login_count = models.IntegerField("ログイン回数", default=0)

    def __str__(self):
        return self.username

    def post_login(self):
        """ログイン後処理"""
        # ログイン回数を増やす
        self.login_count += 1
        self.save()


class FollowRelation(AbstractCommon):
    """フォロー関係の格納用モデル"""

    class Meta:
        db_table = "follow_relation"
        verbose_name = verbose_name_plural = "フォロー関係"
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followee"],
                name="unique_follower_followee_relation",
            )
        ]

    follower = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="following_relations",
        verbose_name="フォローする人",
    )
    followee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="follower_relations",
        verbose_name="フォローされる人",
    )

    def __str__(self):
        return f"{self.follower.username} -> {self.followee.username}"
