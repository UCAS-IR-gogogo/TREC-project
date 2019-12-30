"""
输入topic返回查询结果的demo
"""

"""
demo
"""

from configs.config import config

from preprocessing_doc import dataset_to_preprocessed_structure
from preprocessing_topic import topics_to_preprocessed_structure, input_topic
from import_into_es import import_examples_into_es
from es_search import es_search
from filter_disease_gene_variant import filter_disease_gene_variant


if __name__ == "__main__":
    # topics
    topic = input_topic()
    # es查询
    result_of_each_topic = es_search(topic)
    filtered_result_of_each_topic = filter_disease_gene_variant(result_of_each_topic)

    for i, doc in enumerate(filtered_result_of_each_topic[0].values(), start=1):
        p = f"""{i}  ntc_id: {doc["ntc_id"]}\n    Title: {doc["title"]}\n"""
        print(p)