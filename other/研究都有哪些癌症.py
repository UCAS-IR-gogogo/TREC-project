import json
import jieba
import re

from configs.config import config

with open(config.disease_translate_dict_path) as f:
    trans:dict = json.load(f)
disease = list(trans.values())

def is_cancer(disease:str):
    return "癌" in disease or "瘤" in disease or "白血病" in disease

cancer = [d for d in disease if is_cancer(d)]

# 分词
organs = [c for c in  cancer]

# 以特定词分词
def split_organ_by_str(organs:list, s:str):
    new_organs = []
    for o in organs:
        new_organs += o.split(s)
    new_organs = [o.strip() for o in new_organs]
    return new_organs

organs = split_organ_by_str(organs, "癌症")
organs = split_organ_by_str(organs, "癌")
organs = split_organ_by_str(organs, "肿瘤")
organs = split_organ_by_str(organs, "瘤")
organs = split_organ_by_str(organs, "白血病")

# 分词
new_organs = []
for o in organs:
    new_organs += list(jieba.cut(o))
organs = [o.strip() for o in new_organs]

# 去掉英文
re_chinese = re.compile(u'[\u4e00-\u9fa5]')
organs = [o for o in organs if re_chinese.search(o)]

# 去包含特定字符串的词
def drop_word_with_str(organs: list, s: str):
    return [o for o in organs if s not in o]

organs = drop_word_with_str(organs, "人")
organs = drop_word_with_str(organs, "细胞")
organs = drop_word_with_str(organs, "症")
organs = drop_word_with_str(organs, "病")
organs = drop_word_with_str(organs, "性")
organs = drop_word_with_str(organs, "期")
organs = drop_word_with_str(organs, "级")
organs = drop_word_with_str(organs, "者")
organs = drop_word_with_str(organs, "不")
organs = drop_word_with_str(organs, "类")
organs = drop_word_with_str(organs, "术")
organs = drop_word_with_str(organs, "治疗")
organs = drop_word_with_str(organs, "氏")
organs = drop_word_with_str(organs, "第")
organs = drop_word_with_str(organs, "年")
organs = drop_word_with_str(organs, "炎")


organs = set(organs)

single_organs = set("".join(organs)) # 所有单字

