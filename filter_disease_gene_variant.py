"""
借助不同粒度的查询结果，通过疾病，基因，变体，性别，年龄，过滤es查询结果
"""
from collections import OrderedDict
from pprint import pprint

from configs.config import config
from preprocessing_topic import topics_to_preprocessed_structure
from es_search import es_search
from eval import write2file, trec_eval, trec_eval_shell
from deep_model.infer_example import classify


# 对一个topic的doc进行整合
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

    new_docs_dict = dict()
    for query_condition in keys_order:
        for doc in result_of_topic[query_condition]:
            append_doc(doc, new_docs_dict)

    # 如果结果太少则把基因或变体字段也加上
    if len(new_docs_dict) <= 15:
        query_condition = "基因" if len(result_of_topic["基因"])>0 else "变体"
        for doc in result_of_topic[query_condition]:
            append_doc(doc, new_docs_dict)

    new_docs_dict = sorted(new_docs_dict.values(), key=lambda x:x["_score"], reverse=True)
    return new_docs_dict


# 用深度模型过滤掉非PM文档
def filter_deep_model(doc_list_under_topic: list):
    new_docs = []
    for doc in doc_list_under_topic:
        # category = inf.evaluate(doc['summary']).squeeze(1)
        category = classify(doc['summary'])
        if category == 1:
            new_docs.append(doc)
    return new_docs


# 对每个topic的doc都进行整合
def filter_disease_gene_variant(result_of_each_topic: list, use_deep_model:bool=True):
    new_result_of_each_topic = []
    for i,r in enumerate(result_of_each_topic):
        doc_list = filter_disease_gene_variant_by_topic(r)
        if use_deep_model:
            doc_list = filter_deep_model(doc_list)
        new_result_of_each_topic.append(doc_list)
        # print(f"""topic {i}: {len(doc_list)} docs""")
    return new_result_of_each_topic


if __name__=="__main__":
    year = 2018
    use_deep_model=False
    topics_dict: dict = topics_to_preprocessed_structure(config.topic_path[year])
    result_of_each_topic:list = es_search(list(topics_dict.values()))
    result_of_each_topic: list = filter_disease_gene_variant(result_of_each_topic, use_deep_model=use_deep_model)
    fold = [
        [40, 5, 27, 8, 29, 13, 34, 36, 20, 15],
        [4, 47, 1, 14, 9, 39, 22, 11, 49, 25],
        [21, 3, 32, 23, 19, 10, 12, 38, 26, 16],
        [2, 17, 7, 50, 45, 48, 31, 18, 42, 41],
        [6, 33, 37, 28, 30, 43, 44, 46, 35, 24]
    ]

    # 评测
    write2file(result_of_each_topic, config.runs_path[year])
    metrics = trec_eval(config.runs_path[year], config.qrels_path[year])
    pprint(metrics)
    metrics_str = trec_eval_shell(config.runs_path[year], config.qrels_path[year], config.metrics_path[year])
    print(metrics_str)



