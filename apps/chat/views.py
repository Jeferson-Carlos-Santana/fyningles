from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .utils.dictionary_writer import add_term, term_exists, delete_term, list_terms
from deep_translator import GoogleTranslator
from django.contrib import messages
from langdetect import detect, LangDetectException
from apps.chat.services.language_detector import detectar_idioma
from django.views.decorators.csrf import csrf_exempt
from .models import Chat, Progress, ProgressTmp, UserNivel
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.conf import settings
from django.apps import apps
from datetime import timedelta
from django.db.models import Sum
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from .forms_register_user import RegisterUserForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.views import PasswordResetView
from apps.chat.services.speech_evaluator import evaluate
import requests, json, re, math


# TOTAL DE PONTOS POR DIA
TOTAL_POINTS_DAY = 5

# DIAS QUE AS FRASES NAO APARECE
SUSPIRO = 3

LESSON_TITLES = {
    1: "Frases",
    2: "Presente simples (to have)",
    3: "Presente contínuo (to have)",
    4: "Frases longas",
}


@csrf_exempt
def speech_evaluate(request):
    if request.method != "POST":
        return JsonResponse({"error": "invalid method"}, status=405)

    data = json.loads(request.body.decode("utf-8"))
    expected = data.get("expected", "")
    spoken   = data.get("spoken", "")

    return JsonResponse(evaluate(expected, spoken))


def resend_activation(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if not user:
            return render(request, "chat/resend_activation.html", {
                "error": "E-mail não encontrado."
            })

        if user.is_active:
            return render(request, "chat/resend_activation.html", {
                "error": "Esta conta já está ativada."
            })

        # nivel = user.nivel
        nivel, _ = UserNivel.objects.get_or_create(user=user)
        now = timezone.now()

        # RATE LIMIT — 15 minutos
        if nivel.last_activation_sent_at and now - nivel.last_activation_sent_at < timedelta(minutes=15):
            return render(request, "chat/resend_activation.html", {
                "error": "Aguarde alguns minutos antes de reenviar o e-mail."
            })

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = request.build_absolute_uri(
            reverse("activate", kwargs={"uidb64": uid, "token": token})
        )

        send_mail(
            "Reenvio de ativação",
            f"Clique no link para ativar sua conta:\n{activation_link}",
            None,
            [user.email],
        )

        nivel.last_activation_sent_at = now
        nivel.save(update_fields=["last_activation_sent_at"])

        return redirect("login")

    return render(request, "chat/resend_activation.html")


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("login")

    return HttpResponse("Link de ativação inválido ou expirado.")


class ActiveOnlyPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = User.objects.filter(email=email).first()

        if user and not user.is_active:
            form.add_error("email", "Conta não ativada. Reenvie o e-mail de ativação.")
            return self.form_invalid(form)

        if user:
            # nivel = user.nivel
            nivel, _ = UserNivel.objects.get_or_create(user=user)
            now = timezone.now()

            # RATE LIMIT — 15 minutos
            if (
                nivel.last_password_reset_sent_at
                and now - nivel.last_password_reset_sent_at < timedelta(minutes=15)
            ):
                form.add_error("email", "Aguarde alguns minutos antes de tentar novamente.")
                return self.form_invalid(form)

            # marca envio
            nivel.last_password_reset_sent_at = now
            nivel.save(update_fields=["last_password_reset_sent_at"])

        return super().form_valid(form)


def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            activation_link = request.build_absolute_uri(
                reverse("activate", kwargs={"uidb64": uid, "token": token})
            )

            send_mail(
                "Ative sua conta",
                f"Clique no link para ativar sua conta:\n{activation_link}",
                None,
                [user.email],
            )

            return redirect("login")            
            
    else:
        form = RegisterUserForm()

    return render(request, "chat/register_user.html", {
        "form": form
    })    

# FRASES CONCLUIDAS
# @login_required
def phrase_completed(request):
    user = request.user

    # nível do usuário
    try:
        nivel = UserNivel.objects.get(user=user).nivel
    except UserNivel.DoesNotExist:
        nivel = 1

    limite_por_frase = {
        1: 165,
        2: 215,
        3: 265,
    }.get(nivel, 165)

    progressos = (
        Progress.objects
        .filter(user=user, points__gte=limite_por_frase)  # SOMENTE 100%
        .select_related("chat")
        .order_by("-points")[:1000]
    )

    frases = []
    for p in progressos:
        percent = min(int((p.points / limite_por_frase) * 100), 100)

        frases.append({
            "chat_id": p.chat_id,
            "text": (p.chat.expected_en or "").strip(),
            "text_pt": (p.chat.expected_pt or "").strip(),
            "percent": percent,
        })

    frases.sort(key=lambda f: f["percent"], reverse=True)

    return render(request, "chat/phrase_completed.html", {
        "frases": frases,
        "credit_display": get_credit_display(request.user),
    })

# FIM FRASES CONCLUIDAS

# FRASES QUE ESTAO EM ANDAMENTO, POR USUARIO SESSAO ID, MARCANDO O PERCENTUAL EM BARRAS
# @login_required
def phrase_progress(request):
    user = request.user

    # nível do usuário
    try:
        nivel = UserNivel.objects.get(user=user).nivel
    except UserNivel.DoesNotExist:
        nivel = 1

    limite_por_frase = {
        1: 165,
        2: 215,
        3: 265,
    }.get(nivel, 165)

    progressos = (
        Progress.objects
        .filter(user=user, points__lt=limite_por_frase) # aqui tira o 100% das frases em processo
        .filter(user=user)
        .select_related("chat")
        .order_by("-points")[:1000] # limita frases em andamento para usuario
    )

    frases = []
    for p in progressos:
        percent = min(int((p.points / limite_por_frase) * 100), 100)

        frases.append({
            "chat_id": p.chat_id,
            "text": (p.chat.expected_en or "").strip(),
            "text_pt": (p.chat.expected_pt or "").strip(),
            "percent": percent,
        })
    frases.sort(key=lambda f: f["percent"], reverse=True)
    return render(request, "chat/phrase_progress.html", {
        "frases": frases,
        "credit_display": get_credit_display(request.user),
    })
# FIM FRASES QUE ESTAO EM ANDAMENTO, POR USUARIO SESSAO ID, MARCANDO O PERCENTUAL EM BARRAS

# MODIFICA O PERCENTUAL DAS FRASES
@csrf_exempt
# @login_required
@require_POST
def mark_learned(request):
    try:
        data = json.loads(request.body)
        chat_id = int(data.get("chat_id"))
        percent = int(data.get("percent", 100))
        if percent not in (25, 50, 75, 100):
            raise ValueError
    except Exception:
        return JsonResponse({"ok": False, "error": "Dados inválidos"}, status=400)

    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return JsonResponse({"ok": False, "error": "chat_id inexistente"}, status=400)

    try:
        nivel = UserNivel.objects.get(user=request.user).nivel
    except UserNivel.DoesNotExist:
        nivel = 1

    max_points = {1: 165, 2: 215, 3: 265}.get(nivel, 165)
    
    points = math.ceil(max_points * percent / 100)

    with transaction.atomic():
        try:            
            user_nivel = UserNivel.objects.select_for_update().get(user=request.user)
        except UserNivel.DoesNotExist:
            return JsonResponse({"ok": False, "error": "nivel inexistente"}, status=400)

        creditos_disponiveis = user_nivel.earned_credit - user_nivel.spent_credit

        if creditos_disponiveis <= 0:
            return JsonResponse({"ok": False, "error": "sem_credito"}, status=403)

        # consome 1 crédito
        user_nivel.spent_credit += 1
        user_nivel.save(update_fields=["spent_credit"])

        obj, _ = Progress.objects.get_or_create(
            user=request.user,
            chat=chat,
            defaults={"lesson_id": chat.lesson_id, "points": 0}
        )

        # converte nivel -> NIVEL interno
        if nivel == 1:
            NIVEL = 0
        elif nivel == 2:
            NIVEL = 5
        elif nivel == 3:
            NIVEL = 10
        else:
            NIVEL = 0

        # limites de stage
        STAGES = [
            (25  + NIVEL*1,  1),
            (50  + NIVEL*2,  2),
            (70  + NIVEL*3,  3),
            (90  + NIVEL*4,  4),
            (105 + NIVEL*5,  5),
            (120 + NIVEL*6,  6),
            (130 + NIVEL*7,  7),
            (140 + NIVEL*8,  8),
            (145 + NIVEL*9,  9),
            (150 + NIVEL*10, 10),
            (155 + NIVEL*10, 11),
            (160 + NIVEL*10, 12),
            (165 + NIVEL*10, 13),
        ]

        stage = 0
        for limite, s in STAGES:
            if points >= limite:
                stage = s

        obj.lesson_id = chat.lesson_id
        obj.points = points
        obj.stage = stage

        if percent == 100:
            obj.status = 1
            obj.concluded_at = timezone.now()
        else:
            obj.status = 0
            obj.concluded_at = None

        obj.save(update_fields=[
            "lesson_id", "points", "stage", "status", "concluded_at"
        ])

    return JsonResponse({"ok": True, "points": points})

# FIM MODIFICA O PERCENTUAL DAS FRASES
# @login_required
def chat_home(request):
    return render(request, "chat/chat.html", {
        "lesson_id": None,
        "lines": [],
        "username": request.session.get(
            "username",
            request.user.first_name if request.user.is_authenticated else ""
        ),
        "credit_display": get_credit_display(request.user),
    })

# @login_required
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
        "(a)": "",
        "(as)": "",
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

    partes = re.findall(r'[^.!?:]+[.!?:]?', text)
    return [p.strip() for p in partes if p.strip()]


# MOSTRAR SEMPRE O NUMERO DE CREDITOS
def get_credit_display(user):
    try:
        user_nivel = UserNivel.objects.get(user=user)
    except UserNivel.DoesNotExist:
        return 0

    total_points = (
        Progress.objects
        .filter(user=user)
        .aggregate(total=Sum("points"))
        .get("total") or 0
    )

    blocos = total_points // 5000

    if blocos > user_nivel.earned_credit:
        user_nivel.earned_credit = blocos
        user_nivel.save(update_fields=["earned_credit"])

    return user_nivel.earned_credit - user_nivel.spent_credit


# CHAMAR O CHAT NO HTML
# @login_required
def chat(request, lesson_id):
    
    user = request.user
    now = timezone.now() 
    
    # NIVEL condicionado pelo banco
    try:
        nivel_db = UserNivel.objects.get(user=request.user).nivel
    except UserNivel.DoesNotExist:
        nivel_db = 1

    if nivel_db == 1:
        NIVEL = 0
    elif nivel_db == 2:
        NIVEL = 5
    elif nivel_db == 3:
        NIVEL = 10
    else:
        NIVEL = 0
        
    STAGE_1  = 25 + (NIVEL * 1)   # 25  30  35
    STAGE_2  = 50 + (NIVEL * 2)   # 50  60  70
    STAGE_3  = 70 + (NIVEL * 3)   # 70  85  100 
    STAGE_4  = 90 + (NIVEL * 4)   # 90  110 130
    STAGE_5  = 105 + (NIVEL * 5)  # 105 130 155
    STAGE_6  = 120 + (NIVEL * 6)  # 120 150 180
    STAGE_7  = 130 + (NIVEL * 7)  # 130 165 200
    STAGE_8  = 140 + (NIVEL * 8)  # 140 180 220
    STAGE_9  = 145 + (NIVEL * 9)  # 145 190 235
    STAGE_10 = 150 + (NIVEL * 10) # 150 200 250
    STAGE_11 = STAGE_10 + 5
    STAGE_12 = STAGE_11 + 5
    STAGE_13 = STAGE_12 + 5

    # DIAS PARA  STAGE_DAYS
    DAY_1  = (STAGE_1 // 5) + SUSPIRO                  #  8    9   10
    DAY_2  = ((STAGE_2 - STAGE_1) // 5) + SUSPIRO      #  8    9   10
    DAY_3  = ((STAGE_3 - STAGE_2) // 5) + SUSPIRO      #  7    8   9
    DAY_4  = ((STAGE_4 - STAGE_3) // 5) + SUSPIRO      #  7    8   9
    DAY_5  = ((STAGE_5 - STAGE_4) // 5) + SUSPIRO      #  6    7   8
    DAY_6  = ((STAGE_6 - STAGE_5) // 5) + SUSPIRO      #  6    7   8
    DAY_7  = ((STAGE_7 - STAGE_6) // 5) + SUSPIRO      #  5    6   7
    DAY_8  = ((STAGE_8 - STAGE_7) // 5) + SUSPIRO      #  5    6   7
    DAY_9  = ((STAGE_9 - STAGE_8) // 5) + SUSPIRO      #  4    5   6
    DAY_10 = ((STAGE_10 - STAGE_9) // 5) + SUSPIRO     #  4    5   6
                                                    #  60   70  80
    # DIAS PARA EXECUTAR OS PONTOS EM CADA ESTAGIO
    STAGE_DAYS_1  = DAY_1    
    STAGE_DAYS_2  = DAY_2
    STAGE_DAYS_3  = DAY_3    
    STAGE_DAYS_4  = DAY_4 
    STAGE_DAYS_5  = DAY_5     
    STAGE_DAYS_6  = DAY_6
    STAGE_DAYS_7  = DAY_7     
    STAGE_DAYS_8  = DAY_8
    STAGE_DAYS_9  = DAY_9     
    STAGE_DAYS_10 = DAY_10
    STAGE_DAYS_11 = 30
    STAGE_DAYS_12 = 30
    STAGE_DAYS_13 = 30
    
    # NOVO CÓDIGO — REVALIDA STATUS PELO TEMPO (CHAT)
    STAGE_DAYS = {
        1: STAGE_DAYS_1,
        2: STAGE_DAYS_2,
        3: STAGE_DAYS_3,
        4: STAGE_DAYS_4,
        5: STAGE_DAYS_5,
        6: STAGE_DAYS_6,
        7: STAGE_DAYS_7,
        8: STAGE_DAYS_8,
        9: STAGE_DAYS_9,
        10: STAGE_DAYS_10,
        11: STAGE_DAYS_11,
        12: STAGE_DAYS_12,
        13: STAGE_DAYS_13,
    }

    progressos_bloqueados = Progress.objects.filter(
        user_id=user.id,
        status=1
    )

    for p in progressos_bloqueados:
        if not p.concluded_at or p.stage == 0:
            continue

        dias_minimos = STAGE_DAYS.get(p.stage)
        if dias_minimos is None:
            continue

        dias_passados = (now.date() - p.concluded_at.date()).days
        
        if p.stage == 13 and p.points >= STAGE_13:
            continue  # nunca reabre

        if dias_passados >= dias_minimos:
            p.status = 0
            p.save(update_fields=["status"]) 
    
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
        .filter(total__gte=TOTAL_POINTS_DAY)
        .values_list("chat_id", flat=True)
    )
    
    # CHATS BLOQUEADOS PELO STATUS (progress)
    chats_bloqueados_status = (
        Progress.objects
        .filter(
            user_id=user.id,
            status=1
        )
        .values_list("chat_id", flat=True)
    )
    # FIM # CHATS BLOQUEADOS PELO STATUS (progress)
    
    lines = (
        Chat.objects
        .filter(lesson_id=lesson_id, status=True)
        .exclude(id__in=chats_bloqueados_hoje)
        .exclude(id__in=chats_bloqueados_status)
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
        "credit_display": get_credit_display(request.user),
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

# LISTAR DADOS DO JSON
# @login_required
def dictionary(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Acesso restrito ao superadmin")
    lang = request.GET.get("lang", "pt")  # padrão pt
    terms = list_terms(lang)

    return render(request, "chat/dictionary.html", {
        "lang": lang,
        "terms": terms
    })
# FIM LISTAR DADOS DO JSON

# ADICIONAR DADOS NO JSON
# @login_required
def dictionary_add(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Acesso restrito ao superadmin")
    if request.method != "POST":
        # return redirect("dictionary")
        return redirect(f"/dictionary/?lang={lang}")

    lang = request.POST.get("lang")
    term = request.POST.get("term")
    term = re.sub(r"[.:!?]", "", term)
    term = term.lower().strip()

    if not lang or not term:
        messages.error(request, "Preencha o idioma e a palavra.")
        return redirect(f"/dictionary/?lang={lang}")

    if term_exists(lang, term):
        messages.error(request, "Esta palavra ou frase já existe.")
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
# @login_required
def dictionary_delete(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Acesso restrito ao superadmin")
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
    
    # NIVEL condicionado pelo banco
    try:
        nivel_db = UserNivel.objects.get(user=request.user).nivel
    except UserNivel.DoesNotExist:
        nivel_db = 1

    if nivel_db == 1:
        NIVEL = 0
    elif nivel_db == 2:
        NIVEL = 5
    elif nivel_db == 3:
        NIVEL = 10
    else:
        NIVEL = 0
        
    STAGE_1  = 25 + (NIVEL * 1)   # 25  30  35
    STAGE_2  = 50 + (NIVEL * 2)   # 50  60  70
    STAGE_3  = 70 + (NIVEL * 3)   # 70  85  100 
    STAGE_4  = 90 + (NIVEL * 4)   # 90  110 130
    STAGE_5  = 105 + (NIVEL * 5)  # 105 130 155
    STAGE_6  = 120 + (NIVEL * 6)  # 120 150 180
    STAGE_7  = 130 + (NIVEL * 7)  # 130 165 200
    STAGE_8  = 140 + (NIVEL * 8)  # 140 180 220
    STAGE_9  = 145 + (NIVEL * 9)  # 145 190 235
    STAGE_10 = 150 + (NIVEL * 10) # 150 200 250
    STAGE_11 = STAGE_10 + 5
    STAGE_12 = STAGE_11 + 5
    STAGE_13 = STAGE_12 + 5

    # DIAS PARA  STAGE_DAYS
    DAY_1  = (STAGE_1 // 5) + SUSPIRO                  #  8    9   10
    DAY_2  = ((STAGE_2 - STAGE_1) // 5) + SUSPIRO      #  8    9   10
    DAY_3  = ((STAGE_3 - STAGE_2) // 5) + SUSPIRO      #  7    8   9
    DAY_4  = ((STAGE_4 - STAGE_3) // 5) + SUSPIRO      #  7    8   9
    DAY_5  = ((STAGE_5 - STAGE_4) // 5) + SUSPIRO      #  6    7   8
    DAY_6  = ((STAGE_6 - STAGE_5) // 5) + SUSPIRO      #  6    7   8
    DAY_7  = ((STAGE_7 - STAGE_6) // 5) + SUSPIRO      #  5    6   7
    DAY_8  = ((STAGE_8 - STAGE_7) // 5) + SUSPIRO      #  5    6   7
    DAY_9  = ((STAGE_9 - STAGE_8) // 5) + SUSPIRO      #  4    5   6
    DAY_10 = ((STAGE_10 - STAGE_9) // 5) + SUSPIRO     #  4    5   6
                                                    #  60   70  80
    # DIAS PARA EXECUTAR OS PONTOS EM CADA ESTAGIO
    STAGE_DAYS_1  = DAY_1    
    STAGE_DAYS_2  = DAY_2
    STAGE_DAYS_3  = DAY_3    
    STAGE_DAYS_4  = DAY_4 
    STAGE_DAYS_5  = DAY_5     
    STAGE_DAYS_6  = DAY_6
    STAGE_DAYS_7  = DAY_7     
    STAGE_DAYS_8  = DAY_8
    STAGE_DAYS_9  = DAY_9     
    STAGE_DAYS_10 = DAY_10
    STAGE_DAYS_11 = 30
    STAGE_DAYS_12 = 30
    STAGE_DAYS_13 = 30

    with transaction.atomic():
        obj, created = Progress.objects.get_or_create(
            user_id=user_id,
            chat_id=chat_id,
            defaults={
                "lesson_id": lesson_id,
                "points": points,
                "status": 0,
                "stage": 0,
                "concluded_at": timezone.now(),  # mantém coerência no INSERT
            }
        )

        if not created:
            obj.points += points
            obj.updated_at = timezone.now()            
       
            # DETECTA TROCA DE STAGE           
            stage_anterior = obj.stage
            # FIM DETECTA TROCA DE STAGE  
          
            STAGES = [
                (STAGE_13, 13),
                (STAGE_12, 12),
                (STAGE_11, 11),
                (STAGE_10, 10),
                (STAGE_9, 9),
                (STAGE_8, 8),
                (STAGE_7, 7),
                (STAGE_6, 6),
                (STAGE_5, 5),
                (STAGE_4, 4),
                (STAGE_3, 3),
                (STAGE_2, 2),
                (STAGE_1, 1),
            ]

            for limite, stage in STAGES:
                if obj.points >= limite and obj.stage < stage:
                    obj.stage = stage
                    break                

            # ATUALIZA concluded_at SE O STAGE MUDOU
            if obj.stage != stage_anterior:
                obj.concluded_at = timezone.now()
            # FIM ATUALIZA concluded_at SE O STAGE MUDOU           
            
            # REGRA DE TEMPO POR STAGE (STATUS)
            STAGE_DAYS = {
                1: STAGE_DAYS_1,
                2: STAGE_DAYS_2,
                3: STAGE_DAYS_3,
                4: STAGE_DAYS_4,
                5: STAGE_DAYS_5,
                6: STAGE_DAYS_6,
                7: STAGE_DAYS_7,
                8: STAGE_DAYS_8,
                9: STAGE_DAYS_9,
                10: STAGE_DAYS_10,
                11: STAGE_DAYS_11,
                12: STAGE_DAYS_12,
                13: STAGE_DAYS_13,
            }
            
             # REGRA DEFINITIVA DO STAGE 13
            if obj.points >= STAGE_13:
                obj.stage = 13
                obj.status = 1
                obj.concluded_at = timezone.now()
            else:
                dias_minimos = STAGE_DAYS.get(obj.stage)
                if dias_minimos and obj.concluded_at:
                    dias_passados = (timezone.now().date() - obj.concluded_at.date()).days
                    obj.status = 1 if dias_passados < dias_minimos else 0                       
            
            obj.save(update_fields=["points", "updated_at", "stage", "concluded_at", "status"])

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

# CONTA O TOTAL DOS PONTOS DE CADA USUARIO
# @login_required
def total_points(request):
    total = (
        Progress.objects
        .filter(user=request.user)
        .aggregate(total=Sum("points"))
        .get("total") or 0
    )

    return JsonResponse({
        "total": total
    })

# PONTOS FEITOS NO MESMO DIA
# @login_required
def points_feitos(request):
    now = timezone.now()
    inicio_dia = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total = (
        ProgressTmp.objects
        .filter(
            user=request.user,
            updated_at__gte=inicio_dia
        )
        .aggregate(total=Sum("points"))
        .get("total") or 0
    )

    return JsonResponse({
        "total": total
    })

# VERIFICA O NIVEL DO USUARIO
# @login_required
@require_GET
def user_nivel_get(request):
    try:
        obj = UserNivel.objects.get(user=request.user)
        return JsonResponse({
            "exists": True,
            "nivel": obj.nivel
        })
    except UserNivel.DoesNotExist:
        return JsonResponse({
            "exists": False
        })

# CADASTRA USANDO A MODAL DO NIVEL
# @login_required
@require_POST
def user_nivel_set(request):
    if UserNivel.objects.filter(user=request.user).exists():
        return JsonResponse({"error": "nivel já definido"}, status=400)

    data = json.loads(request.body)
    nivel = int(data.get("nivel", 0))

    if nivel not in (1, 2, 3):
        return JsonResponse({"error": "nivel inválido"}, status=400)

    UserNivel.objects.create(
        user=request.user,
        nivel=nivel
    )

    return JsonResponse({"ok": True})




