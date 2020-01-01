# TREC
TREC精准医疗任务，癌症医学记录查询

## 结果文件位置：
用于trec_eval测试的结果文件：output/runs-2018.txt
trec_eval的运行结果：output/eval-2018.txt

## 运行方法：

**请先将TREC 2018的全部文档clinicaltrials_txt.tar.gz解压到data目录下 ！！！！**  

1.一键构建环境：  
./bash_build_environment.sh  

2.不重新训练的情况下运行全部topic  
./bash_run_all_without_retrain.sh  

3.运行demo（需要先运行上面的脚本构建索引）  
./bash_run_demo.sh  

4.重新训练并运行全部topic（训练的过程很慢！！！！！）  
./bash_run_all.sh  

