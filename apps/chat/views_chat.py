from django.shortcuts import render
from .models import LessonLine  # ajuste se o nome for outro

def chat(request, lesson_id):
    line = (
        LessonLine.objects
        .filter(lesson_id=lesson_id)
        .order_by("id")   # ou "order"/"position"
        .first()
    )

    phrase_html = line.text if line else "<em>Sem frases</em>"

    return render(request, "chat/chat.html", {
        "lesson_id": lesson_id,
        "phrase_html": phrase_html,
    })
