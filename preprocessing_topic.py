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

from configs.config import config


#%%
# 把xml文件提取成list of topic
def topics_to_preprocessed_structure(xml_path: str):
    xml = ET.parse(xml_path)
    root = xml.getroot()
    topics = []
    for xml_topic in root.findall("topic"):
        topic_id = int(xml_topic.attrib['number'])
        disease = xml_topic.find("disease").text
        gene = xml_topic.find("gene").text
        demographic = xml_topic.find("demographic").text
        r_age = re.compile(r"(.*)-year-old")
        age = int(r_age.findall(demographic)[0])
        r_gender = re.compile(r"-year-old (.*)")
        gender = r_gender.findall(demographic)[0]
        new_topic = {
            "topic_id": topic_id,
            "disease": disease,
            "gene": gene,
            "age": age,
            "gender": gender
        }
        topics.append(new_topic)
    return topics


if __name__ == "__main__":
    xml_file_path = config.topic_path[2018]
    topics = topics_to_preprocessed_structure(xml_file_path)