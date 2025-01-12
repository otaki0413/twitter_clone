from django.urls import path

from . import views

app_name = "direct_messages"
urlpatterns = [
    path("", views.MessageListView.as_view(), name="message_list"),
    path("<str:username>/", views.MessageRoomView.as_view(), name="message_room"),
    path(
        "<str:username>/create/",
        views.MessageCreateView.as_view(),
        name="message_create",
    ),
]
