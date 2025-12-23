# views.py
from django.shortcuts import render
from .models import Chat

def chat(request, lesson_id):
    lines = (
        Chat.objects
        .filter(lesson_id=lesson_id, status=True)
        .order_by("seq")
    )

    return render(request, "chat/chat.html", {
        "lesson_id": lesson_id,
        "lines": lines,
    })

