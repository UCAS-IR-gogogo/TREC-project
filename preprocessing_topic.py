#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理topic，把topic文件里各个topic以及对应的gene等域提取出来

Created on Mon Nov 25 14:44:49 2019

@author: wangyuanzheng
"""

# %%
from pathlib import Path
import xml.etree.ElementTree as ET
import re
import json

from configs.config import config

with open(config.disease_translate_dict_path) as f:
    translate_dict = json.load(f)

#%%
# 把xml文件提取成list of topic
def topics_to_preprocessed_structure(xml_path: str):
    xml = ET.parse(xml_path)
    root = xml.getroot()
    # topics = []
    topics_dict = dict()
    for xml_topic in root.findall("topic"):
        topic_id = int(xml_topic.attrib['number'])
        disease = xml_topic.find("disease").text
        gene = xml_topic.find("gene").text
        demographic = xml_topic.find("demographic").text
        r_age = re.compile(r"(.*)-year-old")
        age = int(r_age.findall(demographic)[0])
        r_gender = re.compile(r"-year-old (.*)")
        gender = r_gender.findall(demographic)[0]

        gene_and_variant = gene.split(",")
        gene_and_variant_list = []
        for gv in gene_and_variant:
            # 括号里的变体
            gene_variant = []
            re_K括号里的variant = re.compile(r"\((.*)\)")
            K括号里的variant = re_K括号里的variant.findall(gv)
            gene_variant += K括号里的variant
            # 类似于基因的东西（大写字母+数字+横线，可能后面还有些小写字母）
            re_L类似于gene的东西 = re.compile(r"([A-Z][A-Z0-9\-_]+[A-Z0-9a-z]*)")
            L类似于gene的东西 = re_L类似于gene的东西.findall(gv)
            gene_gene = [g for g in L类似于gene的东西 if g not in K括号里的variant]
            # 去掉基因，以及括号里的变体，剩下的东西也作为变体
            S剩余variant = gv
            for g in L类似于gene的东西:
                S剩余variant = S剩余variant.replace(g, "")
            S剩余variant = S剩余variant.replace("(", "").replace(")", "").strip()
            if S剩余variant:
                gene_variant.append(S剩余variant)
            dc = {
                "gene": gene_gene[0] if len(gene_gene)>0 else "",
                "variant": gene_variant,
            }
            gene_and_variant_list.append(dc)


        new_topic = {
            "topic_id": topic_id,
            "disease": disease,
            "gene": gene,
            "age": age,
            "gender": gender,

            "gene_variant": gene_and_variant_list,
        }
        # topics.append(new_topic)
        topics_dict[topic_id] = new_topic
    # return topics
    return topics_dict


def input_topic():
    # 疾病
    disease = None
    while not isinstance(disease, str) or not disease:
        disease = input("请输入要查询的疾病：")
    # 性别
    gender = ""
    while not gender in (("male", "female", "any")):
        gender = input("请输入患者性别(male/female/any)：")
    # 年龄
    age = -1
    while not (isinstance(age, int) and age>=0):
        age = input("请输入患者年龄（一个整数）：")
        age = int(age) if age.isdigit() else age
    # 基因
    gene_num = -1
    gene_variant_list = []
    gene_raw = []
    while not (isinstance(gene_num, int) and gene_num>0):
        gene_num = input("请输入需要查询的基因数量（大于0的整数）：")
        gene_num = int(gene_num) if gene_num.isdigit() else gene_num
    for i in range(1, gene_num+1):
        gene = None
        while not isinstance(gene, str):
            gene = input(f"请输入基因{i}(可以为空，或者以字母开头，可由大写字母，数字，横线-_组成的字符串)：")
        variant = None
        if not gene:
            while not isinstance(variant, str) or not variant:
                variant = input(f"请输入基因{i}的变体(不可以为空)：")
        else:
            while not isinstance(variant, str):
                variant = input(f"请输入基因{i} {gene}的变体(可以为空)：")
        gene_raw.append(" ".join([gene, variant]))
        gene_variant_list.append({"gene": gene, "variant": variant})
    gene_raw = ", ".join(gene_raw)

    return {0: {
            "topic_id": 0,
            "disease": disease,
            "gene": gene_raw,
            "age": age,
            "gender": gender,

            "gene_variant": gene_variant_list,
        }}


if __name__ == "__main__":
    topics ={2017: topics_to_preprocessed_structure(config.topic_path[2017]),
             2018: topics_to_preprocessed_structure(config.topic_path[2018])}
    for t in topics[2018].values():
        print(t["gene"])
        print(t["gene_variant"])
        print("")

    # 输入的topic
    my_topic = input_topic()
    print(my_topic)