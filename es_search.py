#encoding:utf-8

from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk
from tqdm import tqdm
from math import ceil
import json
from pprint import pprint
from collections import defaultdict
from itertools import chain

from configs.config import config
from preprocessing_topic import topics_to_preprocessed_structure


es = Elasticsearch()


def es_search_by_topic(topic: dict):
    es = Elasticsearch()
    index_name = config.index_name
    type_name = config.type_name
    query_return_size = 4000
    disease = topic["disease"]
    gene_raw = topic["gene"]
    gene_gene = ", ".join([pair["gene"] for pair in topic["gene_variant"]])
    gene_variant = ", ".join(list(chain.from_iterable([pair["variant"] for pair in topic["gene_variant"]])))
    age = topic["age"]
    gender = topic["gender"]

    dsl = {
        # "疾病": {
        #     "query": {
        #         "bool": {
        #             "must": [
        #                 {"bool": {
        #                     "should": [
        #                         {"match": {"title": disease}},
        #                         {"match": {"summary": disease}},
        #                         {"match": {"detailed_description": disease}},
        #                         {"match": {"criteria": disease}},
        #                         {"match": {"condition": disease}},
        #                     ]
        #                 }},
        #             ]
        #         }
        #     },
        #     "size": 3000,
        # },

        # "基因变体的原始字段": {
        #     "query": {
        #         "bool": {
        #             "must": [
        #                 {"bool": {
        #                     "should": [
        #                         {"match": {"title": gene_raw}},
        #                         {"match": {"summary": gene_raw}},
        #                         {"match": {"detailed_description": gene_raw}},
        #                         {"match": {"criteria": gene_raw}}
        #                     ]
        #                 }}
        #             ]
        #         }
        #     },
        #     "size": query_return_size,
        # },

        "基因": {
            "query": {
                "bool": {
                    "must": [
                        {"bool": {
                            "should": [
                                {"match": {"title": gene_gene}},
                                {"match": {"summary": gene_gene}},
                                {"match": {"detailed_description": gene_gene}},
                                {"match": {"criteria": gene_gene}}
                            ]
                        }}
                    ]
                }
            },
            "size": query_return_size,
        },

        "变体": {
            "query": {
                "bool": {
                    "must": [
                        {"bool": {
                            "should": [
                                {"match": {"title": gene_variant}},
                                {"match": {"summary": gene_variant}},
                                {"match": {"detailed_description": gene_variant}},
                                {"match": {"criteria": gene_variant}}
                            ]
                        }}
                    ]
                }
            },
            "size": query_return_size,
        },

        # "疾病+基因变体原始字段(最严格不分词)": {
        #     "query": {
        #         "bool": {
        #             "must": [
        #                 {"bool": {
        #                     "should": [
        #                         {"term": {"title": disease}},
        #                         {"term": {"summary": disease}},
        #                         {"term": {"detailed_description": disease}},
        #                         {"term": {"criteria": disease}},
        #                         {"term": {"condition": disease}},
        #                     ]
        #                 }},
        #                 {"bool": {
        #                     "should": [
        #                         {"match": {"title": gene_raw}},
        #                         {"match": {"summary": gene_raw}},
        #                         {"match": {"detailed_description": gene_raw}},
        #                         {"match": {"criteria": gene_raw}}
        #                     ]
        #                 }}
        #             ]
        #         }
        #     },
        #     "size": query_return_size,
        # },
        # "疾病+基因变体原始字段(严格但可以分词)": {
        #     "query": {
        #         "bool": {
        #             "must": [
        #                 {"bool": {
        #                     "should": [
        #                         {"match_phrase": {"title": {"query": disease, "slop": 10}}},
        #                         {"match_phrase": {"summary": {"query": disease, "slop": 10}}},
        #                         {"match_phrase": {"detailed_description": {"query": disease, "slop": 10}}},
        #                         {"match_phrase": {"criteria": {"query": disease, "slop": 10}}},
        #                         {"match_phrase": {"condition": {"query": disease, "slop": 10}}},
        #                     ]
        #                 }},
        #                 {"bool": {
        #                     "should": [
        #                         {"match": {"title": gene_raw}},
        #                         {"match": {"summary": gene_raw}},
        #                         {"match": {"detailed_description": gene_raw}},
        #                         {"match": {"criteria": gene_raw}}
        #                     ]
        #                 }}
        #             ]
        #         }
        #     },
        #     "size": query_return_size,
        # },
        #
        # "疾病+基因变体原始字段(不严格匹配)": {
        #     "query": {
        #         "bool": {
        #             "must": [
        #                 {"bool": {
        #                     "should": [
        #                         {"match": {"title": disease}},
        #                         {"match": {"summary": disease}},
        #                         {"match": {"detailed_description": disease}},
        #                         {"match": {"criteria": disease}},
        #                         {"match": {"condition": disease}},
        #                     ]
        #                 }},
        #                 {"bool": {
        #                     "should": [
        #                         {"match": {"title": gene_raw}},
        #                         {"match": {"summary": gene_raw}},
        #                         {"match": {"detailed_description": gene_raw}},
        #                         {"match": {"criteria": gene_raw}}
        #                     ]
        #                 }}
        #             ]
        #         }
        #     },
        #     "size": query_return_size,
        # },

        "基因+变体": {
            "query": {
                "bool": {
                    "must": [
                        {"bool": {
                            "should": [
                                {"match": {"title": gene_gene}},
                                {"match": {"summary": gene_gene}},
                                {"match": {"detailed_description": gene_gene}},
                                {"match": {"criteria": gene_gene}}
                            ]
                        }},
                        {"bool": {
                            "should": [
                                {"match": {"title": gene_variant}},
                                {"match": {"summary": gene_variant}},
                                {"match": {"detailed_description": gene_variant}},
                                {"match": {"criteria": gene_variant}}
                            ]
                        }}
                    ]
                }
            },
            "size": query_return_size,
        },

        "疾病+基因": {
            "query": {
                "bool": {
                    "must": [
                        {"bool": {
                            "should": [
                                {"match": {"title": disease}},
                                {"match": {"summary": disease}},
                                {"match": {"detailed_description": disease}},
                                {"match": {"criteria": disease}},
                                {"match": {"condition": disease}},
                            ]
                        }},
                        {"bool": {
                            "should": [
                                {"match": {"title": gene_gene}},
                                {"match": {"summary": gene_gene}},
                                {"match": {"detailed_description": gene_gene}},
                                {"match": {"criteria": gene_gene}}
                            ]
                        }},
                    ]
                }
            },
            "size": query_return_size,
        },

        "疾病+变体": {
            "query": {
                "bool": {
                    "must": [
                        {"bool": {
                            "should": [
                                {"match": {"title": disease}},
                                {"match": {"summary": disease}},
                                {"match": {"detailed_description": disease}},
                                {"match": {"criteria": disease}},
                                {"match": {"condition": disease}},
                            ]
                        }},
                        {"bool": {
                            "should": [
                                {"match": {"title": gene_variant}},
                                {"match": {"summary": gene_variant}},
                                {"match": {"detailed_description": gene_variant}},
                                {"match": {"criteria": gene_variant}}
                            ]
                        }}
                    ]
                }
            },
            "size": query_return_size,
        },

        "疾病+基因+变体": {
            "query": {
                "bool": {
                    "must": [
                        {"bool": {
                            "should": [
                                {"match": {"title": disease}},
                                {"match": {"summary": disease}},
                                {"match": {"detailed_description": disease}},
                                {"match": {"criteria": disease}},
                                {"match": {"condition": disease}},
                            ]
                        }},
                        {"bool": {
                            "should": [
                                {"match": {"title": gene_gene}},
                                {"match": {"summary": gene_gene}},
                                {"match": {"detailed_description": gene_gene}},
                                {"match": {"criteria": gene_gene}}
                            ]
                        }},
                        {"bool": {
                            "should": [
                                {"match": {"title": gene_variant}},
                                {"match": {"summary": gene_variant}},
                                {"match": {"detailed_description": gene_variant}},
                                {"match": {"criteria": gene_variant}}
                            ]
                        }}
                    ]
                }
            },
            "size": query_return_size,
        },

    }

    result_of_each_query = dict()
    for key, query in dsl.items():
        doc_list = []
        es_returns = es.search(index=index_name, doc_type=type_name, body=dsl[key])
        for doc in es_returns["hits"]["hits"]:
            doc_min_age = doc["_source"]["min_age"]
            doc_max_age = doc["_source"]["max_age"]
            doc_gender = doc["_source"]["gender"].lower()
            # 按年龄性别筛选
            if doc_gender == "any" or doc_gender == gender.lower() and \
                    doc_min_age <= age <= doc_max_age:
                # 只保留这三个域
                new_doc = {
                    "ntc_id": doc["_source"]["ntc_id"],
                    "title": doc["_source"]["title"],
                    "summary": doc["_source"]["summary"],
                    "_score": doc["_score"],
                }
                doc_list.append(new_doc)
        result_of_each_query[key] = doc_list
    return result_of_each_query



def es_search(topics:list):
    es = Elasticsearch()
    index_name = config.index_name
    type_name = config.type_name
    query_return_size = 4000
    result_of_each_topic=[]

    for i in range(len(topics)):
        result_under_a_topic = es_search_by_topic(topics[i])
        # print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"""topic {i}""")
        for k in result_under_a_topic.keys():
            print(f"""{k}: {len(result_under_a_topic[k])}""")
        print("")
        result_of_each_topic.append(result_under_a_topic)

    # pprint("返回查询结果：{}".format(results))
    return result_of_each_topic

if __name__=="__main__":
    topics = topics_to_preprocessed_structure(config.topic_path[2018])
    result_of_each_topic = es_search(topics)

    topic_and_result = []
    for t, r in zip(topics, result_of_each_topic):
        topic_and_result.append({"topic": t, "result": r})

