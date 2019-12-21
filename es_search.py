#encoding:utf-8

from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk
from tqdm import tqdm
from math import ceil
import json
from pprint import pprint
from collections import defaultdict

from configs.config import config
from preprocessing_topic import topics_to_preprocessed_structure


def es_search(topics:list):
    es = Elasticsearch()
    index_name = config.index_name
    type_name = config.type_name
    results=[]
    for i in range(len(topics)):
        dsl = {
            "基因和疾病(最严格不分词)": {
                "query": {
                        "bool": {
                            "must": [
                                {"bool": {
                                    "should": [
                                        {"term": {"title": topics[i]["disease"]}},
                                        {"term": {"summary": topics[i]["disease"]}},
                                        {"term": {"detailed_description": topics[i]["disease"]}},
                                        {"term": {"criteria": topics[i]["disease"]}},
                                        {"term": {"condition": topics[i]["disease"]}},
                                    ]
                                }},
                                {"bool": {
                                    "should": [
                                        {"match": {"title": topics[i]["gene"]}},
                                        {"match": {"summary": topics[i]["gene"]}},
                                        {"match": {"detailed_description": topics[i]["gene"]}},
                                        {"match": {"criteria": topics[i]["gene"]}}
                                    ]
                                }}
                            ]
                        }
                    }
                },
            "基因和疾病(严格但可以分词)": {
                "query": {
                        "bool": {
                            "must": [
                                {"bool": {
                                    "should": [
                                        {"match_phrase": {"title": {"query": topics[i]["disease"], "slop": 10}}},
                                        {"match_phrase": {"summary": {"query": topics[i]["disease"], "slop": 10}}},
                                        {"match_phrase": {"detailed_description": {"query": topics[i]["disease"], "slop": 10}}},
                                        {"match_phrase": {"criteria": {"query": topics[i]["disease"], "slop": 10}}},
                                        {"match_phrase": {"condition": {"query": topics[i]["disease"], "slop": 10}}},
                                    ]
                                }},
                                {"bool": {
                                    "should": [
                                        {"match": {"title": topics[i]["gene"]}},
                                        {"match": {"summary": topics[i]["gene"]}},
                                        {"match": {"detailed_description": topics[i]["gene"]}},
                                        {"match": {"criteria": topics[i]["gene"]}}
                                    ]
                                }}
                            ]
                        }
                    }
                },

            "基因和疾病(不严格匹配)": {
                    "query": {
                        "bool": {
                            "must": [
                                {"bool": {
                                    "should": [
                                        {"match": {"title": topics[i]["disease"]}},
                                        {"match": {"summary": topics[i]["disease"]}},
                                        {"match": {"detailed_description": topics[i]["disease"]}},
                                        {"match": {"criteria": topics[i]["disease"]}},
                                        {"match": {"condition": topics[i]["disease"]}},
                                    ]
                                }},
                                {"bool": {
                                    "should": [
                                        {"match": {"title": topics[i]["gene"]}},
                                        {"match": {"summary": topics[i]["gene"]}},
                                        {"match": {"detailed_description": topics[i]["gene"]}},
                                        {"match": {"criteria": topics[i]["gene"]}}
                                    ]
                                }}
                            ]
                        }
                    }
                },

            "只匹配基因": {
                    "query": {
                        "bool": {
                            "must": [
                                {"bool": {
                                    "should": [
                                        {"match": {"title": topics[i]["gene"]}},
                                        {"match": {"summary": topics[i]["gene"]}},
                                        {"match": {"detailed_description": topics[i]["gene"]}},
                                        {"match": {"criteria": topics[i]["gene"]}}
                                    ]
                                }}
                            ]
                        }
                    }
                }
        }

        result = dict()
        for key, query in dsl.items():
            result[key] = es.search(index=index_name, doc_type=type_name, body=dsl[key])["hits"]
        print(json.dumps(result, indent=2, ensure_ascii=False))
        results.append(result)

    # pprint("返回查询结果：{}".format(results))
    return results

if __name__=="__main__":
    topics = topics_to_preprocessed_structure(config.topic_path[2018])
    results = es_search(topics)

    topic_and_result = []
    for t, r in zip(topics, results):
        topic_and_result.append({"topic": t, "result": r})

