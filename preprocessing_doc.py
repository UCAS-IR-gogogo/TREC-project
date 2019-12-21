#encoding:utf-8
"""
预处理document，把每个txt文档转换成字典，最后都放在一个list里
"""
#%%
from pathlib import Path
import xml.etree.ElementTree as ET
import re
from tqdm import tqdm
import pandas as pd
from pandas import DataFrame

from configs.config import config
#%%

#%% 用正则表达式把txt文件里的对应的域提取出来
def txt_to_structure(txt_path: Path):
    with open(str(txt_path), "r") as f:
        txt = f.read()
    r_ntc_id = re.compile("(NCT.*)\.txt")
    ntc_id = r_ntc_id.findall(txt_path.name)[0]
    r_title = re.compile("TITLE:\n([\d\D]*)\n{1,}CONDITION")
    title = r_title.findall(txt)[0].strip()
    r_condition = re.compile("CONDITION:\n([\d\D]*)\n{1,}INTERVENTION:")
    condition = r_condition.findall(txt)[0].replace('\n','').replace('\r','')
    r_intervention = re.compile("INTERVENTION:\n([\d\D]*)\n{1,}SUMMARY:")
    intervention = r_intervention.findall(txt)[0].replace('\n','').replace('\r','')
    r_summary = re.compile("SUMMARY:\n([\d\D]*)\n{1,}DETAILED DESCRIPTION:")
    summary = r_summary.findall(txt)[0].replace('\n','').replace('\r','').strip()
    summary=re.sub(r'\s{2,}',' ',summary)
    r_detailed_description = re.compile("DETAILED DESCRIPTION:\n([\d\D]*)\n{1,}ELIGIBILITY:")
    detailed_description = r_detailed_description.findall(txt)[0].replace('\n','').replace('\r','').strip()
    detailed_description=re.sub(r'\s{2,}',' ',detailed_description)
    r_gender = re.compile("ELIGIBILITY:(?:[\d\D]*)\nGender: (.*)\n")
    gender = r_gender.findall(txt)[0].strip()
    # r_age = re.compile("\nAge: (.*)\n")
    r_age = re.compile("ELIGIBILITY:(?:[\d\D]*)\nAge:(.*)\n")
    age = r_age.findall(txt)[0].strip()
    r_criteria = re.compile("ELIGIBILITY:(?:[\d\D]*)\nCriteria:\n([\d\D]*)\n{1,}")
    criteria = r_criteria.findall(txt)[0].replace('\n','').replace('\r','').strip()
    criteria=re.sub(r'\s{2,}',' ',criteria)

    # 每个txt文件提取后对应一个example
    example = {
        "ntc_id": ntc_id,
        "title": title,
        "condition": condition,
        "intervention": intervention,
        "summary": summary,
        "detailed_description": detailed_description,
        "gender": gender,
        "min_age": age,
        "max_age":age,         #age扩展成min_age和max_age两个字段
        "criteria": criteria,
    }
    return example

# 对提取好的example进行进一步处理
# 1.提取各个域里的疑似是基因的东西（以大写字母开头，至少有两个符号组成，可以说大写字母、数字、横线-，但不能是以冒号结尾的纯大写字母例如"DESCRIPTION:"）
# 2.去掉每行前面多余的空格，后面多余的\n。最好让一个自然段还要变成一个自然段，但不强求(#做了，criteria可能还有点问题)
# 3.提取detailed_description里面的子域（这个待定，因为每个里面子域可能不一样）
# 4.年龄的处理：把年龄字段提取出min age和max age。目前还发现年龄字段有的是Any或者All，看看还有没有其他类似的，这种先统一处理成Any，之后视情况有可能处理成min=0，max=200
# 5.性别，统一处理成male，female，any
# 6.把'None'处理成None
def preprocessing_None(example: dict):
    # 把'NONE'换成None
    for k in example.keys():
        if example[k]=='NONE':
            example[k]=None
    return example

#年龄预处理：把年龄字段提取出min age和max age
def preprocessing_age(example:dict):
    if example['min_age']=='N/A to N/A':
        example['min_age']=0   
        example['max_age']=200   #Any处理成0-200
    else:
        r_min_age=re.compile("(.*)to")
        min_age = r_min_age.findall(example['min_age'])[0].strip()
        if min_age in ('N/A', 'ANY'):
            example['min_age']=0
        else:
            r_min_age=re.compile("(\d+).*to")
            min_age = r_min_age.findall(example['min_age'])[0].strip()
            example['min_age']=min_age
        r_max_age=re.compile("to(.*)")
        max_age = r_max_age.findall(example['max_age'])[0].strip()
        if max_age in ('N/A', 'ANY'):
            example['max_age']=200
        else:
            r_max_age=re.compile("(\d+).*")
            max_age = r_max_age.findall(max_age)[0]
            example['max_age']=max_age
    return example

#性别预处理，统一处理成Male，Female，Any
def preprocessing_gender(example:dict):
    if example['gender']=='All':
        example['gender']='Any'
    return example


def dataset_to_preprocessed_structure(txt_dirs):
    examples = []
    # 遍历两层文件夹
    for first_dir in tqdm(list((txt_dirs).iterdir()), desc="First dir"):
        if not first_dir.is_dir():
            continue
        for second_dir in list(first_dir.iterdir()):
            if not second_dir.is_dir():
                continue
            for file in second_dir.iterdir():
                try:
                    example = txt_to_structure(file)
                    example = preprocessing_age(example)
                    example = preprocessing_gender(example)
                    example = preprocessing_None(example)
                    examples.append(example)
                except:
                    print(file)
                    raise
    return examples

#%%
if __name__=="__main__":
#%%
    txt_dirs = config.doc_txt_dir
    examples = dataset_to_preprocessed_structure(txt_dirs)

#%% pandas更好处理
    df = DataFrame(examples)
#%% 提取所有的疾病
    disease = set(df["condition"])
    with open("disease.txt", "w") as f:
        f.write("\n".join(list(disease- {None})))
#%%
    # 提取基因。目前的问题是类似 'DISCRIPTION:'这样以冒号的全大写子标题也会被提出来
    # r_gene = re.compile(r"([A-Z]+[-A-Z0-9]+)")
    # gene_summary = df["summary"].apply(func=lambda s: list(set(r_gene.findall(s))))
    # gene_criteria = df["criteria"].apply(func=lambda s: list(set(r_gene.findall(s))))
