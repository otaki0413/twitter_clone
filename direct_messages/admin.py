from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    model = Message
    readonly_fields = ("created_at", "updated_at")
