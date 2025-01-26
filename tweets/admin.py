from django.contrib import admin

from .models import Tweet, Like, Retweet, Comment, Bookmark


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    model = Tweet
    readonly_fields = ("created_at", "updated_at")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    model = Like
    readonly_fields = ("created_at", "updated_at")


@admin.register(Retweet)
class RetweetAdmin(admin.ModelAdmin):
    model = Retweet
    readonly_fields = ("created_at", "updated_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    model = Comment
    readonly_fields = ("created_at", "updated_at")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    model = Bookmark
    readonly_fields = ("created_at", "updated_at")
