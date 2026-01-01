from django.urls import path
from django.contrib.auth import views as auth_views
from .views import index, chat, chat_home, lessons, dictionary, dictionary_add, dictionary_delete, tts, tts_line

urlpatterns = [
    path("", index, name="dashboard"),
    path("chat/", chat_home, name="chat"),
    path("chat/<int:lesson_id>/", chat, name="chatId"),
    path("lessons/", lessons, name="lessons"),
    path("dictionary/", dictionary, name="dictionary"),
    path("dictionary/add/", dictionary_add, name="dictionary_add"),
    path("dictionary/delete/", dictionary_delete, name="dictionary_delete"),    
    path("tts/", tts, name="tts"),
    path("tts/line/", tts_line, name="tts_line"), 
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

]
