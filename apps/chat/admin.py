from django.contrib import admin
from .models import Chat
import random, re
from deep_translator import GoogleTranslator
from django.db import models
from django import forms
from .admin_forms import ChatAdminForm
from django.utils.html import format_html
import time

@admin.action(description="Marcar status = ATIVO")
def marcar_status_ativo(modeladmin, request, queryset):
    queryset.update(status=True)

@admin.action(description="Marcar status = INATIVO")
def marcar_status_inativo(modeladmin, request, queryset):
    queryset.update(status=False)
 
# IMPLEMENTACAO 1
def traduz_com_retry(en_full, tentativas=2, espera=1):
    for _ in range(tentativas):
        try:
            return {
                "pt": GoogleTranslator(source="en", target="pt").translate(en_full),
                "es": GoogleTranslator(source="en", target="es").translate(en_full),
                "fr": GoogleTranslator(source="en", target="fr").translate(en_full),
                "it": GoogleTranslator(source="en", target="it").translate(en_full),
            }
        except Exception:
            time.sleep(espera)
    return {"pt": None, "es": None, "fr": None, "it": None}

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
  
  def Sequencia(self, obj):
    if obj.role == "pt-mark":
        color = "pink"
    elif obj.role == "single-mark":
        color = "#00ff80"
    elif obj.role == "teacher":
        color = "transparent"
    else:
        return obj.seq

    return format_html(
        '<span style="background:{}; '
        'display:flex; '
        'border-radius:50%; '
        'padding:2px 5px; '
        'align-items:center; '
        'justify-content:center;">{}</span>',
        color,
        obj.seq
    )

  Sequencia.short_description = ""
  
  form = ChatAdminForm
  # ORDEM DO FORM
  fields = (
    "lesson_id",
    "seq",
    "role",
    "lang",
    "status",
    "auto",
    "end",
    "status_point",
    "template_choice",
    "expected_en",
    "expected_pt",
    "expected_it",
    "expected_fr",
    "expected_es",
    "content_pt",
    "content_it",
    "content_fr",
    "content_es",
  )
  # LISTA DO QUE APARECE NA TABELA
  list_display = (
    "Sequencia",
    "lesson_id",    
    "status",
    "auto",
    "end",
    "status_point",
    "expected_pt",
    "expected_en",
    "expected_it",
    "expected_fr",
    "expected_es",
    "role",
    "lang",
    "created_at",
  )
  list_editable = ("status", "auto", "end", "status_point")
  # DEFINE CAMPOS COM 100%
  formfield_overrides = {
    models.CharField: {
        "widget": forms.TextInput(attrs={"style": "width: 100%;"})
    },
    models.TextField: {
        "widget": forms.Textarea(attrs={"style": "width: 100%;"})
    },
  }
  
  actions = [
        marcar_status_ativo,
        marcar_status_inativo,
    ]
  
  list_filter = ("lesson_id",)
 
  search_fields = (
    "expected_en",
    "expected_pt",
    "expected_it",
    "expected_fr",
    "expected_es",
    "content_pt",
    "content_it",
    "content_fr",
    "content_es",
  )
  
  ordering = ("lesson_id", "-seq")
  sortable_by = ()
  list_per_page = 100
  
  # FUNCAO INFORMAL
  def gerar_informal(self, frase: str) -> str:
    reducoes = {
      r"\bgoing to\b": "gonna",
      r"\bgot to\b": "gotta",
      r"\bwant to\b": "wanna",
      r"\bhave to\b": "hafta",
      r"\bout of\b": "outta",
      r"\bkind of\b": "kinda",
      r"\bsort of\b": "sorta",
      r"\blet me\b": "lemme",
      r"\bgive me\b": "gimme",
      r"\bam not\b": "ain't",
      r"\bbecause\b": "cuz",
      r"\btrying to\b": "tryna",
      r"\bgoing\b": "gon'"
  }
    for padrao, reduzida in reducoes.items():
        frase = re.sub(padrao, reduzida, frase, flags=re.IGNORECASE)
    return frase
 
  # // PRECISA ANDAR ALINHADDA COM A LISTA QUE ESTA NO ADMIN.PY
  def contract_en(self, t: str) -> str:
    reps = [
    (r"\bI am\b", "I'm"), (r"\bi am\b", "i'm"),
    (r"\bYou are\b", "You're"), (r"\byou are\b", "you're"),
    (r"\bWe are\b", "We're"), (r"\bwe are\b", "we're"),
    (r"\bThey are\b", "They're"), (r"\bthey are\b", "they're"),
    (r"\bI have\b", "I've"), (r"\bi have\b", "i've"),
    (r"\bYou have\b", "You've"), (r"\byou have\b", "you've"),
    (r"\bWe have\b", "We've"), (r"\bwe have\b", "we've"),
    (r"\bThey have\b", "They've"), (r"\bthey have\b", "they've"),
    (r"\bI will\b", "I'll"), (r"\bi will\b", "i'll"),
    (r"\bYou will\b", "You'll"), (r"\byou will\b", "you'll"),
    (r"\bWe will\b", "We'll"), (r"\bwe will\b", "we'll"),
    (r"\bThey will\b", "They'll"), (r"\bthey will\b", "they'll"),
    (r"\bDo not\b", "Don't"), (r"\bdo not\b", "don't"),
    (r"\bDoes not\b", "Doesn't"), (r"\bdoes not\b", "doesn't"),
    (r"\bDid not\b", "Didn't"), (r"\bdid not\b", "didn't"),
    (r"\bWill not\b", "Won't"), (r"\bwill not\b", "won't"),
    (r"\bIs not\b", "Isn't"), (r"\bis not\b", "isn't"),
    (r"\bAre not\b", "Aren't"), (r"\bare not\b", "aren't"),
    (r"\bWere not\b", "Weren't"), (r"\bwere not\b", "weren't"),
    (r"\bHe is\b", "He's"), (r"\bhe is\b", "he's"),
    (r"\bShe is\b", "She's"), (r"\bshe is\b", "she's"),
    (r"\bIt is\b", "It's"), (r"\bit is\b", "it's"),
    (r"\bThat is\b", "That's"), (r"\bthat is\b", "that's"),
    (r"\bThere is\b", "There's"), (r"\bthere is\b", "there's"),
    (r"\bThere are\b", "There're"), (r"\bthere are\b", "there're"),
    (r"\bWho is\b", "Who's"), (r"\bwho is\b", "who's"),
    (r"\bWhat is\b", "What's"), (r"\bwhat is\b", "what's"),
    (r"\bWhere is\b", "Where's"), (r"\bwhere is\b", "where's"),
    (r"\bWhen is\b", "When's"), (r"\bwhen is\b", "when's"),
    (r"\bHow is\b", "How's"), (r"\bhow is\b", "how's"),
    (r"\bI had\b", "I'd"), (r"\bi had\b", "i'd"),
    (r"\bYou had\b", "You'd"), (r"\byou had\b", "you'd"),
    (r"\bHe had\b", "He'd"), (r"\bhe had\b", "he'd"),
    (r"\bShe had\b", "She'd"), (r"\bshe had\b", "she'd"),
    (r"\bWe had\b", "We'd"), (r"\bwe had\b", "we'd"),
    (r"\bThey had\b", "They'd"), (r"\bthey had\b", "they'd"),
    (r"\bCould not\b", "Couldn't"), (r"\bcould not\b", "couldn't"),
    (r"\bShould not\b", "Shouldn't"), (r"\bshould not\b", "shouldn't"),
    (r"\bWould not\b", "Wouldn't"), (r"\bwould not\b", "wouldn't"),
    (r"\bMust not\b", "Mustn't"), (r"\bmust not\b", "mustn't"),
    (r"\bMay not\b", "Mayn't"), (r"\bmay not\b", "mayn't"),
    (r"\bMight not\b", "Mightn't"), (r"\bmight not\b", "mightn't"),
    (r"\bHas not\b", "Hasn't"), (r"\bhas not\b", "hasn't"),
    (r"\bHave not\b", "Haven't"), (r"\bhave not\b", "haven't"),
    (r"\bHad not\b", "Hadn't"), (r"\bhad not\b", "hadn't"),
    (r"\bHe will\b", "He'll"), (r"\bhe will\b", "he'll"),
    (r"\bShe will\b", "She'll"), (r"\bshe will\b", "she'll"),
    (r"\bIt will\b", "It'll"), (r"\bit will\b", "it'll"),
    (r"\bGoing to\b", "Gonna"), (r"\bgoing to\b", "gonna"),
    (r"\bLet us\b", "Let's"), (r"\blet us\b", "let's"),
    (r"\bCan not\b", "Can't"), (r"\bcan not\b", "can't"),
    ]

    for regex, repl in reps:
      t = re.sub(regex, repl, t) 
    return t

  # Move ., ?, ! ou : de dentro do </span> para fora.
  def mover_pontuacao(self, texto: str) -> str:    
    return re.sub(r'([.!?:])</span>', r'</span>\1', texto)
    
  # TRADUZ, DEFINE FRASES ABREVIADAS E INFORMAIS, E ESCOLHE O TEMPLATE.
  def save_model(self, request, obj, form, change):
    
    #en_full = obj.expected_en
    raw_expected = obj.expected_en or ""
    # divide por OR / or (case-insensitive)
    parts = re.split(r"\s+or\s+", raw_expected, flags=re.IGNORECASE)
    en_full = parts[0].strip() if len(parts) > 0 else ""
    en_full_M = parts[1].strip() if len(parts) > 1 else ""
    en_abbrev = self.contract_en(en_full)
    en_informal = self.gerar_informal(en_full)
    
    # TROCA OS 2 CODIGOS DE: IMPLEMENTACAO 1, POR ESSE
    # traduções base
    # try:
    #   pt = GoogleTranslator(source="en", target="pt").translate(en_full)
    #   es = GoogleTranslator(source="en", target="es").translate(en_full)
    #   fr = GoogleTranslator(source="en", target="fr").translate(en_full)
    #   it = GoogleTranslator(source="en", target="it").translate(en_full)
    # except Exception:
    #   pt = es = fr = it = None
    
    # IMPLEMENTACAO 1
    trads = traduz_com_retry(en_full)
    pt, es, fr, it = trads["pt"], trads["es"], trads["fr"], trads["it"]
 
    # AQUI GRAVA NO JSON AS VARIAVEIS
    from apps.chat.utils.dictionary_writer import add_term, term_exists

    # EN → todas as formas
    # ingleses = [en_full, en_abbrev, en_informal]

    # for txt in ingleses:
    #     if txt:
    #         term = re.sub(r"[.:!?]", "", txt).lower().strip()
    #         if not term_exists("en", term):
    #             add_term("en", term)
    
    # --- DICIONÁRIO EN (novo / edição com limpeza) ---
    def clean_term(t: str) -> str:
        return re.sub(r"[.:!?]", "", t).lower().strip()

    ingleses = []

    # frase completa com OR
    if " or " in raw_expected.lower():
        ingleses.append(raw_expected)

    # primeira forma
    if en_full:
        ingleses.append(en_full)

    # segunda forma
    if en_full_M:
        ingleses.append(en_full_M)

    for txt in ingleses:
        term = clean_term(txt)
        if term and not term_exists("en", term):
            add_term("en", term)


    # OUTROS IDIOMAS
    entries = {
        "pt": pt,
        "es": es,
        "fr": fr,
        "it": it,
    }

    for lang, text in entries.items():
        if text:
            term = re.sub(r"[.:!?]", "", text).lower().strip()
            if not term_exists(lang, term):
                add_term(lang, term)
                
    # AQUI GRAVA NO JSON AS VARIAVEIS
    template_choice = form.cleaned_data.get("template_choice")

    if template_choice == "1":
        templates_pt = self.TEMPLATES_CONTENT_1_PT
        templates_es = self.TEMPLATES_CONTENT_1_ES
        templates_fr = self.TEMPLATES_CONTENT_1_FR
        templates_it = self.TEMPLATES_CONTENT_1_IT
    elif template_choice == "2":
        templates_pt = self.TEMPLATES_CONTENT_2_PT
        templates_es = self.TEMPLATES_CONTENT_2_ES
        templates_fr = self.TEMPLATES_CONTENT_2_FR
        templates_it = self.TEMPLATES_CONTENT_2_IT
    elif template_choice == "3":
        templates_pt = self.TEMPLATES_CONTENT_3_PT
        templates_es = self.TEMPLATES_CONTENT_3_ES
        templates_fr = self.TEMPLATES_CONTENT_3_FR
        templates_it = self.TEMPLATES_CONTENT_3_IT
    elif template_choice == "4":
        templates_pt = self.TEMPLATES_CONTENT_4_PT
        templates_es = self.TEMPLATES_CONTENT_4_ES
        templates_fr = self.TEMPLATES_CONTENT_4_FR
        templates_it = self.TEMPLATES_CONTENT_4_IT
    elif template_choice == "5":
        templates_pt = self.TEMPLATES_CONTENT_5_PT
        templates_es = self.TEMPLATES_CONTENT_5_ES
        templates_fr = self.TEMPLATES_CONTENT_5_FR
        templates_it = self.TEMPLATES_CONTENT_5_IT
    elif template_choice == "6":
        templates_pt = self.TEMPLATES_CONTENT_6_PT
        templates_es = self.TEMPLATES_CONTENT_6_ES
        templates_fr = self.TEMPLATES_CONTENT_6_FR
        templates_it = self.TEMPLATES_CONTENT_6_IT
    elif template_choice == "7":
        templates_pt = self.TEMPLATES_CONTENT_7_PT
        templates_es = self.TEMPLATES_CONTENT_7_ES
        templates_fr = self.TEMPLATES_CONTENT_7_FR
        templates_it = self.TEMPLATES_CONTENT_7_IT  
    else:
        # fallback seguro
        templates_pt = self.TEMPLATES_CONTENT_1_PT
        templates_es = self.TEMPLATES_CONTENT_1_ES
        templates_fr = self.TEMPLATES_CONTENT_1_FR
        templates_it = self.TEMPLATES_CONTENT_1_IT
    
    # expectativas (não sobrescreve)
    if not obj.expected_pt: obj.expected_pt = pt
    if not obj.expected_it: obj.expected_it = it
    if not obj.expected_es: obj.expected_es = es
    if not obj.expected_fr: obj.expected_fr = fr    

    if not obj.content_pt:
      texto = random.choice(templates_pt).format(
          en_full=en_full,
          en_full_M=en_full_M,
          en_abbrev=en_abbrev,
          en_informal=en_informal,
          pt=pt
      )
      obj.content_pt = self.mover_pontuacao(texto)

    if not obj.content_es:
      texto = random.choice(templates_es).format(
          en_full=en_full,
          en_full_M=en_full_M,
          en_abbrev=en_abbrev,
          en_informal=en_informal,
          es=es
      )
      obj.content_es = self.mover_pontuacao(texto)

    if not obj.content_fr:
      texto = random.choice(templates_fr).format(
          en_full=en_full,
          en_full_M=en_full_M,
          en_abbrev=en_abbrev,
          en_informal=en_informal,
          fr=fr
      )
      obj.content_fr = self.mover_pontuacao(texto)

    if not obj.content_it:
      texto = random.choice(templates_it).format(
          en_full=en_full,
          en_full_M=en_full_M,
          en_abbrev=en_abbrev,
          en_informal=en_informal,
          it=it
      )
      obj.content_it = self.mover_pontuacao(texto)      
 
    super().save_model(request, obj, form, change)
    
    # GRAVA EXPECTEDS NA EDIÇÃO DO DICIONARIO (essa edição é sem apagar os campos)
    if change:
        from apps.chat.utils.dictionary_writer import add_term, term_exists

        expected_map = {
            "en": obj.expected_en,
            "pt": obj.expected_pt,
            "it": obj.expected_it,
            "fr": obj.expected_fr,
            "es": obj.expected_es,
        }

        for lang, text in expected_map.items():
            if not text:
                continue

            # separa por "or" (case-insensitive)
            parts = re.split(r"\s+or\s+", text, flags=re.IGNORECASE)

            # forma completa com "or" normalizado
            if len(parts) > 1:
                full_or = " or ".join(p.strip() for p in parts)
                candidates = [full_or] + parts
            else:
                candidates = parts

            for term_raw in candidates:
                term = re.sub(r"[.:!?]", "", term_raw).lower().strip()
                term = re.sub(r"\s*\(\s*(a|as|o|os)\s*\)", "", term, flags=re.IGNORECASE).strip()
                if not term:
                    continue

                if not term_exists(lang, term):
                    add_term(lang, term)
    # FIM GRAVA EXPECTEDS NA EDIÇÃO DO DICIONARIO (essa edição é sem apagar os campos)    
    
    # --- REGRA single-mark (segunda inserção) ---
    frase = (obj.expected_en or "").strip()

    qs = Chat.objects.filter(
        lesson_id=obj.lesson_id,
        expected_en__iexact=frase
    ).order_by("id")

    if qs.count() == 2:
        antigo = qs.first()
        if antigo.role == "teacher":
            antigo.role = "single-mark"
            antigo.save(update_fields=["role"])


  # FRASES COM ABREVIACOES E SEM ABREVIACOES
  TEMPLATES_CONTENT_1_PT = [     
    "Veja essa frase: <span style='color:blue;'>{pt}</span> "
    "Agora em inglês abreviado: <span style='color:red;'>{en_abbrev}</span> "
    "E sem abreviar fica assim: <span style='color:red;'>{en_full}</span>",
    
    "Dá pra dizer abreviado: <span style='color:red;'>{en_abbrev}</span> "
    "Ou sem abreviação: <span style='color:red;'>{en_full}</span> "
    "Significa: <span style='color:blue;'>{pt}</span>",
    
    "Próxima frase é: <span style='color:blue;'>{pt}</span> "
    "Abreviada em inglês: <span style='color:red;'>{en_abbrev}</span> "
    "E sem abreviação: <span style='color:red;'>{en_full}</span>",
    
    "Abreviado fica: <span style='color:red;'>{en_abbrev}</span> "
    "Sem abreviar fica: <span style='color:red;'>{en_full}</span> "
    "Tradução: <span style='color:blue;'>{pt}</span>",
    
    "Frase em português: <span style='color:blue;'>{pt}</span> "
    "Em inglês abreviado: <span style='color:red;'>{en_abbrev}</span> "
    "Sem usar abreviação: <span style='color:red;'>{en_full}</span>"    
  ]
  TEMPLATES_CONTENT_1_IT = [
    "Guarda questa frase: <span style='color:blue;'>{it}</span> "
    "Ora in inglese abbreviato: <span style='color:red;'>{en_abbrev}</span> "
    "E senza abbreviare diventa così: <span style='color:red;'>{en_full}</span>",
    
    "Si può dire in forma abbreviata: <span style='color:red;'>{en_abbrev}</span> "
    "Oppure senza abbreviazione: <span style='color:red;'>{en_full}</span> "
    "Significa: <span style='color:blue;'>{it}</span>",

    "La prossima frase è: <span style='color:blue;'>{it}</span> "
    "Abbreviata in inglese: <span style='color:red;'>{en_abbrev}</span> "
    "E senza abbreviazione: <span style='color:red;'>{en_full}</span>",
    
    "Abbreviato è: <span style='color:red;'>{en_abbrev}</span> "
    "Senza abbreviare è: <span style='color:red;'>{en_full}</span> "
    "Traduzione: <span style='color:blue;'>{it}</span>",

    "Frase in italiano: <span style='color:blue;'>{it}</span> "
    "In inglese abbreviato: <span style='color:red;'>{en_abbrev}</span> "
    "Senza usare abbreviazioni: <span style='color:red;'>{en_full}</span>"
  ]  
  TEMPLATES_CONTENT_1_FR = [
    "Regarde cette phrase : <span style='color:blue;'>{fr}</span> "
    "Maintenant en anglais abrégé : <span style='color:red;'>{en_abbrev}</span> "
    "Et sans abréviation, cela donne : <span style='color:red;'>{en_full}</span>",
    
    "On peut dire en abrégé : <span style='color:red;'>{en_abbrev}</span> "
    "Ou sans abréviation : <span style='color:red;'>{en_full}</span> "
    "Cela veut dire : <span style='color:blue;'>{fr}</span>",

    "La phrase suivante est : <span style='color:blue;'>{fr}</span> "
    "Abrégée en anglais : <span style='color:red;'>{en_abbrev}</span> "
    "Et sans abréviation : <span style='color:red;'>{en_full}</span>",
    
    "Abrégé, c'est : <span style='color:red;'>{en_abbrev}</span> "
    "Sans abréger, c'est : <span style='color:red;'>{en_full}</span> "
    "Traduction : <span style='color:blue;'>{fr}</span>",

    "Phrase en français : <span style='color:blue;'>{fr}</span> "
    "En anglais abrégé : <span style='color:red;'>{en_abbrev}</span> "
    "Sans utiliser d'abréviations : <span style='color:red;'>{en_full}</span>"
  ]
  TEMPLATES_CONTENT_1_ES = [
    "Mira esta frase: <span style='color:blue;'>{es}</span> "
    "Ahora en inglés abreviado: <span style='color:red;'>{en_abbrev}</span> "
    "Y sin abreviar queda así: <span style='color:red;'>{en_full}</span>",
    
    "Se puede decir abreviado: <span style='color:red;'>{en_abbrev}</span> "
    "O sin abreviación: <span style='color:red;'>{en_full}</span> "
    "Significa: <span style='color:blue;'>{es}</span>",

    "La siguiente frase es: <span style='color:blue;'>{es}</span> "
    "Abreviada en inglés: <span style='color:red;'>{en_abbrev}</span> "
    "Y sin abreviación: <span style='color:red;'>{en_full}</span>",
    
    "Abreviado es: <span style='color:red;'>{en_abbrev}</span> "
    "Sin abreviar es: <span style='color:red;'>{en_full}</span> "
    "Traducción: <span style='color:blue;'>{es}</span>",

    "Frase en español: <span style='color:blue;'>{es}</span> "
    "En inglés abreviado: <span style='color:red;'>{en_abbrev}</span> "
    "Sin usar abreviaciones: <span style='color:red;'>{en_full}</span>"
  ]
  
  # FRASES SEM ABREVIACOES
  TEMPLATES_CONTENT_2_PT = [
    "Pode repetir comigo a frase: <span style='color:blue;'>{pt}</span> Que traduzida em inglês fica: "
    "<span style='color:red;'>{en_full}</span>",

    "Agora repita comigo: <span style='color:blue;'>{pt}</span> Que em inglês dizemos: "
    "<span style='color:red;'>{en_full}</span>",

    "Vamos praticar juntos: <span style='color:blue;'>{pt}</span> A tradução correta em inglês é: "
    "<span style='color:red;'>{en_full}</span>",

    "Repita esta frase comigo: <span style='color:blue;'>{pt}</span> Essa frase em inglês seria: "
    "<span style='color:red;'>{en_full}</span>",

    "Tente falar comigo: <span style='color:blue;'>{pt}</span> Que em inglês a forma certa é: "
    "<span style='color:red;'>{en_full}</span>",
    
    "Repita comigo a seguinte frase: <span style='color:blue;'>{pt}</span> Falando em inglês fica: "
    "<span style='color:red;'>{en_full}</span>",
    
    "Vamos repetir juntos: <span style='color:blue;'>{pt}</span> Isso em inglês significa: "
    "<span style='color:red;'>{en_full}</span>",
    
    "Tente pronunciar comigo: <span style='color:blue;'>{pt}</span> Traduzida para o inglês significa: "
    "<span style='color:red;'>{en_full}</span>",
    
    "Fale comigo esta frase: <span style='color:blue;'>{pt}</span> Traduzida para o inglês é: "
    "<span style='color:red;'>{en_full}</span>",
    
    "Pode treinar comigo dizendo: <span style='color:blue;'>{pt}</span> Em inglês falamos: "
    "<span style='color:red;'>{en_full}</span>",
    
    "Vamos juntos repetir: <span style='color:blue;'>{pt}</span> Essa versão em inglês seria: "
    "<span style='color:red;'>{en_full}</span>",    
    
    "Em português: <span style='color:blue;'>{pt}</span> Agora repita em inglês: "
    "<span style='color:red;'>{en_full}</span>",
    
    "Em português fica assim: <span style='color:blue;'>{pt}</span> Repita em inglês: "
    "<span style='color:red;'>{en_full}</span>",
    
    "Em português temos: <span style='color:blue;'>{pt}</span> Vamos repetir em inglês? "
    "<span style='color:red;'>{en_full}</span>",
    
    "Falamos assim em português: <span style='color:blue;'>{pt}</span> Você poderia repetir em inglês? "
    "<span style='color:red;'>{en_full}</span>",
    
    "Frase em português: <span style='color:blue;'>{pt}</span> Tenta repetir em inglês: "
    "<span style='color:red;'>{en_full}</span>"
  ]  
  TEMPLATES_CONTENT_2_IT = [
    "Puoi ripetere con me la frase: <span style='color:blue;'>{it}</span> Che tradotta in inglese diventa: "
    "<span style='color:red;'>{en_full}</span>",

    "Ora ripeti con me: <span style='color:blue;'>{it}</span> Che in inglese diciamo: "
    "<span style='color:red;'>{en_full}</span>",

    "Alleniamoci insieme: <span style='color:blue;'>{it}</span> La traduzione corretta in inglese è: "
    "<span style='color:red;'>{en_full}</span>",

    "Ripeti questa frase con me: <span style='color:blue;'>{it}</span> Questa frase in inglese sarebbe: "
    "<span style='color:red;'>{en_full}</span>",

    "Prova a dirla con me: <span style='color:blue;'>{it}</span> In inglese la forma giusta è: "
    "<span style='color:red;'>{en_full}</span>",

    "Ripeti con me la seguente frase: <span style='color:blue;'>{it}</span> In inglese diventa: "
    "<span style='color:red;'>{en_full}</span>",

    "Ripetiamo insieme: <span style='color:blue;'>{it}</span> Questo in inglese significa: "
    "<span style='color:red;'>{en_full}</span>",

    "Prova a pronunciarla con me: <span style='color:blue;'>{it}</span> Tradotta in inglese significa: "
    "<span style='color:red;'>{en_full}</span>",

    "Dì con me questa frase: <span style='color:blue;'>{it}</span> Tradotta in inglese è: "
    "<span style='color:red;'>{en_full}</span>",

    "Puoi esercitarti con me dicendo: <span style='color:blue;'>{it}</span> In inglese diciamo: "
    "<span style='color:red;'>{en_full}</span>",

    "Ripetiamo insieme: <span style='color:blue;'>{it}</span> Questa versione in inglese sarebbe: "
    "<span style='color:red;'>{en_full}</span>",

    "In italiano: <span style='color:blue;'>{it}</span> Ora ripeti in inglese: "
    "<span style='color:red;'>{en_full}</span>",

    "In italiano è così: <span style='color:blue;'>{it}</span> Ripeti in inglese: "
    "<span style='color:red;'>{en_full}</span>",

    "In italiano abbiamo: <span style='color:blue;'>{it}</span> Ripetiamo in inglese? "
    "<span style='color:red;'>{en_full}</span>",

    "Diciamo così in italiano: <span style='color:blue;'>{it}</span> Potresti ripetere in inglese? "
    "<span style='color:red;'>{en_full}</span>",

    "Frase in italiano: <span style='color:blue;'>{it}</span> Prova a ripetere in inglese: "
    "<span style='color:red;'>{en_full}</span>"
  ]  
  TEMPLATES_CONTENT_2_FR = [
    "Répétez avec moi la phrase : <span style='color:blue;'>{fr}</span> Qui, traduite en anglais, devient : "
    "<span style='color:red;'>{en_full}</span>",

    "Maintenant, répétez avec moi : <span style='color:blue;'>{fr}</span> Qu'en anglais, on dit : "
    "<span style='color:red;'>{en_full}</span>",

    "Pratiquons ensemble : <span style='color:blue;'>{fr}</span> La traduction correcte en anglais est : "
    "<span style='color:red;'>{en_full}</span>",

    "Répétez cette phrase avec moi : <span style='color:blue;'>{fr}</span> Cette phrase en anglais serait : "
    "<span style='color:red;'>{en_full}</span>",

    "Essayez de la dire avec moi : <span style='color:blue;'>{fr}</span> En anglais, la forme correcte est : "
    "<span style='color:red;'>{en_full}</span>",

    "Répétez avec moi la phrase suivante : <span style='color:blue;'>{fr}</span> En anglais, cela devient : "
    "<span style='color:red;'>{en_full}</span>",

    "Répétons ensemble : <span style='color:blue;'>{fr}</span> Cela en anglais signifie : "
    "<span style='color:red;'>{en_full}</span>",

    "Essayez de la prononcer avec moi : <span style='color:blue;'>{fr}</span> Traduite en anglais, elle signifie : "
    "<span style='color:red;'>{en_full}</span>",

    "Dites cette phrase avec moi : <span style='color:blue;'>{fr}</span> Traduite en anglais, elle est : "
    "<span style='color:red;'>{en_full}</span>",

    "Vous pouvez vous exercer avec moi en disant : <span style='color:blue;'>{fr}</span> En anglais, on dit : "
    "<span style='color:red;'>{en_full}</span>",

    "Répétons ensemble : <span style='color:blue;'>{fr}</span> Cette version en anglais serait : "
    "<span style='color:red;'>{en_full}</span>",

    "En français : <span style='color:blue;'>{fr}</span> Maintenant, répétez en anglais : "
    "<span style='color:red;'>{en_full}</span>",

    "En français, c'est comme ça : <span style='color:blue;'>{fr}</span> Répétez en anglais : "
    "<span style='color:red;'>{en_full}</span>",

    "En français, nous disons : <span style='color:blue;'>{fr}</span> Répétons en anglais ? "
    "<span style='color:red;'>{en_full}</span>",

    "Nous disons ainsi en français : <span style='color:blue;'>{fr}</span> Pourriez-vous répéter en anglais ? "
    "<span style='color:red;'>{en_full}</span>",

    "Phrase en français : <span style='color:blue;'>{fr}</span> Essayez de répéter en anglais : "
    "<span style='color:red;'>{en_full}</span>"
  ]
  TEMPLATES_CONTENT_2_ES = [
    "Puedes repetir conmigo la frase: <span style='color:blue;'>{es}</span> Que traducida al inglés queda: "
    "<span style='color:red;'>{en_full}</span>",

    "Ahora repite conmigo: <span style='color:blue;'>{es}</span> Que en inglés decimos: "
    "<span style='color:red;'>{en_full}</span>",

    "Practiquemos juntos: <span style='color:blue;'>{es}</span> La traducción correcta al inglés es: "
    "<span style='color:red;'>{en_full}</span>",

    "Repite esta frase conmigo: <span style='color:blue;'>{es}</span> Esta frase en inglés sería: "
    "<span style='color:red;'>{en_full}</span>",

    "Intenta decir conmigo: <span style='color:blue;'>{es}</span> Que en inglés la forma correcta es: "
    "<span style='color:red;'>{en_full}</span>",

    "Repite conmigo la siguiente frase: <span style='color:blue;'>{es}</span> En inglés queda: "
    "<span style='color:red;'>{en_full}</span>",

    "Repitamos juntos: <span style='color:blue;'>{es}</span> Esto en inglés significa: "
    "<span style='color:red;'>{en_full}</span>",

    "Intenta pronunciar conmigo: <span style='color:blue;'>{es}</span> Traducida al inglés significa: "
    "<span style='color:red;'>{en_full}</span>",

    "Di conmigo esta frase: <span style='color:blue;'>{es}</span> Traducida al inglés es: "
    "<span style='color:red;'>{en_full}</span>",

    "Puedes practicar conmigo diciendo: <span style='color:blue;'>{es}</span> En inglés decimos: "
    "<span style='color:red;'>{en_full}</span>",

    "Repitamos juntos: <span style='color:blue;'>{es}</span> Esta versión en inglés sería: "
    "<span style='color:red;'>{en_full}</span>",

    "En español: <span style='color:blue;'>{es}</span> Ahora repite en inglés: "
    "<span style='color:red;'>{en_full}</span>",

    "En español queda así: <span style='color:blue;'>{es}</span> Repite en inglés: "
    "<span style='color:red;'>{en_full}</span>",

    "En español tenemos: <span style='color:blue;'>{es}</span> Vamos a repetir en inglés? "
    "<span style='color:red;'>{en_full}</span>",

    "Hablamos así en español: <span style='color:blue;'>{es}</span> ¿Podrías repetir en inglés? "
    "<span style='color:red;'>{en_full}</span>",

    "Frase en español: <span style='color:blue;'>{es}</span> Intenta repetir en inglés: "
    "<span style='color:red;'>{en_full}</span>"
  ]
  
  # FRASE PARA TRADUZIR O PORTUGUES
  TEMPLATES_CONTENT_3_PT = [
    "Como você diria em inglês esta frase? (stp1) <span style='color:blue;'>{pt}</span>",
    "Você sabe como dizer isso em inglês? (stp1) <span style='color:blue;'>{pt}</span>",
    "Tente dizer em inglês a frase: (stp1) <span style='color:blue;'>{pt}</span>",
    "Consegue traduzir para o inglês esta frase? (stp1) <span style='color:blue;'>{pt}</span>",
    "Como ficaria em inglês esta frase? (stp1) <span style='color:blue;'>{pt}</span>",
    "Pense rápido, como se fala em inglês? (stp1) <span style='color:blue;'>{pt}</span>",
    "Você consegue falar em inglês esta frase? (stp1) <span style='color:blue;'>{pt}</span>",
    "Diga em inglês a seguinte frase: (stp1) <span style='color:blue;'>{pt}</span>",
    "Tente traduzir esta frase para o inglês: (stp1) <span style='color:blue;'>{pt}</span>",
    "Você saberia dizer em inglês? (stp1) <span style='color:blue;'>{pt}</span>",
    "Consegue transformar em inglês esta frase? (stp1) <span style='color:blue;'>{pt}</span>",
    "Como se fala em inglês esta frase? (stp1) <span style='color:blue;'>{pt}</span>",
    "Como você pronunciaria em inglês? (stp1) <span style='color:blue;'>{pt}</span>",
    "Em inglês, como diria esta frase? (stp1) <span style='color:blue;'>{pt}</span>",
    "Você lembra como se diz em inglês? (stp1) <span style='color:blue;'>{pt}</span>",
    "Tente traduzir essa frase em inglês: (stp1) <span style='color:blue;'>{pt}</span>",
    "Qual seria a tradução dessa frase? (stp1) <span style='color:blue;'>{pt}</span>",
    "Repita em inglês: (stp1) <span style='color:blue;'>{pt}</span>",    
    "Como você diria isso em inglês? (stp1) <span style='color:blue;'>{pt}</span>",
    "Consegue dizer essa frase em inglês? (stp1) <span style='color:blue;'>{pt}</span>",
    "Transforme esta frase para o inglês: (stp1) <span style='color:blue;'>{pt}</span>",
    "Qual é a versão em inglês desta frase? (stp1) <span style='color:blue;'>{pt}</span>",
    "Tente falar em inglês a frase: (stp1) <span style='color:blue;'>{pt}</span>",
    "Em inglês, como fica isso aqui? (stp1) <span style='color:blue;'>{pt}</span>",
    "Tente converter essa frase para o inglês: (stp1) <span style='color:blue;'>{pt}</span>",
    "Como seria dito em inglês? (stp1) <span style='color:blue;'>{pt}</span>",
    "Mostre como ficaria essa frase em inglês: (stp1) <span style='color:blue;'>{pt}</span>"    
  ]
  TEMPLATES_CONTENT_3_IT = [
    "Come diresti in inglese questa frase? (stp1) <span style='color:blue;'>{it}</span>",
    "Sai come dire questo in inglese? (stp3) <span style='color:blue;'>{it}</span>",
    "Prova a dire in inglese la frase: (stp1) <span style='color:blue;'>{it}</span>",
    "Riesci a tradurre in inglese questa frase? (stp1) <span style='color:blue;'>{it}</span>",
    "Come sarebbe in inglese questa frase? (stp1) <span style='color:blue;'>{it}</span>",
    "Vediamo se indovini. Come si dice in inglese questa frase? (stp1) <span style='color:blue;'>{it}</span>",
    "Immagina di doverlo dire in inglese. Come sarebbe? (stp1) <span style='color:blue;'>{it}</span>",
    "Pensa in fretta. Come si dice in inglese? (stp1) <span style='color:blue;'>{it}</span>",
    "Riesci a dire in inglese questa frase? (stp1) <span style='color:blue;'>{it}</span>",
    "Di' in inglese la seguente frase: (stp1) <span style='color:blue;'>{it}</span>",
    "Prova a tradurre questa frase in inglese: (stp1) <span style='color:blue;'>{it}</span>",
    "Sapresti dirlo in inglese? (stp1) <span style='color:blue;'>{it}</span>",
    "Riesci a trasformare in inglese questa frase? (stp1) <span style='color:blue;'>{it}</span>",
    "Come si dice in inglese questa frase? (stp1) <span style='color:blue;'>{it}</span>",
    "Come pronunceresti in inglese? (stp1) <span style='color:blue;'>{it}</span>",
    "In inglese, come diresti questa frase? (stp1) <span style='color:blue;'>{it}</span>",
    "Ti ricordi come si dice in inglese? (stp1) <span style='color:blue;'>{it}</span>",
    "Prova a tradurre questa frase in inglese: (stp1) <span style='color:blue;'>{it}</span>",
    "Quale sarebbe la traduzione di questa frase? (stp1) <span style='color:blue;'>{it}</span>",
    "Ripeti in inglese: (stp1) <span style='color:blue;'>{it}</span>",    
    "Come diresti questo in inglese? (stp1) <span style='color:blue;'>{it}</span>",
    "Riesci a dire questa frase in inglese? (stp1) <span style='color:blue;'>{it}</span>",
    "Trasforma questa frase in inglese: (stp1) <span style='color:blue;'>{it}</span>",
    "Qual è la versione in inglese di questa frase? (stp1) <span style='color:blue;'>{it}</span>",
    "Prova a dire in inglese la frase: (stp1) <span style='color:blue;'>{it}</span>",
    "In inglese, come sarebbe questo? (stp1) <span style='color:blue;'>{it}</span>",
    "Riesci a pensare a come dirlo in inglese? (stp1) <span style='color:blue;'>{it}</span>",
    "Prova a convertire questa frase in inglese: (stp1) <span style='color:blue;'>{it}</span>",
    "Come si direbbe in inglese? (stp1) <span style='color:blue;'>{it}</span>",
    "Mostra come sarebbe questa frase in inglese: (stp1) <span style='color:blue;'>{it}</span>"
  ]
  TEMPLATES_CONTENT_3_FR = [
    "Comment dirais-tu cette phrase en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Sais-tu comment dire cela en anglais ? (stp3) <span style='color:blue;'>{fr}</span>",
    "Essaie de dire en anglais la phrase : (stp1) <span style='color:blue;'>{fr}</span>",
    "Peux-tu traduire cette phrase en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Comment serait cette phrase en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Voyons si tu trouves. Comment dit-on cette phrase en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Imagine que tu dois le dire en anglais. Comment serait-ce ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Pense vite. Comment on dit ça en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Peux-tu dire cette phrase en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Dis en anglais la phrase suivante : (stp1) <span style='color:blue;'>{fr}</span>",
    "Essaie de traduire cette phrase en anglais : (stp1) <span style='color:blue;'>{fr}</span>",
    "Saurais-tu le dire en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Peux-tu transformer cette phrase en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Comment dit-on cette phrase en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Comment la prononcerais-tu en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "En anglais, comment dirais-tu cette phrase ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Te souviens-tu comment on dit cela en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Essaie de traduire cette phrase en anglais : (stp1) <span style='color:blue;'>{fr}</span>",
    "Quelle serait la traduction de cette phrase ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Répète en anglais : (stp1) <span style='color:blue;'>{fr}</span>",    
    "Comment dirais-tu cela en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Peux-tu dire cette phrase en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Transforme cette phrase en anglais : (stp1) <span style='color:blue;'>{fr}</span>",
    "Quelle est la version anglaise de cette phrase ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Essaie de dire en anglais la phrase : (stp1) <span style='color:blue;'>{fr}</span>",
    "En anglais, comment serait ceci ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Peux-tu imaginer comment le dire en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Essaie de convertir cette phrase en anglais : (stp1) <span style='color:blue;'>{fr}</span>",
    "Comment serait-ce dit en anglais ? (stp1) <span style='color:blue;'>{fr}</span>",
    "Montre comment cette phrase serait en anglais : (stp1) <span style='color:blue;'>{fr}</span>"
  ]
  TEMPLATES_CONTENT_3_ES = [
    "¿Cómo dirías en inglés esta frase? (stp1) <span style='color:blue;'>{es}</span>",
    "¿Sabes cómo decir esto en inglés? (stp3) <span style='color:blue;'>{es}</span>",
    "Intenta decir en inglés la frase: (stp1) <span style='color:blue;'>{es}</span>",
    "¿Puedes traducir al inglés esta frase? (stp1) <span style='color:blue;'>{es}</span>",
    "¿Cómo sería en inglés esta frase? (stp1) <span style='color:blue;'>{es}</span>",
    "Veamos si aciertas. ¿Cómo se dice en inglés esta frase? (stp1) <span style='color:blue;'>{es}</span>",
    "Imagina que necesitas decir esto en inglés. ¿Cómo sería? (stp1) <span style='color:blue;'>{es}</span>",
    "Piensa rápido. ¿Cómo se dice en inglés? (stp1) <span style='color:blue;'>{es}</span>",
    "¿Puedes decir en inglés esta frase? (stp1) <span style='color:blue;'>{es}</span>",
    "Di en inglés la siguiente frase: (stp1) <span style='color:blue;'>{es}</span>",
    "Intenta traducir esta frase al inglés: (stp1) <span style='color:blue;'>{es}</span>",
    "¿Sabrías decirlo en inglés? (stp1) <span style='color:blue;'>{es}</span>",
    "¿Puedes transformar esta frase al inglés? (stp1) <span style='color:blue;'>{es}</span>",
    "¿Cómo se dice en inglés esta frase? (stp1) <span style='color:blue;'>{es}</span>",
    "¿Cómo la pronunciarías en inglés? (stp1) <span style='color:blue;'>{es}</span>",
    "En inglés, ¿cómo dirías esta frase? (stp1) <span style='color:blue;'>{es}</span>",
    "¿Recuerdas cómo se dice en inglés? (stp1) <span style='color:blue;'>{es}</span>",
    "Intenta traducir esta frase al inglés: (stp1) <span style='color:blue;'>{es}</span>",
    "¿Cuál sería la traducción de esta frase? (stp1) <span style='color:blue;'>{es}</span>",
    "Repite en inglés: (stp1) <span style='color:blue;'>{es}</span>",    
    "¿Cómo dirías esto en inglés? (stp1) <span style='color:blue;'>{es}</span>",
    "¿Puedes decir esta frase en inglés? (stp1) <span style='color:blue;'>{es}</span>",
    "Transforma esta frase al inglés: (stp1) <span style='color:blue;'>{es}</span>",
    "¿Cuál es la versión en inglés de esta frase? (stp1) <span style='color:blue;'>{es}</span>",
    "Intenta decir en inglés la frase: (stp1) <span style='color:blue;'>{es}</span>",
    "En inglés, ¿cómo sería esto? (stp1) <span style='color:blue;'>{es}</span>",
    "¿Puedes pensar cómo decirlo en inglés? (stp1) <span style='color:blue;'>{es}</span>",
    "Intenta convertir esta frase al inglés: (stp1) <span style='color:blue;'>{es}</span>",
    "¿Cómo se diría en inglés? (stp1) <span style='color:blue;'>{es}</span>",
    "Muestra cómo quedaría esta frase en inglés: (stp1) <span style='color:blue;'>{es}</span>"
  ]
  
  # FRASES FORMAIS E INFORMAIS
  TEMPLATES_CONTENT_4_PT = [
    "Esta frase: <span style='color:blue;'>{pt}</span> Em inglês fica: <span style='color:red;'>{en_abbrev}</span> E pode ser falada informalmente: <span style='color:red;'>{en_informal}</span>",
    "Em inglês, a frase: <span style='color:blue;'>{pt}</span> Pode ser dita como: <span style='color:red;'>{en_abbrev}</span> De forma ainda mais informal, dizemos: <span style='color:red;'>{en_informal}</span>",
    "A tradução dessa frase: <span style='color:blue;'>{pt}</span> Pode ser dita assim: <span style='color:red;'>{en_abbrev}</span> De modo mais informal, você pode dizer: <span style='color:red;'>{en_informal}</span>",
    "Podemos dizer que essa frase: <span style='color:blue;'>{pt}</span> Em inglês significa: <span style='color:red;'>{en_abbrev}</span> E de forma mais casual: <span style='color:red;'>{en_informal}</span>",
    "Essa frase em português: <span style='color:blue;'>{pt}</span> Em inglês, dizemos: <span style='color:red;'>{en_abbrev}</span> E de modo mais informal: <span style='color:red;'>{en_informal}</span>",  
    "A frase: <span style='color:blue;'>{pt}</span> Pode ser traduzida como: <span style='color:red;'>{en_abbrev}</span> E falada de forma informal: <span style='color:red;'>{en_informal}</span>",
    "Em português dizemos: <span style='color:blue;'>{pt}</span> Em inglês, a forma é: <span style='color:red;'>{en_abbrev}</span> E de forma mais solta: <span style='color:red;'>{en_informal}</span>",
    "Veja a frase: <span style='color:blue;'>{pt}</span> Em inglês seria: <span style='color:red;'>{en_abbrev}</span> Informalmente, podemos dizer: <span style='color:red;'>{en_informal}</span>",
    "Aqui temos: <span style='color:blue;'>{pt}</span> A tradução é: <span style='color:red;'>{en_abbrev}</span> E a forma mais descontraída: <span style='color:red;'>{en_informal}</span>",
    "Esta é a frase: <span style='color:blue;'>{pt}</span> Em inglês se diz: <span style='color:red;'>{en_abbrev}</span> E de modo mais natural: <span style='color:red;'>{en_informal}</span>",
    "Podemos traduzir assim: <span style='color:blue;'>{pt}</span> Em inglês falamos: <span style='color:red;'>{en_abbrev}</span> E de forma mais informal: <span style='color:red;'>{en_informal}</span>",
    "A forma correta em inglês seria: <span style='color:blue;'>{pt}</span> Traduzida como: <span style='color:red;'>{en_abbrev}</span> E de modo mais simples: <span style='color:red;'>{en_informal}</span>",
    "Traduzindo para o inglês: <span style='color:blue;'>{pt}</span> Fica: <span style='color:red;'>{en_abbrev}</span> E de forma coloquial: <span style='color:red;'>{en_informal}</span>",
    "Em inglês podemos dizer: <span style='color:blue;'>{pt}</span> Assim: <span style='color:red;'>{en_abbrev}</span> Ou mais naturalmente: <span style='color:red;'>{en_informal}</span>",
    "A frase equivalente em inglês é: <span style='color:blue;'>{pt}</span> Que fica: <span style='color:red;'>{en_abbrev}</span> E de maneira informal: <span style='color:red;'>{en_informal}</span>",
    "Se traduzirmos: <span style='color:blue;'>{pt}</span> Em inglês seria: <span style='color:red;'>{en_abbrev}</span> E falada casualmente: <span style='color:red;'>{en_informal}</span>",
    "Em inglês podemos expressar: <span style='color:blue;'>{pt}</span> Usando: <span style='color:red;'>{en_abbrev}</span> E de forma informal: <span style='color:red;'>{en_informal}</span>",
    "Essa expressão: <span style='color:blue;'>{pt}</span> Fica em inglês: <span style='color:red;'>{en_abbrev}</span> E falada de modo leve: <span style='color:red;'>{en_informal}</span>",
    "Em inglês, podemos dizer: <span style='color:blue;'>{pt}</span> Assim: <span style='color:red;'>{en_abbrev}</span> E mais informalmente: <span style='color:red;'>{en_informal}</span>",
    "A tradução literal é: <span style='color:blue;'>{pt}</span> Mas de forma informal, usamos: <span style='color:red;'>{en_abbrev}</span> : <span style='color:red;'>{en_informal}</span>"
  ]
  TEMPLATES_CONTENT_4_IT = [
    "Questa frase: <span style='color:blue;'>{it}</span> In inglese diventa: <span style='color:red;'>{en_abbrev}</span> E può essere detta in modo informale: <span style='color:red;'>{en_informal}</span>",
    "In inglese, la frase: <span style='color:blue;'>{it}</span> Può essere detta come: <span style='color:red;'>{en_abbrev}</span> In modo ancora più informale, diciamo: <span style='color:red;'>{en_informal}</span>",
    "La traduzione di questa frase: <span style='color:blue;'>{it}</span> Può essere detta così: <span style='color:red;'>{en_abbrev}</span> In modo più informale puoi dire: <span style='color:red;'>{en_informal}</span>",
    "Possiamo dire che questa frase: <span style='color:blue;'>{it}</span> In inglese significa: <span style='color:red;'>{en_abbrev}</span> E in modo più casuale: <span style='color:red;'>{en_informal}</span>",
    "Questa frase in italiano: <span style='color:blue;'>{it}</span> In inglese diciamo: <span style='color:red;'>{en_abbrev}</span> E in modo più informale: <span style='color:red;'>{en_informal}</span>",
    "La frase: <span style='color:blue;'>{it}</span> Può essere tradotta come: <span style='color:red;'>{en_abbrev}</span> E detta in modo informale: <span style='color:red;'>{en_informal}</span>",
    "In italiano diciamo: <span style='color:blue;'>{it}</span> In inglese, la forma è: <span style='color:red;'>{en_abbrev}</span> E in modo più naturale: <span style='color:red;'>{en_informal}</span>",
    "Guarda la frase: <span style='color:blue;'>{it}</span> In inglese sarebbe: <span style='color:red;'>{en_abbrev}</span> Informalmente possiamo dire: <span style='color:red;'>{en_informal}</span>",
    "Qui abbiamo: <span style='color:blue;'>{it}</span> La traduzione è: <span style='color:red;'>{en_abbrev}</span> E la forma più colloquiale: <span style='color:red;'>{en_informal}</span>",
    "Questa è la frase: <span style='color:blue;'>{it}</span> In inglese si dice: <span style='color:red;'>{en_abbrev}</span> E in modo più naturale: <span style='color:red;'>{en_informal}</span>",
    "Possiamo tradurre così: <span style='color:blue;'>{it}</span> In inglese diciamo: <span style='color:red;'>{en_abbrev}</span> E in modo più informale: <span style='color:red;'>{en_informal}</span>",
    "La forma corretta in inglese sarebbe: <span style='color:blue;'>{it}</span> Tradotta come: <span style='color:red;'>{en_abbrev}</span> E in modo più semplice: <span style='color:red;'>{en_informal}</span>",
    "Traducendo in inglese: <span style='color:blue;'>{it}</span> Diventa: <span style='color:red;'>{en_abbrev}</span> E in forma colloquiale: <span style='color:red;'>{en_informal}</span>",
    "In inglese possiamo dire: <span style='color:blue;'>{it}</span> Così: <span style='color:red;'>{en_abbrev}</span> O più naturalmente: <span style='color:red;'>{en_informal}</span>",
    "La frase equivalente in inglese è: <span style='color:blue;'>{it}</span> Che diventa: <span style='color:red;'>{en_abbrev}</span> E in modo informale: <span style='color:red;'>{en_informal}</span>",
    "Se traduciamo: <span style='color:blue;'>{it}</span> In inglese sarebbe: <span style='color:red;'>{en_abbrev}</span> E detta in modo casuale: <span style='color:red;'>{en_informal}</span>",
    "In inglese possiamo esprimere: <span style='color:blue;'>{it}</span> Usando: <span style='color:red;'>{en_abbrev}</span> E in modo informale: <span style='color:red;'>{en_informal}</span>",
    "Questa espressione: <span style='color:blue;'>{it}</span> In inglese diventa: <span style='color:red;'>{en_abbrev}</span> E detta in modo leggero: <span style='color:red;'>{en_informal}</span>",
    "In inglese possiamo dire: <span style='color:blue;'>{it}</span> Così: <span style='color:red;'>{en_abbrev}</span> E più informalmente: <span style='color:red;'>{en_informal}</span>",
    "La traduzione letterale è: <span style='color:blue;'>{it}</span> Ma in modo informale usiamo: <span style='color:red;'>{en_abbrev}</span> O ancora: <span style='color:red;'>{en_informal}</span>"
  ]
  TEMPLATES_CONTENT_4_FR = [
    "Cette phrase : <span style='color:blue;'>{fr}</span> En anglais devient : <span style='color:red;'>{en_abbrev}</span> Et peut être dite de façon informelle : <span style='color:red;'>{en_informal}</span>",
    "En anglais, la phrase : <span style='color:blue;'>{fr}</span> Peut être dite comme : <span style='color:red;'>{en_abbrev}</span> Et de manière encore plus informelle : <span style='color:red;'>{en_informal}</span>",
    "La traduction de cette phrase : <span style='color:blue;'>{fr}</span> Se dit ainsi : <span style='color:red;'>{en_abbrev}</span> Et de façon plus informelle : <span style='color:red;'>{en_informal}</span>",
    "On peut dire que cette phrase : <span style='color:blue;'>{fr}</span> En anglais signifie : <span style='color:red;'>{en_abbrev}</span> Et de manière plus décontractée : <span style='color:red;'>{en_informal}</span>",
    "Cette phrase en français : <span style='color:blue;'>{fr}</span> En anglais, on dit : <span style='color:red;'>{en_abbrev}</span> Et de façon plus informelle : <span style='color:red;'>{en_informal}</span>",
    "La phrase : <span style='color:blue;'>{fr}</span> Peut être traduite par : <span style='color:red;'>{en_abbrev}</span> Et dite de manière informelle : <span style='color:red;'>{en_informal}</span>",
    "En français nous disons : <span style='color:blue;'>{fr}</span> En anglais, la forme est : <span style='color:red;'>{en_abbrev}</span> Et de façon plus naturelle : <span style='color:red;'>{en_informal}</span>",
    "Regardez la phrase : <span style='color:blue;'>{fr}</span> En anglais ce serait : <span style='color:red;'>{en_abbrev}</span> Informellement, on peut dire : <span style='color:red;'>{en_informal}</span>",
    "Voici : <span style='color:blue;'>{fr}</span> La traduction est : <span style='color:red;'>{en_abbrev}</span> Et la forme plus familière : <span style='color:red;'>{en_informal}</span>",
    "Voici la phrase : <span style='color:blue;'>{fr}</span> En anglais on dit : <span style='color:red;'>{en_abbrev}</span> Et de façon plus naturelle : <span style='color:red;'>{en_informal}</span>",
    "Nous pouvons traduire ainsi : <span style='color:blue;'>{fr}</span> En anglais on dit : <span style='color:red;'>{en_abbrev}</span> Et de manière informelle : <span style='color:red;'>{en_informal}</span>",
    "La forme correcte en anglais serait : <span style='color:blue;'>{fr}</span> Traduite par : <span style='color:red;'>{en_abbrev}</span> Et de manière plus simple : <span style='color:red;'>{en_informal}</span>",
    "En traduisant en anglais : <span style='color:blue;'>{fr}</span> Cela devient : <span style='color:red;'>{en_abbrev}</span> Et en version familière : <span style='color:red;'>{en_informal}</span>",
    "En anglais on peut dire : <span style='color:blue;'>{fr}</span> Ainsi : <span style='color:red;'>{en_abbrev}</span> Ou plus naturellement : <span style='color:red;'>{en_informal}</span>",
    "La phrase équivalente en anglais est : <span style='color:blue;'>{fr}</span> Qui devient : <span style='color:red;'>{en_abbrev}</span> Et de manière informelle : <span style='color:red;'>{en_informal}</span>",
    "Si nous traduisons : <span style='color:blue;'>{fr}</span> En anglais ce serait : <span style='color:red;'>{en_abbrev}</span> Et dit de façon décontractée : <span style='color:red;'>{en_informal}</span>",
    "En anglais nous pouvons exprimer : <span style='color:blue;'>{fr}</span> En disant : <span style='color:red;'>{en_abbrev}</span> Et de manière informelle : <span style='color:red;'>{en_informal}</span>",
    "Cette expression : <span style='color:blue;'>{fr}</span> Devient en anglais : <span style='color:red;'>{en_abbrev}</span> Et peut être dite de manière légère : <span style='color:red;'>{en_informal}</span>",
    "En anglais, on peut dire : <span style='color:blue;'>{fr}</span> Ainsi : <span style='color:red;'>{en_abbrev}</span> Et plus familièrement : <span style='color:red;'>{en_informal}</span>",
    "La traduction littérale est : <span style='color:blue;'>{fr}</span> Mais de manière informelle on utilise : <span style='color:red;'>{en_abbrev}</span> Ou encore : <span style='color:red;'>{en_informal}</span>"
  ]
  TEMPLATES_CONTENT_4_ES = [
    "Esta frase: <span style='color:blue;'>{es}</span> En inglés queda: <span style='color:red;'>{en_abbrev}</span> Y puede decirse de forma informal: <span style='color:red;'>{en_informal}</span>",
    "En inglés, la frase: <span style='color:blue;'>{es}</span> Puede decirse como: <span style='color:red;'>{en_abbrev}</span> Y de una manera aún más informal: <span style='color:red;'>{en_informal}</span>",
    "La traducción de esta frase: <span style='color:blue;'>{es}</span> Puede decirse así: <span style='color:red;'>{en_abbrev}</span> De manera más informal puedes decir: <span style='color:red;'>{en_informal}</span>",
    "Podemos decir que esta frase: <span style='color:blue;'>{es}</span> En inglés significa: <span style='color:red;'>{en_abbrev}</span> Y de forma más casual: <span style='color:red;'>{en_informal}</span>",
    "Esta frase en español: <span style='color:blue;'>{es}</span> En inglés decimos: <span style='color:red;'>{en_abbrev}</span> Y de manera informal: <span style='color:red;'>{en_informal}</span>",
    "La frase: <span style='color:blue;'>{es}</span> Puede traducirse como: <span style='color:red;'>{en_abbrev}</span> Y decirse de forma informal: <span style='color:red;'>{en_informal}</span>",
    "En español decimos: <span style='color:blue;'>{es}</span> En inglés, la forma es: <span style='color:red;'>{en_abbrev}</span> Y de manera más natural: <span style='color:red;'>{en_informal}</span>",
    "Mira la frase: <span style='color:blue;'>{es}</span> En inglés sería: <span style='color:red;'>{en_abbrev}</span> Informalmente podemos decir: <span style='color:red;'>{en_informal}</span>",
    "Aquí tenemos: <span style='color:blue;'>{es}</span> La traducción es: <span style='color:red;'>{en_abbrev}</span> Y la forma más relajada: <span style='color:red;'>{en_informal}</span>",
    "Esta es la frase: <span style='color:blue;'>{es}</span> En inglés se dice: <span style='color:red;'>{en_abbrev}</span> Y de forma más natural: <span style='color:red;'>{en_informal}</span>",
    "Podemos traducir así: <span style='color:blue;'>{es}</span> En inglés decimos: <span style='color:red;'>{en_abbrev}</span> Y de forma informal: <span style='color:red;'>{en_informal}</span>",
    "La forma correcta en inglés sería: <span style='color:blue;'>{es}</span> Traducida como: <span style='color:red;'>{en_abbrev}</span> Y de manera más simple: <span style='color:red;'>{en_informal}</span>",
    "Traduciendo al inglés: <span style='color:blue;'>{es}</span> Queda: <span style='color:red;'>{en_abbrev}</span> Y en su versión coloquial: <span style='color:red;'>{en_informal}</span>",
    "En inglés podemos decir: <span style='color:blue;'>{es}</span> Así: <span style='color:red;'>{en_abbrev}</span> O más naturalmente: <span style='color:red;'>{en_informal}</span>",
    "La frase equivalente en inglés es: <span style='color:blue;'>{es}</span> Que queda: <span style='color:red;'>{en_abbrev}</span> Y de manera informal: <span style='color:red;'>{en_informal}</span>",
    "Si traducimos: <span style='color:blue;'>{es}</span> En inglés sería: <span style='color:red;'>{en_abbrev}</span> Y dicho de manera casual: <span style='color:red;'>{en_informal}</span>",
    "En inglés podemos expresar: <span style='color:blue;'>{es}</span> Usando: <span style='color:red;'>{en_abbrev}</span> Y de forma informal: <span style='color:red;'>{en_informal}</span>",
    "Esta expresión: <span style='color:blue;'>{es}</span> En inglés queda: <span style='color:red;'>{en_abbrev}</span> Y puede decirse de forma ligera: <span style='color:red;'>{en_informal}</span>",
    "En inglés, podemos decir: <span style='color:blue;'>{es}</span> Así: <span style='color:red;'>{en_abbrev}</span> Y más informalmente: <span style='color:red;'>{en_informal}</span>",
    "La traducción literal es: <span style='color:blue;'>{es}</span> Pero de forma informal usamos: <span style='color:red;'>{en_abbrev}</span> O también: <span style='color:red;'>{en_informal}</span>"
  ]
  
  # COLOCAR 2 TRADUCÕES PARA O INGLES, MAS NÃO ABREVIACAO.
  TEMPLATES_CONTENT_5_PT = [
    "Pode repetir comigo a frase: <span style='color:blue;'>{pt}</span> Que traduzida em inglês fica: "
    "<span style='color:red;'>{en_full}</span> ou então (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Agora repita comigo: <span style='color:blue;'>{pt}</span> Que em inglês dizemos: "
    "<span style='color:red;'>{en_full}</span> ou pode ser também (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Vamos praticar juntos: <span style='color:blue;'>{pt}</span> A tradução correta em inglês é: "
    "<span style='color:red;'>{en_full}</span> ou ainda (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Repita esta frase comigo: <span style='color:blue;'>{pt}</span> Essa frase em inglês seria: "
    "<span style='color:red;'>{en_full}</span> ou então (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Tente falar comigo: <span style='color:blue;'>{pt}</span> Que em inglês a forma certa é: "
    "<span style='color:red;'>{en_full}</span> ou pode ser também (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Repita comigo a seguinte frase: <span style='color:blue;'>{pt}</span> Falando em inglês fica: "
    "<span style='color:red;'>{en_full}</span> ou ainda (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Vamos repetir juntos: <span style='color:blue;'>{pt}</span> Isso em inglês significa: "
    "<span style='color:red;'>{en_full}</span> ou então (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Tente pronunciar comigo: <span style='color:blue;'>{pt}</span> Traduzida para o inglês significa: "
    "<span style='color:red;'>{en_full}</span> ou pode ser também (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Fale comigo esta frase: <span style='color:blue;'>{pt}</span> Traduzida para o inglês é: "
    "<span style='color:red;'>{en_full}</span> ou então (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Pode treinar comigo dizendo: <span style='color:blue;'>{pt}</span> Em inglês falamos: "
    "<span style='color:red;'>{en_full}</span> ou pode ser também (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Vamos juntos repetir: <span style='color:blue;'>{pt}</span> Essa versão em inglês seria: "
    "<span style='color:red;'>{en_full}</span> ou ainda (stp1) <span style='color:red;'>{en_full_M}</span>",    

    "Em português: <span style='color:blue;'>{pt}</span> Agora repita em inglês: "
    "<span style='color:red;'>{en_full}</span> ou então (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Em português fica assim: <span style='color:blue;'>{pt}</span> Repita em inglês: "
    "<span style='color:red;'>{en_full}</span> ou pode ser também (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Em português temos: <span style='color:blue;'>{pt}</span> Vamos repetir em inglês? "
    "<span style='color:red;'>{en_full}</span> ou ainda (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Falamos assim em português: <span style='color:blue;'>{pt}</span> Você poderia repetir em inglês? "
    "<span style='color:red;'>{en_full}</span> ou então (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Frase em português: <span style='color:blue;'>{pt}</span> Tenta repetir em inglês: "
    "<span style='color:red;'>{en_full}</span> ou pode ser também (stp1) <span style='color:red;'>{en_full_M}</span>"   
  ]
  TEMPLATES_CONTENT_5_IT = [
    "Puoi ripetere con me la frase: <span style='color:blue;'>{it}</span> Che tradotta in inglese diventa: "
    "<span style='color:red;'>{en_full}</span> oppure (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Ora ripeti con me: <span style='color:blue;'>{it}</span> Che in inglese diciamo: "
    "<span style='color:red;'>{en_full}</span> o può essere anche (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Pratichiamo insieme: <span style='color:blue;'>{it}</span> La traduzione corretta in inglese è: "
    "<span style='color:red;'>{en_full}</span> oppure ancora (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Ripeti questa frase con me: <span style='color:blue;'>{it}</span> Questa frase in inglese sarebbe: "
    "<span style='color:red;'>{en_full}</span> oppure (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Prova a parlare con me: <span style='color:blue;'>{it}</span> Che in inglese la forma corretta è: "
    "<span style='color:red;'>{en_full}</span> o può essere anche (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Ripeti con me la seguente frase: <span style='color:blue;'>{it}</span> Detto in inglese diventa: "
    "<span style='color:red;'>{en_full}</span> oppure ancora (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Ripetiamo insieme: <span style='color:blue;'>{it}</span> Questo in inglese significa: "
    "<span style='color:red;'>{en_full}</span> oppure (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Prova a pronunciare con me: <span style='color:blue;'>{it}</span> Tradotta in inglese significa: "
    "<span style='color:red;'>{en_full}</span> o può essere anche (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Di’ con me questa frase: <span style='color:blue;'>{it}</span> Tradotta in inglese è: "
    "<span style='color:red;'>{en_full}</span> oppure (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Puoi allenarti con me dicendo: <span style='color:blue;'>{it}</span> In inglese diciamo: "
    "<span style='color:red;'>{en_full}</span> o può essere anche (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Ripetiamo insieme: <span style='color:blue;'>{it}</span> Questa versione in inglese sarebbe: "
    "<span style='color:red;'>{en_full}</span> oppure ancora (stp1) <span style='color:red;'>{en_full_M}</span>",    

    "In italiano: <span style='color:blue;'>{it}</span> Ora ripeti in inglese: "
    "<span style='color:red;'>{en_full}</span> oppure (stp1) <span style='color:red;'>{en_full_M}</span>",

    "In italiano è così: <span style='color:blue;'>{it}</span> Ripeti in inglese: "
    "<span style='color:red;'>{en_full}</span> o può essere anche (stp1) <span style='color:red;'>{en_full_M}</span>",

    "In italiano abbiamo: <span style='color:blue;'>{it}</span> Ripetiamo in inglese? "
    "<span style='color:red;'>{en_full}</span> oppure ancora (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Così diciamo in italiano: <span style='color:blue;'>{it}</span> Potresti ripetere in inglese? "
    "<span style='color:red;'>{en_full}</span> oppure (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Frase in italiano: <span style='color:blue;'>{it}</span> Prova a ripetere in inglese: "
    "<span style='color:red;'>{en_full}</span> o può essere anche (stp1) <span style='color:red;'>{en_full_M}</span>"

  ]
  TEMPLATES_CONTENT_5_FR = [
    "Peux-tu répéter avec moi la phrase : <span style='color:blue;'>{fr}</span> Qui, traduite en anglais, devient : "
    "<span style='color:red;'>{en_full}</span> ou alors (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Maintenant répète avec moi : <span style='color:blue;'>{fr}</span> Qu’en anglais on dit : "
    "<span style='color:red;'>{en_full}</span> ou peut aussi être (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Pratiquons ensemble : <span style='color:blue;'>{fr}</span> La traduction correcte en anglais est : "
    "<span style='color:red;'>{en_full}</span> ou encore (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Répète cette phrase avec moi : <span style='color:blue;'>{fr}</span> Cette phrase en anglais serait : "
    "<span style='color:red;'>{en_full}</span> ou alors (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Essaie de parler avec moi : <span style='color:blue;'>{fr}</span> Qu’en anglais, la forme correcte est : "
    "<span style='color:red;'>{en_full}</span> ou peut aussi être (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Répète avec moi la phrase suivante : <span style='color:blue;'>{fr}</span> En anglais, cela devient : "
    "<span style='color:red;'>{en_full}</span> ou encore (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Répétons ensemble : <span style='color:blue;'>{fr}</span> Cela signifie en anglais : "
    "<span style='color:red;'>{en_full}</span> ou alors (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Essaie de prononcer avec moi : <span style='color:blue;'>{fr}</span> Traduit en anglais, cela signifie : "
    "<span style='color:red;'>{en_full}</span> ou peut aussi être (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Dis cette phrase avec moi : <span style='color:blue;'>{fr}</span> Traduit en anglais, c’est : "
    "<span style='color:red;'>{en_full}</span> ou alors (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Tu peux t’entraîner avec moi en disant : <span style='color:blue;'>{fr}</span> En anglais, on dit : "
    "<span style='color:red;'>{en_full}</span> ou peut aussi être (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Répétons ensemble : <span style='color:blue;'>{fr}</span> Cette version en anglais serait : "
    "<span style='color:red;'>{en_full}</span> ou encore (stp1) <span style='color:red;'>{en_full_M}</span>",    

    "En français : <span style='color:blue;'>{fr}</span> Maintenant répète en anglais : "
    "<span style='color:red;'>{en_full}</span> ou alors (stp1) <span style='color:red;'>{en_full_M}</span>",

    "En français, c’est ainsi : <span style='color:blue;'>{fr}</span> Répète en anglais : "
    "<span style='color:red;'>{en_full}</span> ou peut aussi être (stp1) <span style='color:red;'>{en_full_M}</span>",

    "En français, nous avons : <span style='color:blue;'>{fr}</span> Répétons en anglais ? "
    "<span style='color:red;'>{en_full}</span> ou encore (stp1) <span style='color:red;'>{en_full_M}</span>",

    "On dit ainsi en français : <span style='color:blue;'>{fr}</span> Pourrais-tu répéter en anglais ? "
    "<span style='color:red;'>{en_full}</span> ou alors (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Phrase en français : <span style='color:blue;'>{fr}</span> Essaie de répéter en anglais : "
    "<span style='color:red;'>{en_full}</span> ou peut aussi être (stp1) <span style='color:red;'>{en_full_M}</span>"

  ]
  TEMPLATES_CONTENT_5_ES = [
    "Puedes repetir conmigo la frase: <span style='color:blue;'>{es}</span> Que traducida al inglés queda: "
    "<span style='color:red;'>{en_full}</span> o entonces (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Ahora repite conmigo: <span style='color:blue;'>{es}</span> Que en inglés decimos: "
    "<span style='color:red;'>{en_full}</span> o también puede ser (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Vamos a practicar juntos: <span style='color:blue;'>{es}</span> La traducción correcta al inglés es: "
    "<span style='color:red;'>{en_full}</span> o incluso (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Repite esta frase conmigo: <span style='color:blue;'>{es}</span> Esta frase en inglés sería: "
    "<span style='color:red;'>{en_full}</span> o entonces (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Intenta hablar conmigo: <span style='color:blue;'>{es}</span> Que en inglés la forma correcta es: "
    "<span style='color:red;'>{en_full}</span> o también puede ser (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Repite conmigo la siguiente frase: <span style='color:blue;'>{es}</span> Dicho en inglés queda: "
    "<span style='color:red;'>{en_full}</span> o incluso (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Vamos a repetir juntos: <span style='color:blue;'>{es}</span> Esto en inglés significa: "
    "<span style='color:red;'>{en_full}</span> o entonces (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Intenta pronunciar conmigo: <span style='color:blue;'>{es}</span> Traducida al inglés significa: "
    "<span style='color:red;'>{en_full}</span> o también puede ser (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Di conmigo esta frase: <span style='color:blue;'>{es}</span> Traducida al inglés es: "
    "<span style='color:red;'>{en_full}</span> o entonces (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Puedes entrenar conmigo diciendo: <span style='color:blue;'>{es}</span> En inglés decimos: "
    "<span style='color:red;'>{en_full}</span> o también puede ser (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Vamos a repetir juntos: <span style='color:blue;'>{es}</span> Esta versión en inglés sería: "
    "<span style='color:red;'>{en_full}</span> o incluso (stp1) <span style='color:red;'>{en_full_M}</span>",    

    "En español: <span style='color:blue;'>{es}</span> Ahora repite en inglés: "
    "<span style='color:red;'>{en_full}</span> o entonces (stp1) <span style='color:red;'>{en_full_M}</span>",

    "En español queda así: <span style='color:blue;'>{es}</span> Repite en inglés: "
    "<span style='color:red;'>{en_full}</span> o también puede ser (stp1) <span style='color:red;'>{en_full_M}</span>",

    "En español tenemos: <span style='color:blue;'>{es}</span> ¿Repetimos en inglés? "
    "<span style='color:red;'>{en_full}</span> o incluso (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Así hablamos en español: <span style='color:blue;'>{es}</span> ¿Podrías repetir en inglés? "
    "<span style='color:red;'>{en_full}</span> o entonces (stp1) <span style='color:red;'>{en_full_M}</span>",

    "Frase en español: <span style='color:blue;'>{es}</span> Intenta repetir en inglés: "
    "<span style='color:red;'>{en_full}</span> o también puede ser (stp1) <span style='color:red;'>{en_full_M}</span>"
  ]
  
  TEMPLATES_CONTENT_6_PT = [
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Agora repita.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Agora tente repitir.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Pode repetir tranquilamente.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Agora fale você.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Fale em inglês.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Diga em inglês.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Sua vez, pode repetir.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Agora repita você.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Sua vez de falar.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Agora repita em inglês.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Sua vez agora.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Agora pode repetir.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Pode repetir agora.", 
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Vamos repetir juntos.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Pode falar agora.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Agora tente falar.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Tente repetir agora.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Pode tentar repetir.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Fale com calma.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Repita com calma.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Vamos tentar juntos.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Pode falar tranquilo.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Fale sem pressa.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Repita sem pressa.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Agora tente novamente.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Pode repetir novamente.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Vamos falar juntos.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Sua vez de repetir.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Pode falar você.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Tente falar agora.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Fale no seu tempo.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Repita no seu tempo.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Vamos repetir agora.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Pode tentar agora.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Agora diga você.",
    "<span style='color:blue;'>{pt}</span> <span style='color:red;'>{en_full}</span> Vamos dizer juntos."
  ]
  TEMPLATES_CONTENT_6_FR = [
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Tu peux répéter.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Répète maintenant.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Parle maintenant.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> À toi de parler.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Répétons ensemble.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Tu peux parler.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Essaie de parler.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Essaie de répéter.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Tu peux essayer.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Parle calmement.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Répète calmement.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Dis à voix.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> À toi maintenant.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Essayons ensemble.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Parle tranquillement.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Sans te presser.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Répète sans presser.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Essaie encore.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Tu peux répéter encore.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Parlons ensemble.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> À toi de répéter.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> C’est à toi.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Tu peux parler.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Essaie maintenant.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> À ton rythme.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Répète à ton rythme.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Répétons maintenant.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Tu peux essayer.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Dis-le toi.",
    "<span style='color:blue;'>{fr}</span> <span style='color:red;'>{en_full}</span> Disons ensemble."
  ]
  TEMPLATES_CONTENT_6_ES = [
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Ahora puedes repetir.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Puedes repetir ahora.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Ahora habla tú.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Tu turno de hablar.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Vamos a repetir.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Puedes hablar ahora.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Ahora intenta hablar.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Intenta repetir ahora.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Puedes intentar repetir.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Habla con calma.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Repite con calma.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Ahora di en voz.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Tu turno ahora mismo.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Vamos a intentar.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Puedes hablar tranquilo.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Habla sin prisa.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Repite sin prisa.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Ahora intenta nuevamente.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Puedes repetir nuevamente.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Vamos a hablar.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Tu turno de repetir.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Ahora es tuya.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Puedes hablar tú.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Intenta hablar ahora.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Habla a tu ritmo.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Repite a tu ritmo.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Vamos a repetir.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Puedes intentar ahora.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Ahora di tú.",
    "<span style='color:blue;'>{es}</span> <span style='color:red;'>{en_full}</span> Vamos a decir."
  ]
  TEMPLATES_CONTENT_6_IT = [
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ora puoi ripetere.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Puoi ripetere ora.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ora parla tu.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Il tuo turno parlare.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ripetiamo insieme.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Puoi parlare ora.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ora prova parlare.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Prova ripetere ora.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Puoi provare ripetere.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Parla con calma.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ripeti con calma.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ora dì a voce.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Il tuo turno ora.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Proviamo insieme.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Parla tranquillo.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Parla senza fretta.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ripeti senza fretta.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ora prova ancora.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Puoi ripetere ancora.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Parliamo insieme.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Il tuo turno ripetere.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ora tocca a te.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Puoi parlare tu.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Prova parlare ora.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Parla al tuo ritmo.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ripeti al tuo ritmo.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ripetiamo ora.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Puoi provare ora.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Ora dì tu.",
    "<span style='color:blue;'>{it}</span> <span style='color:red;'>{en_full}</span> Diciamo insieme."
  ]
    
  TEMPLATES_CONTENT_7_PT = [
    "<span style='color:blue;'>{pt}</span> Agora pode repetir.",
    "<span style='color:blue;'>{pt}</span> Pode repetir agora.",
    "<span style='color:blue;'>{pt}</span> Agora fale você.",
    "<span style='color:blue;'>{pt}</span> Sua vez de falar.",
    "<span style='color:blue;'>{pt}</span> Vamos repetir juntos.",
    "<span style='color:blue;'>{pt}</span> Pode falar agora.",
    "<span style='color:blue;'>{pt}</span> Agora tente falar.",
    "<span style='color:blue;'>{pt}</span> Tente repetir agora.",
    "<span style='color:blue;'>{pt}</span> Pode tentar repetir.",
    "<span style='color:blue;'>{pt}</span> Fale com calma.",
    "<span style='color:blue;'>{pt}</span> Repita com calma.",
    "<span style='color:blue;'>{pt}</span> Agora diga em voz.",
    "<span style='color:blue;'>{pt}</span> Sua vez agora mesmo.",
    "<span style='color:blue;'>{pt}</span> Vamos tentar juntos.",
    "<span style='color:blue;'>{pt}</span> Pode falar tranquilo.",
    "<span style='color:blue;'>{pt}</span> Fale sem pressa.",
    "<span style='color:blue;'>{pt}</span> Repita sem pressa.",
    "<span style='color:blue;'>{pt}</span> Agora tente novamente.",
    "<span style='color:blue;'>{pt}</span> Pode repetir novamente.",
    "<span style='color:blue;'>{pt}</span> Vamos falar juntos.",
    "<span style='color:blue;'>{pt}</span> Sua vez de repetir.",
    "<span style='color:blue;'>{pt}</span> Agora é sua.",
    "<span style='color:blue;'>{pt}</span> Pode falar você.",
    "<span style='color:blue;'>{pt}</span> Tente falar agora.",
    "<span style='color:blue;'>{pt}</span> Fale no seu tempo.",
    "<span style='color:blue;'>{pt}</span> Repita no seu tempo.",
    "<span style='color:blue;'>{pt}</span> Vamos repetir agora.",
    "<span style='color:blue;'>{pt}</span> Pode tentar agora.",
    "<span style='color:blue;'>{pt}</span> Agora diga você.",
    "<span style='color:blue;'>{pt}</span> Vamos dizer juntos."
  ]
  TEMPLATES_CONTENT_7_FR = [
    "<span style='color:blue;'>{fr}</span> Tu peux répéter.",
    "<span style='color:blue;'>{fr}</span> Répète maintenant.",
    "<span style='color:blue;'>{fr}</span> Parle maintenant.",
    "<span style='color:blue;'>{fr}</span> À toi de parler.",
    "<span style='color:blue;'>{fr}</span> Répétons ensemble.",
    "<span style='color:blue;'>{fr}</span> Tu peux parler.",
    "<span style='color:blue;'>{fr}</span> Essaie de parler.",
    "<span style='color:blue;'>{fr}</span> Essaie de répéter.",
    "<span style='color:blue;'>{fr}</span> Tu peux essayer.",
    "<span style='color:blue;'>{fr}</span> Parle calmement.",
    "<span style='color:blue;'>{fr}</span> Répète calmement.",
    "<span style='color:blue;'>{fr}</span> Dis à voix.",
    "<span style='color:blue;'>{fr}</span> À toi maintenant.",
    "<span style='color:blue;'>{fr}</span> Essayons ensemble.",
    "<span style='color:blue;'>{fr}</span> Parle tranquillement.",
    "<span style='color:blue;'>{fr}</span> Sans te presser.",
    "<span style='color:blue;'>{fr}</span> Répète sans presser.",
    "<span style='color:blue;'>{fr}</span> Essaie encore.",
    "<span style='color:blue;'>{fr}</span> Tu peux répéter encore.",
    "<span style='color:blue;'>{fr}</span> Parlons ensemble.",
    "<span style='color:blue;'>{fr}</span> À toi de répéter.",
    "<span style='color:blue;'>{fr}</span> C’est à toi.",
    "<span style='color:blue;'>{fr}</span> Tu peux parler.",
    "<span style='color:blue;'>{fr}</span> Essaie maintenant.",
    "<span style='color:blue;'>{fr}</span> À ton rythme.",
    "<span style='color:blue;'>{fr}</span> Répète à ton rythme.",
    "<span style='color:blue;'>{fr}</span> Répétons maintenant.",
    "<span style='color:blue;'>{fr}</span> Tu peux essayer.",
    "<span style='color:blue;'>{fr}</span> Dis-le toi.",
    "<span style='color:blue;'>{fr}</span> Disons ensemble."
  ]
  TEMPLATES_CONTENT_7_ES = [
    "<span style='color:blue;'>{es}</span> Ahora puedes repetir.",
    "<span style='color:blue;'>{es}</span> Puedes repetir ahora.",
    "<span style='color:blue;'>{es}</span> Ahora habla tú.",
    "<span style='color:blue;'>{es}</span> Tu turno de hablar.",
    "<span style='color:blue;'>{es}</span> Vamos a repetir.",
    "<span style='color:blue;'>{es}</span> Puedes hablar ahora.",
    "<span style='color:blue;'>{es}</span> Ahora intenta hablar.",
    "<span style='color:blue;'>{es}</span> Intenta repetir ahora.",
    "<span style='color:blue;'>{es}</span> Puedes intentar repetir.",
    "<span style='color:blue;'>{es}</span> Habla con calma.",
    "<span style='color:blue;'>{es}</span> Repite con calma.",
    "<span style='color:blue;'>{es}</span> Ahora di en voz.",
    "<span style='color:blue;'>{es}</span> Tu turno ahora mismo.",
    "<span style='color:blue;'>{es}</span> Vamos a intentar.",
    "<span style='color:blue;'>{es}</span> Puedes hablar tranquilo.",
    "<span style='color:blue;'>{es}</span> Habla sin prisa.",
    "<span style='color:blue;'>{es}</span> Repite sin prisa.",
    "<span style='color:blue;'>{es}</span> Ahora intenta nuevamente.",
    "<span style='color:blue;'>{es}</span> Puedes repetir nuevamente.",
    "<span style='color:blue;'>{es}</span> Vamos a hablar.",
    "<span style='color:blue;'>{es}</span> Tu turno de repetir.",
    "<span style='color:blue;'>{es}</span> Ahora es tuya.",
    "<span style='color:blue;'>{es}</span> Puedes hablar tú.",
    "<span style='color:blue;'>{es}</span> Intenta hablar ahora.",
    "<span style='color:blue;'>{es}</span> Habla a tu ritmo.",
    "<span style='color:blue;'>{es}</span> Repite a tu ritmo.",
    "<span style='color:blue;'>{es}</span> Vamos a repetir.",
    "<span style='color:blue;'>{es}</span> Puedes intentar ahora.",
    "<span style='color:blue;'>{es}</span> Ahora di tú.",
    "<span style='color:blue;'>{es}</span> Vamos a decir."
  ]
  TEMPLATES_CONTENT_7_IT = [
    "<span style='color:blue;'>{it}</span> Ora puoi ripetere.",
    "<span style='color:blue;'>{it}</span> Puoi ripetere ora.",
    "<span style='color:blue;'>{it}</span> Ora parla tu.",
    "<span style='color:blue;'>{it}</span> Il tuo turno parlare.",
    "<span style='color:blue;'>{it}</span> Ripetiamo insieme.",
    "<span style='color:blue;'>{it}</span> Puoi parlare ora.",
    "<span style='color:blue;'>{it}</span> Ora prova parlare.",
    "<span style='color:blue;'>{it}</span> Prova ripetere ora.",
    "<span style='color:blue;'>{it}</span> Puoi provare ripetere.",
    "<span style='color:blue;'>{it}</span> Parla con calma.",
    "<span style='color:blue;'>{it}</span> Ripeti con calma.",
    "<span style='color:blue;'>{it}</span> Ora dì a voce.",
    "<span style='color:blue;'>{it}</span> Il tuo turno ora.",
    "<span style='color:blue;'>{it}</span> Proviamo insieme.",
    "<span style='color:blue;'>{it}</span> Parla tranquillo.",
    "<span style='color:blue;'>{it}</span> Parla senza fretta.",
    "<span style='color:blue;'>{it}</span> Ripeti senza fretta.",
    "<span style='color:blue;'>{it}</span> Ora prova ancora.",
    "<span style='color:blue;'>{it}</span> Puoi ripetere ancora.",
    "<span style='color:blue;'>{it}</span> Parliamo insieme.",
    "<span style='color:blue;'>{it}</span> Il tuo turno ripetere.",
    "<span style='color:blue;'>{it}</span> Ora tocca a te.",
    "<span style='color:blue;'>{it}</span> Puoi parlare tu.",
    "<span style='color:blue;'>{it}</span> Prova parlare ora.",
    "<span style='color:blue;'>{it}</span> Parla al tuo ritmo.",
    "<span style='color:blue;'>{it}</span> Ripeti al tuo ritmo.",
    "<span style='color:blue;'>{it}</span> Ripetiamo ora.",
    "<span style='color:blue;'>{it}</span> Puoi provare ora.",
    "<span style='color:blue;'>{it}</span> Ora dì tu.",
    "<span style='color:blue;'>{it}</span> Diciamo insieme."
  ]

