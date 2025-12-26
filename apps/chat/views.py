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
import re





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

def limpar_html(text):
    return re.sub(r"<[^>]+>", "", text)

def quebrar_frases(text):
    return [f.strip() for f in re.split(r'[.:!?]', text) if f.strip()]


@csrf_exempt
def tts_line(request):
    data = json.loads(request.body)
    line = Chat.objects.get(id=data.get("line_id"))

    texto = limpar_html(line.content_pt)
    frases = quebrar_frases(texto)

    files = []

    for frase in frases:
        frase = frase.strip()
        if not frase:
            continue

        # 🎯 DECISÃO SIMPLES E FUNCIONAL
        try:
            idioma = detect(frase)
        except:
            idioma = "en"

        if idioma == "pt":
            lang = "pt"
        else:
            lang = "en"

        r = requests.post(
            "http://127.0.0.1:9000",
            json={
                "text": frase,
                "lang": lang
            },
            timeout=20
        )

        files.append(r.json()["file"])

    return JsonResponse({"files": files})






# @csrf_exempt
# def tts_line(request):
#     data = json.loads(request.body)
#     line_id = data.get("line_id")

#     line = Chat.objects.get(id=line_id)
#     frases = quebrar_frases(limpar_html(line.content_pt))

#     files = []
#     for frase in frases:
#         r = requests.post(
#             "http://127.0.0.1:9000",
#             json={"text": frase},
#             timeout=20
#         )
#         files.append(r.json()["file"])

#     return JsonResponse({"files": files})

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

