from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .utils.dictionary_writer import add_term, term_exists, delete_term, list_terms
from deep_translator import GoogleTranslator
from django.shortcuts import redirect
from django.contrib import messages
from langdetect import detect, LangDetectException
import requests, json
from django.views.decorators.csrf import csrf_exempt
from .models import Chat

import hashlib
import os
import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def tts(request):
    data = json.loads(request.body)
    text = data.get("text", "").strip()

    if not text:
        return JsonResponse({"error": "no text"}, status=400)

    # 🔑 nome fixo baseado no TEXTO (cache)
    filename = hashlib.md5(text.encode("utf-8")).hexdigest() + ".mp3"
    cache_dir = os.path.join(settings.MEDIA_ROOT, "cache")
    cache_path = os.path.join(cache_dir, filename)

    # garante que a pasta existe
    os.makedirs(cache_dir, exist_ok=True)

    # ✅ SE JÁ EXISTE → NÃO GERA DE NOVO
    if os.path.exists(cache_path):
        return JsonResponse({
            "file": filename,
            "cached": True
        })

    # ❌ SE NÃO EXISTE → CHAMA O TTS (Python 3.10)
    r = requests.post(
        "http://127.0.0.1:9000",
        json={"text": text, "filename": filename},
        timeout=20
    )

    return JsonResponse({
        "file": filename,
        "cached": False
    })


def index(request):
    return render(request, "chat/index.html")


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
    
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chat
import json, requests

@csrf_exempt
def tts_line(request):
    data = json.loads(request.body)
    line_id = data.get("line_id")

    line = Chat.objects.get(id=line_id)
    text = line.expected_en  # texto limpo enviado ao TTS externo

    # CHAMADA AO SERVIÇO TTS EXTERNO
    r = requests.post(
        "http://127.0.0.1:9000",   # endpoint do TTS (outro projeto)
        json={"text": text},
        timeout=20
    )

    # o TTS retorna: {"file": "uuid.mp3"}
    return JsonResponse(r.json())





def lessons(request):
    return render(request, "chat/lessons.html")

# LISTAR DADOS DO JSON
def dictionary(request):
    lang = request.GET.get("lang", "pt")  # padrão pt
    terms = list_terms(lang)

    return render(request, "chat/dictionary.html", {
        "lang": lang,
        "terms": terms
    })
# FIM LISTAR DADOS DO JSON

# ADICIONAR DADOS NO JSON
def dictionary_add(request):
    if request.method != "POST":
        # return redirect("dictionary")
        return redirect(f"/dictionary/?lang={lang}")

    lang = request.POST.get("lang")
    # term = request.POST.get("term")
    term = request.POST.get("term").strip()

    if not lang or not term:
        messages.error(request, "Preencha o idioma e a palavra.")
        # return redirect("dictionary")
        return redirect(f"/dictionary/?lang={lang}")

    if term_exists(lang, term):
        messages.error(request, "Esta palavra ou frase já existe.")
        # return redirect("dictionary")
        return redirect(f"/dictionary/?lang={lang}")
    
    # bloqueia idiomas não-base
    if lang not in ("pt", "en"):
        messages.error(
            request,
            "Inserções só são permitidas em Português ou Inglês."
        )
        return redirect(f"/dictionary/?lang={lang}")
    
    try:
        detected = detect(term)
    except LangDetectException:
        messages.error(request, "Não foi possível identificar o idioma.")
        return redirect(f"/dictionary/?lang={lang}")

    force = request.POST.get("force")

    if lang == "pt" and detected != "pt" and not force:
        messages.warning(
            request,
            "Essa frase não parece estar em Português. Deseja cadastrar mesmo assim?"
        )
        return redirect(f"/dictionary/?lang={lang}&term={term}&confirm=1")

    if lang == "en" and detected != "en" and not force:
        messages.warning(
            request,
            "Essa frase não parece estar em Inglês. Deseja cadastrar mesmo assim?"
        )
        return redirect(f"/dictionary/?lang={lang}&term={term}&confirm=1")
    
    # só PT ou EN podem iniciar transação
    if lang in ("pt", "en"):

        translations = {}  # buffer em memória

        targets = ["pt", "en", "es", "fr", "it"]
        targets.remove(lang)

        # 1) traduz TUDO primeiro
        for target in targets:
            translated = GoogleTranslator(
                source=lang,
                target=target
            ).translate(term)

            # falhou → aborta tudo
            if not translated or not translated.strip():
                messages.error(
                    request,
                    "Falha na tradução. Nenhum dado foi gravado."
                )
                return redirect(f"/dictionary/?lang={lang}")

            translations[target] = translated.strip()

        # 2) só agora grava TUDO
        add_term(lang, term)

        for target, translated in translations.items():
            if not term_exists(target, translated):
                add_term(target, translated)

        messages.success(request, "Salvo com sucesso em todos os idiomas!")
        return redirect(f"/dictionary/?lang={lang}")


    # # 1) salva o termo no idioma escolhido
    # add_term(lang, term)

    # # 2) se for PT ou EN, traduz e salva nos outros idiomas
    # if lang in ("pt", "en"):
    #     targets = ["pt", "en", "es", "fr", "it"]
    #     targets.remove(lang)

    #     for target in targets:
    #         translated = GoogleTranslator(source=lang, target=target).translate(term)

    #         # evita duplicado no idioma de destino
    #         if translated and not term_exists(target, translated):
    #             add_term(target, translated)

    #     messages.success(request, "Salvo e traduzido para os outros idiomas!")
    #     return redirect(f"/dictionary/?lang={lang}")

    # 3) ES/FR/IT: só salva, não traduz
    messages.success(request, "Salvo!")
    return redirect(f"/dictionary/?lang={lang}")
# FIM ADICIONAR DADOS NO JSON

# APAGAR DADOS NO JSON
def dictionary_delete(request):
    if request.method != "POST":
        # return redirect("dictionary")
        return redirect(f"/dictionary/?lang={lang}")

    lang = request.POST.get("lang")
    # term = request.POST.get("term")
    term = request.POST.get("term").strip()
    
    # bloqueia delete direto em idiomas não-base
    if lang not in ("pt", "en"):
        messages.error(
            request,
            "Exclusões só são permitidas a partir do Português ou Inglês."
        )
        return redirect(f"/dictionary/?lang={lang}")

    if not lang or not term:
        messages.error(request, "Dados inválidos.")
        return redirect(f"/dictionary/?lang={lang}")
        # return redirect("dictionary")

    # apaga o termo base
    deleted = delete_term(lang, term)

    if not deleted:
        messages.error(request, "Termo não encontrado.")
        # return redirect("dictionary")
        return redirect(f"/dictionary/?lang={lang}")

    # se for PT ou EN, apaga traduções
    if lang in ("pt", "en"):
        targets = ["pt", "en", "es", "fr", "it"]
        targets.remove(lang)

        for target in targets:
            translated = GoogleTranslator(source=lang, target=target).translate(term)
            delete_term(target, translated)

        messages.success(request, "Termo e traduções apagados com sucesso!")
        # return redirect("dictionary")
        return redirect(f"/dictionary/?lang={lang}")

    messages.success(request, "Termo apagado com sucesso!")
    # return redirect("dictionary")
    return redirect(f"/dictionary/?lang={lang}")
# FIM APAGAR DADOS NO JSON

