from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.chat.urls")),
    path("login/", LoginView.as_view(template_name="chat/login.html"), name="login"),
]



