from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .utils.dictionary_writer import add_term, term_exists, delete_term, list_terms
from deep_translator import GoogleTranslator
from django.shortcuts import redirect
from django.contrib import messages
from langdetect import detect, LangDetectException
from apps.chat.services.language_detector import detectar_idioma
import requests, json
from django.views.decorators.csrf import csrf_exempt
from .models import Chat, Progress, ProgressTmp
import re

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.conf import settings
from django.apps import apps
from datetime import timedelta
from django.db.models import Sum






LESSON_TITLES = {
    1: "Usando verbos",
    2: "Expressões populares",
    3: "Utilidades diárias",
}


def chat_home(request):
    return render(request, "chat/chat.html", {
        "lesson_id": None,
        "lines": [],
        "username": request.session.get(
            "username",
            request.user.first_name if request.user.is_authenticated else ""
        ),
    })

def index(request):
    return render(request, "chat/index.html")

def limpar_html(text):
    return re.sub(r"<[^>]+>", "", text)

def norm(s):
    return s.strip().lower()

# TROCAR MARCADORES
def normalizar_marcadores(text):
    if not text:
        return text

    trocas = {
        "(stp0)": ",",
        "(stp1)": ".", # atencao usar esse quebra a frase com uma pausa
        "(stp2)": "—",
        "(stp3)": "— —",
    }

    for k, v in trocas.items():
        text = text.replace(k, v)

    return text

# LIMPAR VISUALMENTE
def limpar_visual(text):
    if not text:
        return text

    esconder = ["(stp0)", "(stp1)", "(stp2)", "(stp3)"]

    for k in esconder:
        text = text.replace(k, "")

    return text

# QUEBRAR AS FRASES POR . : ! ? OU (q)
def quebrar_frases(text):
    if not text:
        return []
    
    partes = re.split(r'[.:!?]', text)

    # limpa espaços e descarta vazios
    return [p.strip() for p in partes if p.strip()]  

# CHAMAR O CHAT NO HTML
def chat(request, lesson_id):
    
    user = request.user
    now = timezone.now()
    
    # DELETE > 2 dias (aqui, na tabela progress_tmp)
    limite = timezone.now() - timedelta(days=2)
    ProgressTmp.objects.filter(updated_at__lt=limite).delete()
    # FIM DELETE > 2 dias (aqui, na tabela progress_tmp)
    
    # 2) Hoje (janela diária)
    inicio_dia = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 3) Frases bloqueadas hoje (>= 5 pontos no dia)
    chats_bloqueados_hoje = (
        ProgressTmp.objects
        .filter(
            user_id=user.id,
            updated_at__gte=inicio_dia
        )
        .values("chat_id")
        .annotate(total=Sum("points"))
        .filter(total__gte=20)
        .values_list("chat_id", flat=True)
    )
    
    lines = (
        Chat.objects
        .filter(lesson_id=lesson_id, status=True)
        .exclude(id__in=chats_bloqueados_hoje)
        .order_by("seq")
    )

    for l in lines:
        l.content_pt = limpar_visual(l.content_pt)
    
    username = request.session.get(
        "username",
        user.first_name if user.is_authenticated else ""
    )
    
    lesson_title = LESSON_TITLES.get(lesson_id, f"Lição {lesson_id}")

    return render(request, "chat/chat.html", {
        "lesson_id": lesson_id,
        "lesson_title": lesson_title,
        "lines": lines,
        "username": username,
    }) 
    
 
# ENVIAR PARA CRIACAO DE AUDIOS
@csrf_exempt
def tts_line(request):
    data = json.loads(request.body)

    files = []

    if data.get("text"):
        texto = limpar_html(data.get("text"))
        texto = normalizar_marcadores(texto)
        frases = quebrar_frases(texto)

        for frase in frases:
            frase = frase.strip()
            if not frase:
                continue

            frase_n = norm(frase)

            if term_exists("pt", frase_n):
                lang = "pt"
            elif term_exists("en", frase_n):
                lang = "en"
            else:
                lang = detectar_idioma(frase)

            r = requests.post(
                "http://127.0.0.1:9000",
                json={
                    "text": frase,
                    "lang": lang,
                    "fixed": False  # feedback NÃO é do banco
                },
                timeout=20
            )

            files.append(r.json()["file"])

        return JsonResponse({"files": files})

    # =========================
    # 2) MODO NORMAL (BANCO)
    # =========================
    line = Chat.objects.get(id=data.get("line_id"))

    texto = limpar_html(line.content_pt)
    texto = normalizar_marcadores(texto)
    frases = quebrar_frases(texto)

    for frase in frases:
        frase = frase.strip()
        if not frase:
            continue

        frase_n = norm(frase)

        if term_exists("pt", frase_n):
            lang = "pt"
        elif term_exists("en", frase_n):
            lang = "en"
        else:
            lang = detectar_idioma(frase)

        fixed = bool(line.status_point)

        r = requests.post(
            "http://127.0.0.1:9000",
            json={
                "text": frase,
                "lang": lang,
                "fixed": fixed
            },
            timeout=20
        )

        files.append(r.json()["file"])

    return JsonResponse({"files": files})

@csrf_exempt
def tts(request):
    data = json.loads(request.body)
    text = data.get("text")

    r = requests.post(
        "http://127.0.0.1:9000",
        json={"text": text},
        timeout=20
    )
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
    term = request.POST.get("term")
    term = re.sub(r"[.:!?]", "", term)
    term = term.lower().strip()

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


# CADASTRAR NA TABELA progress e editar    
@csrf_exempt
def save_progress(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "invalid method"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "not authenticated"}, status=401)

    try:
        data = json.loads(request.body)

        chat_id = int(data.get("chat_id"))
        lesson_id = int(data.get("lesson_id"))
        points = int(data.get("points"))

        user_id = request.user.id

    except Exception:
        return JsonResponse({"error": "Dados inválidos"}, status=400)

    Progress = apps.get_model("chat", "Progress")

    if not Chat.objects.filter(id=chat_id).exists():
        return JsonResponse(
            {"ok": False, "error": "chat_id inexistente"},
            status=400
        )

    with transaction.atomic():
        obj, created = Progress.objects.get_or_create(
            user_id=user_id,
            chat_id=chat_id,
            defaults={
                "lesson_id": lesson_id,
                "points": points,
                "status": 0,
                "stage": 0,
            }
        )

        if not created:
            obj.points += points
            obj.updated_at = timezone.now()
            obj.save(update_fields=["points", "updated_at"])


    return JsonResponse({
        "ok": True,
        "created": created
    })

# CADASTRAR NA TABELA progress_tmp    
@csrf_exempt
def save_progress_tmp(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "invalid method"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "not authenticated"}, status=401)

    try:
        data = json.loads(request.body)

        chat_id = int(data.get("chat_id"))
        points = int(data.get("points"))

        user_id = request.user.id

    except Exception:
        return JsonResponse({"error": "Dados inválidos"}, status=400)

    if not Chat.objects.filter(id=chat_id).exists():
        return JsonResponse(
            {"ok": False, "error": "chat_id inexistente"},
            status=400
        )

    ProgressTmp = apps.get_model("chat", "ProgressTmp")

    ProgressTmp.objects.create(
        user_id=user_id,
        chat_id=chat_id,
        points=points
    )

    return JsonResponse({
        "ok": True
    })
