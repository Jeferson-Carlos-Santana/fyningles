import json
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "services" / "dictionary"
BASE_DIR.mkdir(parents=True, exist_ok=True) 
MAX_ITEMS = 2000

def list_terms(lang):
    terms = []
    # files = BASE_DIR.glob(f"{lang}_*.json")
    files = sorted(BASE_DIR.glob(f"{lang}_*.json"))

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            terms.extend(data.get(lang, []))

    return terms

def term_exists(lang, term):
    # files = BASE_DIR.glob(f"{lang}_*.json")
    files = sorted(BASE_DIR.glob(f"{lang}_*.json"))

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if term in data.get(lang, []):
                return True
    return False

def add_term(lang, term):
    # 1) lista arquivos do idioma
    files = sorted(BASE_DIR.glob(f"{lang}_*.json"))

    # 2) se não existir nenhum, cria o primeiro
    if not files:
        file_path = BASE_DIR / f"{lang}_0001.json"
        data = {lang: []}
    else:
        file_path = files[-1]
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    # 3) se o arquivo atual estiver cheio, cria o próximo
    if len(data.get(lang, [])) >= MAX_ITEMS:
        last_num = int(file_path.stem.split("_")[1])
        next_num = last_num + 1
        file_path = BASE_DIR / f"{lang}_{next_num:04d}.json"
        data = {lang: []}

    # 4) adiciona o termo
    data[lang].append(term)

    # 5) salva
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def delete_term(lang, term):
    # files = BASE_DIR.glob(f"{lang}_*.json")
    files = sorted(BASE_DIR.glob(f"{lang}_*.json"))

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if term in data.get(lang, []):
            data[lang].remove(term)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True

    return False


