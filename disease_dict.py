from pathlib import Path
import json

cwd = Path(".")

with open(cwd/ "data/disease.txt") as fe, open(cwd / "data/疾病.txt") as fc:
    disease_en = [line.strip() for line in fe.readlines()]
    disease_ch = [line.strip() for line in fc.readlines()]

disease_translate_dict = {en: ch for en, ch in zip(disease_en, disease_ch)}
# disease_translate_dict[None] = ""
dict_path = cwd / "data/disease_translate_dict.json"

with open(dict_path, "w") as f:
    json.dump(disease_translate_dict, f)

with open(dict_path) as f:
    d = json.load(f)