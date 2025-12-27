import re
import unicodedata

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
# DETECTOR (SEM LANGID)
# =========================
def detectar_idioma(frase: str) -> str:
    """
    ORDEM FIXA:
    1) Dicionário
    2) Heurísticas
    3) Fallback previsível ("en")
    """

    # 1️⃣ DICIONÁRIO (PRIORIDADE TOTAL)
    frase_n = _norm(frase)

    if term_exists("pt", frase_n):
        return "pt"
    if term_exists("en", frase_n):
        return "en"

    # 2️⃣ HEURÍSTICAS
    raw = re.sub(r"<[^>]+>", "", frase or "")
    text_norm_pt = _norm(raw)
    text_norm_en = _norm_en(raw)

    # acentos → PT
    if re.search(r"[áàâãäéèêëíìîïóòôõöúùûüç]", raw, re.I):
        return "pt"

    # contrações EN (don't, I'm, it's)
    if re.search(r"\b[a-z]+'[a-z]+\b", text_norm_en):
        return "en"

    # morfologia PT
    if re.search(
        r"\b[a-z]{3,}(mos|ram|rei|rão|ava|avam|aria|ariam|esse|asse|emos|indo|ando|endo)\b",
        text_norm_pt
    ):
        return "pt"

    # stopwords PT
    if re.search(
        r"\b(e|ele|eles|de|da|das|dos|na|nas|um|uma|uns|umas|sim|não|que|pra|pro|tá|né|pois|então|mas|porque|como|quando|onde|já|também|ainda|agora)\b",
        text_norm_pt
    ):
        return "pt"

    # 3️⃣ FALLBACK FINAL (controlado)
    return "en"
