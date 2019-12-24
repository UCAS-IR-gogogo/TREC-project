"""
一些全局的config
"""
#%%
from pathlib import Path

base = Path(".")
class ConfigClass(object):
    index_name = "trials"  # index名字
    type_name = "document"
    buck_size = 10000  # 导入es的批大小
    es_url = "localhost:9200"
    es_index_json = base / "configs/es_index_english.json"
    es_search_json = base / "configs/es_search.json"
    doc_txt_dir = base / "data/clinicaltrials_txt"
    doc_xml_dir = base / "data/clinicaltrials_xml"
    topic_path = {2017: base / "data/topics2017.xml",
                  2018: base / "data/topics2018.xml"}
    disease_translate_dict_path = base / "data/disease_translate_dict.json"

config = ConfigClass()
