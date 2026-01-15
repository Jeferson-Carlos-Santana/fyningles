from django.urls import path
from .views import index, chat, chat_home, dictionary, dictionary_add, dictionary_delete, tts, tts_line
from . import views
urlpatterns = [
    path("", index, name="login"),
    path("dashboard/", index, name="dashboard"),
    path("chat/", chat_home, name="chat"),
    path("chat/<int:lesson_id>/", chat, name="chatId"),
    path("dictionary/", dictionary, name="dictionary"),
    path("dictionary/add/", dictionary_add, name="dictionary_add"),
    path("dictionary/delete/", dictionary_delete, name="dictionary_delete"),    
    path("tts/", tts, name="tts"),
    path("tts/line/", tts_line, name="tts_line"), 
    path("progress/save/", views.save_progress, name="save_progress"),
    path("progress/tmp/save/", views.save_progress_tmp, name="save_progress_tmp"),
    path("progress/total/", views.total_points, name="total_points"),
    path("progress/feitos/", views.points_feitos, name="points_feitos"),
    path("user/nivel/", views.user_nivel_get, name="user_nivel_get"),
    path("user/nivel/set/", views.user_nivel_set, name="user_nivel_set"),
    path("phrases/progress/", views.phrase_progress, name="phrase_progress"),

]
