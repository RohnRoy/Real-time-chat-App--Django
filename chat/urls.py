from django.urls import path
from .views import user_list, chat_view

urlpatterns = [
    path("", user_list, name="user_list"),
    path("chat/<int:user_id>/", chat_view, name="chat"),
]