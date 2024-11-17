from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import FollowRelation

CustomUser = get_user_model()

admin.site.register(CustomUser)


@admin.register(FollowRelation)
class FollowRelationAdmin(admin.ModelAdmin):
    model = FollowRelation
    readonly_fields = ("created_at", "updated_at")
