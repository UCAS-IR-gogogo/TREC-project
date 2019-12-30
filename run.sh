#!/usr/bin/env

echo "正在构建索引......"
#python3 main.py
echo "构建索引完毕"
while true
do
echo -n  "输入查询topic:"
read  num
if [[ $num =~ 'exit' ]]; then
echo "bye"
break
else
python3 preprocessing_topic_v2.py $num
fi
done
