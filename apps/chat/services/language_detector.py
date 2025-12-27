import re
import unicodedata
import langid

from apps.chat.utils.dictionary_writer import term_exists

# =========================
# NORMALIZAÇÃO
# =========================
def _norm(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text)

def _norm_en(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.lower().strip())


# =========================
# DETECTOR (COM LANGID)
# =========================
def detectar_idioma(frase: str) -> str:
    """
    ORDEM (igual ao projeto antigo):
    1) Dicionário
    2) Heurísticas
    3) langid (fallback estatístico)
    4) 'en'
    """

    # 🔹 limpeza base (igual ao antigo)
    raw = frase or ""
    raw = re.sub(r"</span>\.", "</span>", raw)
    raw = re.sub(r"<[^>]+>", "", raw)
    raw = re.sub(r"[.!?:]{1,2}$", "", raw).strip()
    raw = re.sub(r"\s+", " ", raw).strip()

    # =========================
    # 1️⃣ DICIONÁRIO (PRIORIDADE TOTAL)
    # =========================
    fr_pt = _norm(raw)
    fr_en = _norm_en(raw)

    if term_exists("pt", fr_pt):
        return "pt"
    if term_exists("en", fr_en):
        return "en"

    # =========================
    # 2️⃣ HEURÍSTICAS (IGUAIS AO ANTIGO)
    # =========================

    # acentos → PT
    if re.search(r"[áàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ]", raw, re.I):
        return "pt"

    # morfologia PT
    if re.search(
        r"\b[a-z]{3,}(mos|ram|rei|rão|ava|avam|aria|ariam|esse|asse|emos|indo|ando|endo)\b",
        fr_pt
    ):
        return "pt"

    # stopwords PT
    if re.search(
        r"\b(e|ele|eles|de|da|das|dos|na|nas|um|uma|uns|umas|sim|não|que|pra|pro|tá|né|pois|então|mas|porque|como|quando|onde|já|também|ainda|agora)\b",
        fr_pt
    ):
        return "pt"

    # contrações EN
    if re.search(r"\b[a-z]+'[a-z]+\b", fr_en):
        return "en"

    # =========================
    # 3️⃣ LANGID (FALLBACK REAL — IGUAL AO PROJETO ANTIGO)
    # =========================
    try:
        idioma, confianca = langid.classify(raw)
        if idioma in ("pt", "en") and confianca > 0.7:
            return idioma
    except Exception:
        pass

    # =========================
    # 4️⃣ FALLBACK FINAL
    # =========================
    return "en"
