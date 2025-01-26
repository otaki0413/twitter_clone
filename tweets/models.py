from django.db import models
from accounts.models import CustomUser
from config.utils import get_resized_image_url


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
    content = models.CharField("ツイート内容", max_length=140, null=False, blank=False)
    image = models.ImageField("ツイート画像", upload_to="tweets/", blank=True)

    def __str__(self):
        return f"{self.user.username}のツイート: ${self.content[:20]}"

    @classmethod
    def get_base_queryset(cls):
        """基本のクエリセット"""
        return (
            cls.objects.select_related("user")
            .prefetch_related("likes", "retweets", "bookmarks")
            .order_by("-created_at")
        )

    @classmethod
    def get_timeline_tweets(cls, requesting_user):
        """おすすめのツイート一覧を取得する"""
        queryset = cls.get_base_queryset()
        return cls.get_tweets_with_status(queryset, requesting_user)

    @classmethod
    def get_following_tweets(cls, requesting_user):
        """フォロー中のツイート一覧を取得する"""
        following_user_ids = requesting_user.following_relations.values_list(
            "followee", flat=True
        )
        queryset = cls.get_base_queryset().filter(user_id__in=following_user_ids)
        return cls.get_tweets_with_status(queryset, requesting_user)

    @classmethod
    def get_my_tweets(cls, user, requesting_user=None):
        """自身のツイート一覧を取得する"""
        queryset = cls.get_base_queryset().filter(user=user)
        return cls.get_tweets_with_status(queryset, requesting_user)

    @classmethod
    def get_liked_tweets(cls, user, requesting_user=None):
        """いいねしたツイート一覧を取得する"""
        liked_tweet_ids = user.likes.values_list("tweet", flat=True)
        queryset = cls.get_base_queryset().filter(id__in=liked_tweet_ids)
        return cls.get_tweets_with_status(queryset, requesting_user)

    @classmethod
    def get_retweeted_tweets(cls, user, requesting_user=None):
        """リツイートしたツイート一覧を取得する"""
        retweeted_tweet_ids = user.retweets.values_list("tweet", flat=True)
        queryset = cls.get_base_queryset().filter(id__in=retweeted_tweet_ids)
        return cls.get_tweets_with_status(queryset, requesting_user)

    @classmethod
    def get_commented_tweets(cls, user, requesting_user=None):
        """コメントしたツイート一覧を取得する"""
        commented_tweet_ids = user.comments.values_list("tweet", flat=True)
        queryset = cls.get_base_queryset().filter(id__in=commented_tweet_ids)
        return cls.get_tweets_with_status(queryset, requesting_user)

    @classmethod
    def get_bookmarked_tweets(cls, requesting_user):
        """ブックマークしたツイート一覧を取得する"""
        bookmarked_tweet_ids = requesting_user.bookmarks.values_list("tweet", flat=True)
        queryset = cls.get_base_queryset().filter(id__in=bookmarked_tweet_ids)
        return cls.get_tweets_with_status(queryset, requesting_user)

    @classmethod
    def get_tweet_detail(cls):
        """単一のツイート情報を取得"""
        return cls.get_base_queryset().prefetch_related("comments__user")

    @classmethod
    def get_tweets_with_status(cls, queryset, requesting_user=None):
        """各ツイートにログインユーザーの情報を付与したものを取得する"""

        # ログインユーザーが指定されていない場合は、そのまま返す
        if requesting_user is None:
            return queryset

        # ログインユーザーに関連する情報取得（いいね・リツイート・ブックマークなど）
        relations = requesting_user.get_relations()
        if relations:
            for tweet in queryset:
                # 各ツイートに情報を付与する
                tweet.add_status(requesting_user, relations)

        return queryset

    def add_status(self, requesting_user, relations):
        """単一のツイートにログインユーザーの情報や画像リサイズを付与する"""

        # ログインユーザーが指定されていない場合は、そのまま返す
        if requesting_user is None:
            return self

        if relations:
            # ログインユーザがいいねしているか設定
            self.is_liked_by_user = self.id in relations["liked_tweet_ids"]
            # ログインユーザがリツイートしているか設定
            self.is_retweeted_by_user = self.id in relations["retweeted_tweet_ids"]
            # ログインユーザーがブックマークしているか設定
            self.is_bookmarked_by_user = self.id in relations["bookmarked_tweet_ids"]
            # ツイート投稿者がフォロワーかどうか設定
            self.user.is_followed_by_user = (
                self.user.id in relations["following_user_ids"]
            )
            # ツイート投稿者がフォロワーかどうか設定
            self.user.is_following = self.user.id in relations["follower_user_ids"]
            # ツイート画像のリサイズ
            if self.image:
                self.resized_image_url = get_resized_image_url(self.image.url, 150, 150)
        return self


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
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="likes")

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
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="retweets")

    def __str__(self):
        return f"[{self.id}] {self.user.username} retweet: {self.tweet.content}"


class Bookmark(AbstractCommon):
    """ブックマーク情報の格納用モデル"""

    class Meta:
        db_table = "bookmark"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tweet"],
                name="unique_bookmark_relation",
            )
        ]

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="bookmarks"
    )
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="bookmarks")

    def __str__(self):
        return f"[{self.id}] {self.user.username} bookmark: {self.tweet.content}"


class Comment(AbstractCommon):
    """コメント情報の格納用モデル"""

    class Meta:
        db_table = "comment"

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments"
    )
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField("コメント内容", null=False, blank=False)

    def __str__(self):
        return f"[{self.id}] {self.user.username} commented: {self.content} on {self.tweet.content}"
