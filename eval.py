from trectools import TrecQrel, procedures, TrecRun, TrecEval
from pathlib import Path
import os

from configs.config import config

# 将查询结果写入为trec runs文件
def write2file(data: dict, runs_file_path: Path or str):
    f = open(runs_file_path, 'w', encoding='utf-8')
    for tid in data.keys():
        topic = data[tid]
        for j, dict in enumerate(topic):
            topic_id = str(tid)
            doc_id = dict['ntc_id']
            score = round(dict['_score'], 4)
            res = " ".join([topic_id, 'Q0', doc_id, str(j), str(score), 'my_run'])
            f.writelines([res + '\n'])
    f.close()

# python的trectools运行评测指标
def trec_eval(runs_file_path: Path or str, qrels_file_path: Path or str):
    metrics = dict()
    r1 = TrecRun(str(runs_file_path.absolute()))
    qrels = TrecQrel(str(qrels_file_path.absolute()))
    results = TrecEval(r1, qrels)
    metrics["P@5"] = results.get_precision(5)
    metrics["P@10"] = results.get_precision(10)
    metrics["P@15"] = results.get_precision(15)
    metrics["bpref"] = results.get_bpref()
    metrics["map"] = results.get_map()

    metrics = {k: round(v, 4) for k,v in metrics.items()}
    return metrics

# 编译并运行c语言版trec_eval，读取重定向的评测结果返回
def trec_eval_shell(runs_file_path: Path or str, qrels_file_path: Path or str, eval_file_path: Path or str):
    # 编译trec_eval文件
    command_compile_trec = f"""cd {config.trec_eval_source.absolute()} && make clean && make && mv {(config.trec_eval_source / "trec_eval").absolute()} {config.trec_eval_bin}"""
    os.system(command_compile_trec)
    # 运行测评
    command_eval = f"""{config.trec_eval_bin.absolute()} {qrels_file_path.absolute()} {runs_file_path.absolute()} > {eval_file_path.absolute()}"""
    os.system(command_eval)
    # 读取测评结果返回
    try:
        with open(eval_file_path) as f:
            eval_result_str = f.read()
        return eval_result_str
    except:
        return ""

if __name__ == '__main__':
    trec_eval("./qresults/results.txt")