import re

def normalize(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"[^\w\s:']", "", text)
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
    # if len(spoken_tokens) > len(expected_tokens):
    #     errors += 1
    if len(spoken_tokens) != len(expected_tokens):
        #errors += 1
        errors += abs(len(spoken_tokens) - len(expected_tokens))

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
