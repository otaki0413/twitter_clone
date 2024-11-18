from django.contrib import admin

from .models import Tweet


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    model = Tweet
    list_display = ["user", "content", "created_at", "updated_at"]
    readonly_fields = ("created_at", "updated_at")
