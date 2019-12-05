# encoding=utf-8

"""
本脚本用来查看json文件中保存的信息

"""

# 将本次训练的精度写入json文件
import json

from Config.AutoStkConfig import rootPath

with open(rootPath + '\LSTM\AboutLSTM\stk_max_min.json', 'r') as f:
    json_max_min_info = json.load(f)

end = 0