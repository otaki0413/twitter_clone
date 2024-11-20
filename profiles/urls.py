from django.urls import path
from .views import UserProfileView

app_name = "profiles"
urlpatterns = [
    path("<str:username>/", UserProfileView.as_view(), name="user_profile"),
]
