from django.shortcuts import render
from .models import LessonLine

def chat(request, lesson_id):
    lines = (
        LessonLine.objects
        .filter(lesson_id=lesson_id)
        .order_by("id")   # ou seq/position
    )

    return render(request, "chat/chat.html", {
        "lesson_id": lesson_id,
        "lines": lines,
    })
