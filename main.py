"""
大作业一键式运行的main函数
"""
from configs.config import config

from preprocessing_doc import dataset_to_preprocessed_structure
from preprocessing_topic import topics_to_preprocessed_structure
from import_into_es import import_examples_into_es
from es_search import es_search
from filter_disease_gene_variant import filter_disease_gene_variant


if __name__ == "__main__":
    # topics
    topics = {2017: topics_to_preprocessed_structure(config.topic_path[2017]),
              2018: topics_to_preprocessed_structure(config.topic_path[2018])}
    # doc导入es构建索引
    import_examples_into_es(dataset_to_preprocessed_structure(config.doc_txt_dir))
    # es查询
    result_of_each_topic = es_search(topics[2018])
    filtered_result_of_each_topic = filter_disease_gene_variant(result_of_each_topic)