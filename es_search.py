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



def es_search(topics:list):
    es = Elasticsearch()
    index_name = config.index_name
    type_name = config.type_name
    results=[]

    for i in range(len(topics)):
        disease = topics[i]["disease"]
        gene_gene = ", ".join([pair["gene"] for pair in topics[i]["gene_variant"]])
        gene_variant = ", ".join(list(chain.from_iterable([pair["variant"] for pair in topics[i]["gene_variant"]])))
        dsl = {
            "疾病": {
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
                        ]
                    }
                }
            },

            "基因变体的原始字段": {
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
            },

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
                }
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
                }
            },

            "疾病+基因变体原始字段(最严格不分词)": {
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
            "疾病+基因变体原始字段(严格但可以分词)": {
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

            "疾病+基因变体原始字段(不严格匹配)": {
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
                    }
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
                }
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
                }
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
                }
            },

        }


        result = dict()
        for key, query in dsl.items():
            result[key] = es.search(index=index_name, doc_type=type_name, body=dsl[key])["hits"]
        # print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"""topic {i}""")
        for k in result.keys():
            print(f"""{k}: {result[k]["total"]}""")
        print("")
        results.append(result)

    # pprint("返回查询结果：{}".format(results))
    return results

if __name__=="__main__":
    topics = topics_to_preprocessed_structure(config.topic_path[2018])
    results = es_search(topics)

    topic_and_result = []
    for t, r in zip(topics, results):
        topic_and_result.append({"topic": t, "result": r})

