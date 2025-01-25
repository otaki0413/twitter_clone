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
    def get_timeline_tweets(cls):
        """おすすめのツイート一覧を取得する"""
        return (
            cls.objects.select_related("user")
            .prefetch_related("likes", "retweets", "bookmarks")
            .order_by("-created_at")
        )

    @classmethod
    def get_following_tweets(cls, user):
        """フォロー中のツイート一覧を取得する"""
        inner_qs = user.following_relations.values_list("followee", flat=True)
        return (
            cls.objects.filter(user_id__in=inner_qs)
            .select_related("user")
            .prefetch_related("likes", "retweets", "bookmarks")
            .order_by("-created_at")
        )

    @classmethod
    def get_bookmarked_tweets(cls, user):
        """ブックマークしたツイート一覧を取得する"""
        inner_qs = user.bookmarks.values_list("tweet", flat=True)
        return (
            cls.objects.filter(id__in=inner_qs)
            .select_related("user")
            .prefetch_related("likes", "retweets", "bookmarks")
            .order_by("-created_at")
        )

    @classmethod
    def get_my_tweets(cls, user, requesting_user=None):
        """自身のツイート一覧を取得する"""
        queryset = (
            cls.objects.filter(user=user)
            .select_related("user")
            .prefetch_related("likes", "retweets", "bookmarks")
            .order_by("-created_at")
        )
        return cls.add_tweet_status(queryset, requesting_user)

    @classmethod
    def get_liked_tweets(cls, user, requesting_user=None):
        """いいねしたツイート一覧を取得する"""
        liked_tweet_ids = user.likes.values_list("tweet", flat=True)
        queryset = (
            cls.objects.filter(id__in=liked_tweet_ids)
            .select_related("user")
            .prefetch_related("likes", "retweets", "bookmarks")
            .order_by("-created_at")
        )
        return cls.add_tweet_status(queryset, requesting_user)

    @classmethod
    def get_retweeted_tweets(cls, user, requesting_user=None):
        """リツイートしたツイート一覧を取得する"""
        retweeted_tweet_ids = user.retweets.values_list("tweet", flat=True)
        queryset = (
            cls.objects.filter(id__in=retweeted_tweet_ids)
            .select_related("user")
            .prefetch_related("likes", "retweets", "bookmarks")
            .order_by("-created_at")
        )
        return cls.add_tweet_status(queryset, requesting_user)

    @classmethod
    def get_commented_tweets(cls, user, requesting_user=None):
        """コメントしたツイート一覧を取得する"""
        commented_tweet_ids = user.likes.values_list("tweet", flat=True)
        queryset = (
            cls.objects.filter(id__in=commented_tweet_ids)
            .select_related("user")
            .prefetch_related("likes", "retweets", "bookmarks")
            .order_by("-created_at")
        )
        return cls.add_tweet_status(queryset, requesting_user)

    @classmethod
    def add_tweet_status(cls, tweet_queryset, requesting_user):
        """各ツイートにログインユーザーの情報を付与する"""
        # ログインユーザーに関連する情報をツイートから取得
        if requesting_user is not None:
            # いいねしたツイートID
            liked_tweet_ids = set(
                requesting_user.likes.values_list("tweet_id", flat=True)
            )
            # リツイートしたツイートID
            retweeted_tweet_ids = set(
                requesting_user.retweets.values_list("tweet_id", flat=True)
            )
            # ブックマークしたツイートID
            bookmarked_tweet_ids = set(
                requesting_user.bookmarks.values_list("tweet_id", flat=True)
            )
            # フォローしているユーザーID
            following_user_ids = set(
                requesting_user.following_relations.values_list(
                    "followee_id", flat=True
                )
            )
            # フォロワーのID
            follower_user_ids = set(
                requesting_user.follower_relations.values_list("follower_id", flat=True)
            )
            for tweet in tweet_queryset:
                # ログインユーザがいいねしているか設定
                tweet.is_liked_by_user = tweet.id in liked_tweet_ids
                # ログインユーザがリツイートしているか設定
                tweet.is_retweeted_by_user = tweet.id in retweeted_tweet_ids
                # ログインユーザーがブックマークしているか設定
                tweet.is_bookmarked_by_user = tweet.id in bookmarked_tweet_ids
                # ログインユーザーがフォローしているか設定
                tweet.user.is_followed_by_user = tweet.user.id in following_user_ids
                # ツイート投稿者がフォロワーかどうか設定
                tweet.user.is_following = tweet.user.id in follower_user_ids
                # ツイート画像のリサイズ
                if tweet.image:
                    tweet.resized_image_url = get_resized_image_url(
                        tweet.image.url, 150, 150
                    )
        return tweet_queryset

    def is_liked_by_user(self, user):
        """ログインユーザーがいいねしているかどうか"""
        try:
            self.likes.get(user=user)
            return True
        except Like.DoesNotExist:
            return False

    def is_retweeted_by_user(self, user):
        """ログインユーザーがリツイートしているかどうか"""
        try:
            self.retweets.get(user=user)
            return True
        except Retweet.DoesNotExist:
            return False

    def is_bookmarked_by_user(self, user):
        """ログインユーザーがブックマークしているかどうか"""
        try:
            self.bookmarks.get(user=user)
            return True
        except Bookmark.DoesNotExist:
            return False


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
