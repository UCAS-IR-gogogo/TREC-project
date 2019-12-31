"""
大作业一键式运行的main函数
"""
from pprint import pprint
from argparse import ArgumentParser

from configs.config import config

from preprocessing_doc import dataset_to_preprocessed_structure
from preprocessing_topic import topics_to_preprocessed_structure, input_topic
from import_into_es import import_examples_into_es
from es_search import es_search
from ranking_and_filter import ranking_and_filter_all_topics
from eval import write2file, trec_eval, trec_eval_shell

def search_and_eval(topics_dict: dict, print_topics: bool=False):
    print(f"topic ids: {tuple(topics_dict.keys())}")
    if print_topics:
        pprint(topics_dict)
    # es查询
    result_of_each_topic: dict = es_search(topics_dict)
    # 对结果进行排序和过滤
    result_of_each_topic: dict = ranking_and_filter_all_topics(result_of_each_topic, use_deep_model=use_deep_model)

    # 评测
    # 生成runs文件
    write2file(result_of_each_topic, config.runs_path[year])
    # python调用trectools计算评测指标
    metrics = trec_eval(config.runs_path[year], config.qrels_path[year])
    pprint(metrics)
    # 通过os.system编译并调用trec_eval中运行评测指标
    metrics_str = trec_eval_shell(config.runs_path[year], config.qrels_path[year], config.metrics_path[year])
    print(metrics_str)

    return metrics


if __name__ == "__main__":
    year = 2018
    use_deep_model = True
    create_index = False

    parser = ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="以demo模式运行，不构建索引，topic需要手动输入。运行demo前需要先用--create_index参数构建索引。如果已经构建了索引，或者已经以非demo的一键式脚本运行过，则不需要再次构建索引")
    parser.add_argument("--run_all", action="store_true", help="自动运行全部topic")
    parser.add_argument("--create_index", action="store_true", help="构建索引")
    parser.add_argument("--print_topics", action="store_true", help="打印所有的topic（太多了所以默认不打印）")
    args = parser.parse_args()

    # doc导入es构建索引
    if create_index or args.create_index:  # todo:非demo模式一键式脚本需要构建索引
        import_examples_into_es(dataset_to_preprocessed_structure(config.doc_txt_dir))

    if args.demo:
        # 导入topic并进行预处理
        topics_dict: dict = input_topic()
        # es查询
        result_of_each_topic: dict = es_search(topics_dict)
        # 对结果进行排序和过滤
        result_of_each_topic: list = ranking_and_filter_all_topics(result_of_each_topic, use_deep_model=use_deep_model)[0]
        for i, doc in enumerate(result_of_each_topic, start=1):
            p = f"""{i}  ntc_id: {doc["ntc_id"]}\n    Title: {doc["title"]}\n"""
            print(p)

    elif args.run_all:
        # 五折交叉
        fold = [
            (40, 5, 27, 8, 29, 13, 34, 36, 20, 15),
            (4, 47, 1, 14, 9, 39, 22, 11, 49, 25),
            (21, 3, 32, 23, 19, 10, 12, 38, 26, 16),
            (2, 17, 7, 50, 45, 48, 31, 18, 42, 41),
            (6, 33, 37, 28, 30, 43, 44, 46, 35, 2),
        ]

        # 导入topic并进行预处理
        topics_dict: dict = topics_to_preprocessed_structure(config.topic_path[year])

        # 五折的sub—topic
        for sub_topic_ids in fold:
            sub_topics_dict = {tid: topics_dict[tid] for tid in sub_topic_ids}
            metrics = search_and_eval(sub_topics_dict, print_topics=args.print_topics)

        # 全量topic
        metrics = search_and_eval(topics_dict, print_topics=args.print_topics)
    else:
        print("请用--demo 运行demo，或--run_all一键运行全部topic")



