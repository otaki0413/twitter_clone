from django.urls import path

from . import views

app_name = "tweets"
urlpatterns = [
    path("", views.TimelineView.as_view(), name="timeline"),
]
