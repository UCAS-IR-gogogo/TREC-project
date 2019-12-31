#!/usr/bin/env bash
# 安装docker
# 注：我的docker已经装好了。不确定这个命令能不能安装成功
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 获取ElasticSearch镜像
docker pull elasticsearch:6.5.0  # pull es docker镜像
docker run --name ES -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:6.5.0  # 启动docker
curl -X GET localhost:9200  # 测试是否安装成功

# python需要的包
conda create -n IR -python=3.7
conda activate IR
pip install -r requirements.txt
