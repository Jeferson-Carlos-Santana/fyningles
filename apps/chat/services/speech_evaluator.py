import re

def normalize(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    # normalização de contrações (básico)
    contractions = {
        "don't": "do not",
        "doesn't": "does not",
        "didn't": "did not",
        "i'm": "i am",
        "you're": "you are",
        "he's": "he is",
        "she's": "she is",
        "it's": "it is",
        "we're": "we are",
        "they're": "they are",
        "can't": "can not",
        "won't": "will not",
    }

    for c, expanded in contractions.items():
        text = re.sub(rf"\b{re.escape(c)}\b", expanded, text)

    # normalização de números por extenso
    numbers = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
    }

    for word, digit in numbers.items():
        text = re.sub(rf"\b{word}\b", digit, text)

    # limpeza padrão (igual à versão antiga)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    return text.split(" ")


def align_words(expected: list[str], spoken: list[str]) -> int:
    """
    Retorna quantas palavras do expected aparecem no spoken, em ordem,
    ignorando palavras extras no spoken. (LCS por palavras)
    """
    n, m = len(expected), len(spoken)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        ei = expected[i - 1]
        for j in range(1, m + 1):
            sj = spoken[j - 1]
            if ei == sj:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[n][m]


def evaluate(expected_text: str, spoken_text: str) -> dict:
    expected_tokens = tokenize(normalize(expected_text))
    spoken_tokens = tokenize(normalize(spoken_text))

    total = len(expected_tokens)

    # acertos reais (LCS)
    correct = align_words(expected_tokens, spoken_tokens)

    # erros por falta ou troca
    errors = total - correct

    # penalidade fixa por palavras a mais
    if len(spoken_tokens) > len(expected_tokens):
        errors += 1

    # limite inferior: nunca negativo
    if errors > total:
        errors = total

    correct = total - errors
    if correct < 0:
        correct = 0

    return {
        "total_words": total,
        "correct": correct,
        "errors": errors,
    }
