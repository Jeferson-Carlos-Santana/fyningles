from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import index, chat, chat_home, dictionary, dictionary_add, dictionary_delete, tts, tts_line
from . import views
urlpatterns = [
    path("", index, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.register_user, name="register"), 
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
    path("phrases/completed/", views.phrase_completed, name="phrase_completed"),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate"),
    path("resend-activation/", views.resend_activation, name="resend_activation"),
    path("progress/mark-learned/", views.mark_learned, name="mark_learned"),
    path("speech/evaluate/", views.speech_evaluate, name="speech_evaluate"),
]

urlpatterns += [
    path(
        "password-reset/",
        views.ActiveOnlyPasswordResetView.as_view(
            template_name="chat/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="chat/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="chat/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="chat/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
