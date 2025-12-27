from django.contrib import admin
from .models import Chat
import random, re
from deep_translator import GoogleTranslator
from django.db import models
from django import forms
from .admin_forms import ChatAdminForm




@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
  form = ChatAdminForm
  # ORDEM DO FORM
  fields = (
    "lesson_id",
    "seq",
    "role",
    "lang",
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
    "id",
    "lesson_id",
    "seq",
    "role",
    "lang",
    "expected_pt",
    "expected_en",
    "expected_it",
    "expected_fr",
    "expected_es",
    "status",
    "created_at",
  )
  # DEFINE CAMPOS COM 100%
  formfield_overrides = {
    models.CharField: {
        "widget": forms.TextInput(attrs={"style": "width: 100%;"})
    },
    models.TextField: {
        "widget": forms.Textarea(attrs={"style": "width: 100%;"})
    },
  }
  
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
  # FUNCAO ABREVIADO E FULL
  def contract_en(self, t: str) -> str:
    reps = [
      (r"\bi am\b", "I'm"),
      (r"\byou are\b", "you're"),
      (r"\bwe are\b", "we're"),
      (r"\bthey are\b", "they're"),
      (r"\bi have\b", "I've"),
      (r"\byou have\b", "you've"),
      (r"\bwe have\b", "we've"),
      (r"\bthey have\b", "they've"),
      (r"\bi will\b", "I'll"),
      (r"\byou will\b", "you'll"),
      (r"\bwe will\b", "we'll"),
      (r"\bthey will\b", "they'll"),
      (r"\bdo not\b", "don't"),
      (r"\bdoes not\b", "doesn't"),
      (r"\bdid not\b", "didn't"),
      (r"\bgoing to\b", "gonna"),
      (r"\bcan not\b", "cannot"),
      (r"\bwill not\b", "won't"),
      (r"\bis not\b", "isn't"),
      (r"\bare not\b", "aren't"),
    ]

    for regex, repl in reps:
        t = re.sub(regex, repl, t, flags=re.IGNORECASE)
    return t

  # Move ., ?, ! ou : de dentro do </span> para fora.
  def mover_pontuacao(self, texto: str) -> str:    
    return re.sub(r'([.!?:])</span>', r'</span>\1', texto)
  
  def norm_dict(s):
    return re.sub(r"[.:!?]", "", s).lower().strip()
    
  # TRADUZ, DEFINE FRASES ABREVIADAS E INFORMAIS, E ESCOLHE O TEMPLATE.
  def save_model(self, request, obj, form, change):    
    
    from apps.chat.utils.dictionary_writer import add_term, term_exists
    
    def norm_dict(s):
        s = s or ""
        s = re.sub(r"[.:!?]", "", s)
        return s.lower().strip()
      
    en_full = obj.expected_en or ""
    en_abbrev = self.contract_en(en_full) if en_full else ""
    en_informal = self.gerar_informal(en_full) if en_full else ""
        
    for txt in (en_full, en_abbrev, en_informal):
        termo = norm_dict(txt)
        if termo and not term_exists("en", termo):
            add_term("en", termo)    

    # traduções base
    try:
      pt = GoogleTranslator(source="en", target="pt").translate(en_full)
      es = GoogleTranslator(source="en", target="es").translate(en_full)
      fr = GoogleTranslator(source="en", target="fr").translate(en_full)
      it = GoogleTranslator(source="en", target="it").translate(en_full)
    except Exception:
      pt = es = fr = it = None
 
    # AQUI GRAVA NO JSON A AS VARIAVEIS
    
    
    # 4) cadastra traduções NORMALIZADAS também (pra ficar tudo consistente)
    entries = {"pt": pt, "es": es, "fr": fr, "it": it}
    for lang, text in entries.items():
        termo = norm_dict(text)
        if termo and not term_exists(lang, termo):
            add_term(lang, termo)

    # entries = {
    #     "en": en_full,
    #     "pt": pt,
    #     "es": es,
    #     "fr": fr,
    #     "it": it,
    # }

    # for lang, text in entries.items():
    #     if text and not term_exists(lang, text):
    #         add_term(lang, text)              
    # FIM AQUI GRAVA NO JSON A AS VARIAVEIS

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
          en_abbrev=en_abbrev,
          en_informal=en_informal,
          pt=pt
      )
      obj.content_pt = self.mover_pontuacao(texto)

    if not obj.content_es:
      texto = random.choice(templates_es).format(
          en_full=en_full,
          en_abbrev=en_abbrev,
          en_informal=en_informal,
          es=es
      )
      obj.content_es = self.mover_pontuacao(texto)

    if not obj.content_fr:
      texto = random.choice(templates_fr).format(
          en_full=en_full,
          en_abbrev=en_abbrev,
          en_informal=en_informal,
          fr=fr
      )
      obj.content_fr = self.mover_pontuacao(texto)

    if not obj.content_it:
      texto = random.choice(templates_it).format(
          en_full=en_full,
          en_abbrev=en_abbrev,
          en_informal=en_informal,
          it=it
      )
      obj.content_it = self.mover_pontuacao(texto)      
 
    super().save_model(request, obj, form, change)

  # FRASES COM ABREVIACOES E SEM ABREVIACOES
  TEMPLATES_CONTENT_1_PT = [     
    "Veja essa frase: <span style='color:blue;'>{pt}</span> "
    "Agora em inglês abreviado: <span style='color:red;'>{en_abbrev}</span> "
    "E sem abreviar fica assim: <span style='color:red;'>{en_full}</span>",
    
    "Dá pra dizer abreviado: <span style='color:red;'>{en_abbrev}</span> "
    "Ou sem abreviação: <span style='color:red;'>{en_full}</span> "
    "Significa: <span style='color:blue;'>{pt}</span>",
    
    "Próxima frase é: <span style='color:blue;'>{pt}</span> "
    "Abrevida em inglês: <span style='color:red;'>{en_abbrev}</span> "
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
    "Você sabe como dizer isso em inglês? (stp3) <span style='color:blue;'>{pt}</span>",
    "Tente dizer em inglês a frase: (stp1) <span style='color:blue;'>{pt}</span>",
    "Consegue traduzir para o inglês esta frase? (stp1) <span style='color:blue;'>{pt}</span>",
    "Como ficaria em inglês esta frase? (stp1) <span style='color:blue;'>{pt}</span>",
    "Pense rápido. Como se fala em inglês? (stp1) <span style='color:blue;'>{pt}</span>",
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
    "A tradução literal é: <span style='color:blue;'>{pt}</span> Mas de forma informal, usamos: <span style='color:red;'>{en_abbrev}</span> Ou ainda: <span style='color:red;'>{en_informal}</span>"
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
  
  # NÃO DEFINIDO
  TEMPLATES_CONTENT_5_PT = [
    "Não definido ainda!!!"    
  ]
  TEMPLATES_CONTENT_5_IT = [
    "Não definido ainda!!!"
  ]
  TEMPLATES_CONTENT_5_FR = [
    "Não definido ainda!!!"
  ]
  TEMPLATES_CONTENT_5_ES = [
    "Não definido ainda!!!"
  ]