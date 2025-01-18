from django.contrib import admin

from .models import NotificationType, Notification


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    model = NotificationType
    readonly_fields = ("created_at", "updated_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    model = Notification
    readonly_fields = ("created_at", "updated_at")
