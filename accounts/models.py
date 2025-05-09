from django.contrib.auth.models import AbstractUser
from django.db import models
from django.templatetags.static import static


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
    description = models.TextField("自己紹介", max_length=160, blank=True)
    tel_number = models.CharField("電話番号", max_length=15, null=True, blank=True)
    birth_date = models.DateField("生年月日", null=True, blank=True)
    icon_image = models.ImageField(
        "アイコン画像", upload_to=icon_image_path, blank=True
    )
    header_image = models.ImageField(
        "ヘッダー画像", upload_to=header_image_path, blank=True
    )
    location = models.CharField("場所", max_length=30, blank=True)
    website = models.CharField("ウェブサイト", max_length=100, blank=True)
    login_count = models.IntegerField("ログイン回数", default=0)

    def __str__(self):
        return self.username

    @property
    def icon_image_url(self):
        """アイコン画像のURLを取得して、存在しない場合はデフォルト画像を返す"""
        if self.icon_image and self.icon_image != "":
            return self.icon_image.url
        return static("default_icon.png")

    @property
    def display_name(self):
        """名前が設定されていれば返す、なければusernameを返す"""
        if self.name and self.name.strip():
            # 前後の空白を取り除く
            return self.name.strip()
        return self.username

    def is_followed_by_user(self, user):
        """指定したユーザーがフォロワーかどうか確認する"""
        try:
            self.follower_relations.get(follower=user)
            return True
        except FollowRelation.DoesNotExist:
            return False

    def get_followings(self):
        """自身がフォローしている人を取得する"""
        return self.following_relations.select_related("followee")

    def get_followers(self):
        """自身のフォロワーを取得する"""
        return self.follower_relations.select_related("follower")

    def get_notifications(self):
        """自身への通知情報を取得する"""
        return self.received_notifications.select_related(
            "notification_type", "sender", "tweet"
        ).order_by("-created_at")

    def post_login(self):
        """ログイン後処理"""
        # ログイン回数を増やす
        self.login_count += 1
        self.save()

    def get_relations(self):
        """ユーザーに関連する情報を取得する"""
        return {
            # いいねしたツイートID
            "liked_tweet_ids": set(self.likes.values_list("tweet_id", flat=True)),
            # リツイートしたツイートID
            "retweeted_tweet_ids": set(
                self.retweets.values_list("tweet_id", flat=True)
            ),
            # ブックマークしたツイートID
            "bookmarked_tweet_ids": set(
                self.bookmarks.values_list("tweet_id", flat=True)
            ),
            # フォローしているユーザーID
            "following_user_ids": set(
                self.following_relations.values_list("followee_id", flat=True)
            ),
            # フォロワーのID
            "follower_user_ids": set(
                self.follower_relations.values_list("follower_id", flat=True)
            ),
        }


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
