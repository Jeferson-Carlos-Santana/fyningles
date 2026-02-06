import re

def normalize(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    # normalização de contrações (básico)
    contractions = { 
        "i'm": "i am",
        "you're": "you are",
        "he's": "he is",
        "she's": "she is",
        "it's": "it is",
        "we're": "we are",
        "they're": "they are",
        "i've": "i have",
        "you've": "you have",
        "we've": "we have",
        "they've": "they have",
        "i'd": "i would",
        "you'd": "you would",
        "he'd": "he would",
        "she'd": "she would",
        "we'd": "we would",
        "they'd": "they would",
        "i'll": "i will",
        "you'll": "you will",
        "he'll": "he will",
        "she'll": "she will",
        "we'll": "we will",
        "they'll": "they will",
        "isn't": "is not",
        "aren't": "are not",
        "wasn't": "was not",
        "weren't": "were not",
        "don't": "do not",
        "doesn't": "does not",
        "didn't": "did not",
        "haven't": "have not",
        "hasn't": "has not",
        "hadn't": "had not",
        "can't": "can not",
        "couldn't": "could not",
        "shouldn't": "should not",
        "wouldn't": "would not",
        "mightn't": "might not",
        "mustn't": "must not",
        "won't": "will not",
        "shan't": "shall not",
        "could've": "could have",
        "should've": "should have",
        "would've": "would have",
        "might've": "might have",
        "must've": "must have",
        "what's": "what is",
        "where's": "where is",
        "who's": "who is",
        "how's": "how is",
        "when's": "when is",
        "why's": "why is",
        "there's": "there is",
        "here's": "here is",
        "that's": "that is",
        "this's": "this is",
        "let's": "let us",
        "gonna": "going to",
        "wanna": "want to",
        "gotta": "got to"
    }
    
    for a, b in contractions.items():
        text = re.sub(rf"\b{re.escape(a)}\b", f"__TMP__{b}__", text)
    for a, b in contractions.items():
        text = re.sub(rf"__TMP__{re.escape(b)}__", b, text)


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
        
    # horas em "oclock"
    hours = {
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
        "eleven": "11", 
        "twelve": "12"
    }

    for word, num in hours.items():
        text = re.sub(rf"\b{word}\s+oclock\b", f"{num}:00", text)

    # limpeza padrão (igual à versão antiga)
    # text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"[^\w\s:']", "", text)  #[^\w\s:']

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
