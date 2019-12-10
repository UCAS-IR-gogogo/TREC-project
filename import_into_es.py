#!/usr/bin/env python
#%%
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk
from tqdm import tqdm
from math import ceil
import json
from pprint import pprint

from configs.config import config


# %%
def import_examples_into_es(examples: list):
    index_name = config.index_name
    type_name = config.type_name
    buck_size = config.buck_size

    es = Elasticsearch(config.es_url)
    es_index = IndicesClient(es)
    if es_index.exists(index=index_name):
        es_index.delete(index=index_name)
    # 创建索引
    with open(config.es_index_json) as f:
        mappings = json.load(f)

    res = es.indices.create(index=index_name, body=mappings)

    # 数据批量导入es
    for i in range(len(examples)):
        examples[i] = {
            "_index": index_name,
            "_type": type_name,
            "_id": examples[i]["ntc_id"],
            "_source": examples[i]
        }

    for i in tqdm(range(ceil(len(examples) / buck_size))):
        bulk(es, actions=examples[i * buck_size: min((i + 1) * buck_size, len(examples))])

#%%
if __name__ == "__main__":
    from preprocessing_doc import dataset_to_preprocessed_structure

    examples = dataset_to_preprocessed_structure(config.doc_txt_dir)
    #%%
    import_examples_into_es(examples)

    # 查询一条数据
    #%%
    es = Elasticsearch(config.es_url)
    res_one = es.get(index=config.index_name, doc_type=config.type_name, id="NCT02445157")
    pprint(res_one)
