from trectools import TrecQrel, procedures, TrecRun, TrecEval

from deep_model.infer_example import Inferer, opt

inf = Inferer(opt)


def write2file(data):
    f = open('result.txt', 'w', encoding='utf-8')
    for i in range(50):
        topic = data[i]
        for j, dict in enumerate(topic):
            topic_id = str(i)
            doc_id = dict['ntc_id']
            sorce = dict['_score']
            res = " ".join([topic_id, 'Q0', doc_id, str(j), sorce, 'my_run'])
            f.writelines([res + '\n'])
    f.close()

def trec_eval(file):
    r1 = TrecRun(file)
    qrels = TrecQrel("./dataset/.txt")
    results = TrecEval(r1, qrels)
    p5 = results.get_precision(5)
    p10 = results.get_precision(10)
    p15 = results.get_precision(15)
    print(p5)
    print(p10)
    print(p15)


if __name__ == '__main__':
    pass
    # trec_eval("./qresults/results.txt")