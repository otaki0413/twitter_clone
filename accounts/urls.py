from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("signup/", views.CustomSignupView.as_view(), name="signup"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("follow_toggle/", views.FollowToggleView.as_view(), name="follow_toggle"),
]
