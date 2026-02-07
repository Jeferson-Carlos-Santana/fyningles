import re

def normalize(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    # normalização de contrações (básico)
    contractions = {
        "i'm":"i am","i am":"i'm",
        "you're":"you are","you are":"you're",
        "he's":"he is","he is":"he's",
        "she's":"she is","she is":"she's",
        "it's":"it is","it is":"it's",
        "we're":"we are","we are":"we're",
        "they're":"they are","they are":"they're",
        "i've":"i have","i have":"i've",
        "you've":"you have","you have":"you've",
        "we've":"we have","we have":"we've",
        "they've":"they have","they have":"they've",
        "i'd":"i would","i would":"i'd",
        "you'd":"you would","you would":"you'd",
        "he'd":"he would","he would":"he'd",
        "she'd":"she would","she would":"she'd",
        "we'd":"we would","we would":"we'd",
        "they'd":"they would","they would":"they'd",
        "i'll":"i will","i will":"i'll",
        "you'll":"you will","you will":"you'll",
        "he'll":"he will","he will":"he'll",
        "she'll":"she will","she will":"she'll",
        "we'll":"we will","we will":"we'll",
        "they'll":"they will","they will":"they'll",
        "isn't":"is not","is not":"isn't",
        "aren't":"are not","are not":"aren't",
        "wasn't":"was not","was not":"wasn't",
        "weren't":"were not","were not":"weren't",
        "don't":"do not","do not":"don't",
        "doesn't":"does not","does not":"doesn't",
        "didn't":"did not","did not":"didn't",
        "haven't":"have not","have not":"haven't",
        "hasn't":"has not","has not":"hasn't",
        "hadn't":"had not","had not":"hadn't",
        "can't":"can not","can not":"can't",
        "couldn't":"could not","could not":"couldn't",
        "shouldn't":"should not","should not":"shouldn't",
        "wouldn't":"would not","would not":"wouldn't",
        "mightn't":"might not","might not":"mightn't",
        "mustn't":"must not","must not":"mustn't",
        "won't":"will not","will not":"won't",
        "shan't":"shall not","shall not":"shan't",
        "could've":"could have","could have":"could've",
        "should've":"should have","should have":"should've",
        "would've":"would have","would have":"would've",
        "might've":"might have","might have":"might've",
        "must've":"must have","must have":"must've",
        "what's":"what is","what is":"what's",
        "where's":"where is","where is":"where's",
        "who's":"who is","who is":"who's",
        "how's":"how is","how is":"how's",
        "when's":"when is","when is":"when's",
        "why's":"why is","why is":"why's",
        "there's":"there is","there is":"there's",
        "here's":"here is","here is":"here's",
        "that's":"that is","that is":"that's",
        "this's":"this is","this is":"this's",
        "let's":"let us","let us":"let's",
        "gonna":"going to","going to":"gonna",
        "wanna":"want to",
        "gotta":"got to","got to":"gotta",
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

    # AM / PM PRIMEIRO
    def _am_pm(m):
        hour = int(m.group(1))
        p = m.group(2)
        if p == "pm" and hour < 12:
            hour += 12
        if p == "am" and hour == 12:
            hour = 0
        return f"at {hour}:00"

    text = re.sub(r"\bat\s+(\d{1,2})\s*(am|pm)\b", _am_pm, text)

    # depois at 9 -> at 9:00
    text = re.sub(r"\bat\s+(\d{1,2})\b", r"at \1:00", text)
        
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

    # text = re.sub(r"[^\w\s:]", "", text)
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
