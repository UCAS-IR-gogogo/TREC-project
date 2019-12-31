"""
借助不同粒度的查询结果，通过疾病，基因，变体，性别，年龄，过滤es查询结果
"""
from collections import OrderedDict
from pprint import pprint
from tqdm import tqdm

from configs.config import config
from preprocessing_topic import topics_to_preprocessed_structure
from es_search import es_search
from eval import write2file, trec_eval, trec_eval_shell
from deep_model.infer_example import opt, Inferer

inf = Inferer(opt)

# 对一个topic的doc进行打分和ranking，基于四个粒度的query进行打分
def ranking_and_filter_disease_gene_variant_by_topic(result_of_topic: dict):
    # 疾病 + 基因 + 变体
    # 疾病 + 基因(如果疾病 + 基因是0则返回疾病 + 变体)
    # 基因 + 变体
    # 如果结果少于15个则再加上这个条件：基因(如果基因是0则返回变体)

    # 必须要用的粒度
    keys_order_must = [
        "疾病+基因+变体",
        "疾病+基因" if len(result_of_topic["疾病+基因"]) > 0 else "疾病+变体",
    ]

    # 少于15个结果时再加上的粒度
    keys_order_less_than_15 = [
        "基因+变体",
        "基因" if len(result_of_topic["基因"]) > 0 else "变体",
    ]

    # 把doc添加到doc_list里
    def append_doc(doc, new_docs_dict):
        if doc["ntc_id"] not in new_docs_dict.keys():
            new_docs_dict[doc["ntc_id"]] = dict(**doc)
        else:
            new_docs_dict[doc["ntc_id"]]["_score"] += doc["_score"]

    # 必须要用的粒度
    new_docs_dict = dict()
    for query_condition in keys_order_must:
        for doc in result_of_topic[query_condition]:
            append_doc(doc, new_docs_dict)

    # 如果小于15个结果再加上的粒度
    for query_condition in keys_order_less_than_15:
        if len(new_docs_dict) <= 15:
            for doc in result_of_topic[query_condition]:
                append_doc(doc, new_docs_dict)

    new_docs_dict = sorted(new_docs_dict.values(), key=lambda x:x["_score"], reverse=True)
    return new_docs_dict


# 用深度模型过滤掉非PM文档
def filter_deep_model(doc_list_under_topic: list):
    new_docs = []
    for doc in doc_list_under_topic:
        category = inf.evaluate(doc['summary']).squeeze(1)
        if category == 1:
            new_docs.append(doc)
    return new_docs


# 对每个topic下的doc都进行整合，进行ranking和过滤
def ranking_and_filter_all_topics(result_of_each_topic: dict, use_deep_model:bool=True):
    new_result_of_each_topic = dict()
    for i,r in tqdm(result_of_each_topic.items(), desc="Filter and Ranking:"):
        # 按不同粒度的查询的分数相加进行ranking
        doc_list = ranking_and_filter_disease_gene_variant_by_topic(r)
        # 用深度模型过滤是否是pm
        if use_deep_model:
            doc_list = filter_deep_model(doc_list)
        new_result_of_each_topic[i] = doc_list
        # print(f"""topic {i}: {len(doc_list)} docs""")
    return new_result_of_each_topic


if __name__=="__main__":
    year = 2018
    use_deep_model=False
    topics_dict: dict = topics_to_preprocessed_structure(config.topic_path[year])
    result_of_each_topic:dict = es_search(topics_dict)
    result_of_each_topic: dict = ranking_and_filter_all_topics(result_of_each_topic, use_deep_model=use_deep_model)

    # 评测
    write2file(result_of_each_topic, config.runs_path[year])
    metrics = trec_eval(config.runs_path[year], config.qrels_path[year])
    pprint(metrics)
    metrics_str = trec_eval_shell(config.runs_path[year], config.qrels_path[year], config.metrics_path[year])
    print(metrics_str)



