from django.urls import path

from . import views

app_name = "direct_messages"
urlpatterns = [
    path("", views.MessageListView.as_view(), name="message_list"),
    path("<str:username>/", views.MessageRoomView.as_view(), name="message_room"),
]
