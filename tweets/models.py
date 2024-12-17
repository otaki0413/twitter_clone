from django.db import models
from accounts.models import CustomUser


class AbstractCommon(models.Model):
    """共通フィールド用の抽象基底クラス"""

    class Meta:
        abstract = True

    created_at = models.DateTimeField("登録日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)


class Tweet(AbstractCommon):
    """ツイート情報の格納用モデル"""

    class Meta:
        db_table = "tweet"

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="tweets"
    )
    content = models.TextField("ツイート内容", max_length=140, null=False, blank=False)
    image = models.ImageField("ツイート画像", upload_to="tweets/", blank=True)

    def __str__(self):
        return f"{self.user.username}のツイート"


class Like(AbstractCommon):
    """いいね情報の格納用モデル"""

    class Meta:
        db_table = "like"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tweet"],
                name="unique_like_relation",
            )
        ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="likes")
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)

    def __str__(self):
        return f"[{self.id}] {self.user.username} like: {self.tweet.content}"


class Retweet(AbstractCommon):
    """リツイート情報の格納用モデル"""

    class Meta:
        db_table = "retweet"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tweet"],
                name="unique_retweet_relation",
            )
        ]

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="retweets"
    )
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)

    def __str__(self):
        return f"[{self.id}] {self.user.username} retweet: {self.tweet.content}"


class Comment(AbstractCommon):
    """コメント情報の格納用モデル"""

    class Meta:
        db_table = "comment"

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments"
    )
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    content = models.TextField("コメント内容", null=False, blank=False)

    def __str__(self):
        return f"[{self.id}] {self.user.username} commented: {self.content} on {self.tweet.content}"
