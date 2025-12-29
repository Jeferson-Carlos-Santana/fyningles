from django.urls import path
from .views import index, chat, dictionary, dictionary_add, dictionary_delete, tts, tts_line

urlpatterns = [
    path("", index, name="dashboard"),
    path("chat/<int:lesson_id>/", chat, name="chat"),
    path("dictionary/", dictionary, name="dictionary"),
    path("dictionary/add/", dictionary_add, name="dictionary_add"),
    path("dictionary/delete/", dictionary_delete, name="dictionary_delete"),    
    path("tts/", tts, name="tts"),
    path("tts/line/", tts_line, name="tts_line"),
]

