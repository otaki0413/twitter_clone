from django.contrib.auth.models import AbstractUser
from django.db import models


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

    email = models.EmailField("メールアドレス", unique=True, null=False, blank=False)
    description = models.TextField("自己紹介", blank=True)
    tel_number = models.CharField("電話番号", null=False, max_length=15)
    birth_date = models.DateField("生年月日", null=False)
    icon_image = models.ImageField("アイコン画像", upload_to="", blank=True)
    header_image = models.ImageField("ヘッダー画像", upload_to="", blank=True)
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
