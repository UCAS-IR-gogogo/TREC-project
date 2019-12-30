"""
一些全局的config
"""
#%%
from pathlib import Path

base = Path(__file__).parent.parent
class ConfigClass(object):
    index_name = "trials"  # index名字
    type_name = "document"
    buck_size = 10000  # 导入es的批大小
    es_url = "localhost:9200"
    es_index_json: Path = base / "configs/es_index.json"
    es_search_json: Path = base / "configs/es_search.json"
    doc_txt_dir: Path = base / "data/clinicaltrials_txt"
    doc_xml_dir: Path = base / "data/clinicaltrials_xml"
    topic_path = {2017: base / "data/topics2017.xml",
                  2018: base / "data/topics2018.xml"}
    disease_translate_dict_path: Path = base / "data/disease_translate_dict.json"
    qrels_path = {2017: base / "data/qrels-2017.txt",
                  2018: base / "data/qrels-2018-v2.txt"}
    runs_path = {2017: base / "output/runs-2017.txt",
                 2018: base / "output/runs-2018.txt"}
    metrics_path = {2017: base / "output/eval-2017.txt",
                    2018: base / "output/eval-2018.txt",}
    trec_eval_source: Path = base / "trec_eval-9.0.7"
    trec_eval_bin: Path = base / "trec_eval"

config = ConfigClass()
