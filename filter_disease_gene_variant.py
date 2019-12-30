"""
借助不同粒度的查询结果，通过疾病，基因，变体，性别，年龄，过滤es查询结果
"""
from collections import OrderedDict

from configs.config import config
from preprocessing_topic import topics_to_preprocessed_structure
from es_search import es_search

def filter_disease_gene_variant_by_topic(result_of_topic: dict):
    # 疾病 + 基因 + 变体
    # 疾病 + 基因(如果疾病 + 基因是0则返回疾病 + 变体)
    # 基因 + 变体
    # 如果结果少于15个则再加上这个条件：基因(如果基因是0则返回变体)
    keys_order = [
        "疾病+基因+变体",
        "疾病+基因" if len(result_of_topic["疾病+基因"])>0 else "疾病+变体",
        "基因+变体",
        # "基因" if len(result_of_topic["基因"])>0 else "变体"
    ]

    # 把doc添加到doc_list里
    def append_doc(doc, new_docs_dict):
        if doc["ntc_id"] not in new_docs_dict.keys():
            new_docs_dict[doc["ntc_id"]] = dict(**doc)
        else:
            new_docs_dict[doc["ntc_id"]]["_score"] += doc["_score"]

    new_docs_dict = OrderedDict()
    for query_condition in keys_order:
        for doc in result_of_topic[query_condition]:
            append_doc(doc, new_docs_dict)

    # 如果结果太少则把基因或变体字段也加上
    if len(new_docs_dict) <= 15:
        query_condition = "基因" if len(result_of_topic["基因"])>0 else "变体"
        for doc in result_of_topic[query_condition]:
            append_doc(doc, new_docs_dict)

    return new_docs_dict

def filter_disease_gene_variant(result_of_each_topic: list):
    new_result_of_each_topic = []
    for i,r in enumerate(result_of_each_topic):
        doc_list = filter_disease_gene_variant_by_topic(r)
        new_result_of_each_topic.append(doc_list)
        print(f"""topic {i}: {len(doc_list)} docs""")
    return new_result_of_each_topic


if __name__=="__main__":
    topics = topics_to_preprocessed_structure(config.topic_path[2018])
    result_of_each_topic = es_search(topics)
    result_of_each_topic = filter_disease_gene_variant(result_of_each_topic)
