# encoding=utf-8

"""
常用定时控制中的子函数
"""
from Config.AutoStkConfig import rootPath
import json
import os

"""
F:\MYAI\Code\master\My_Quant\AutoDailyOpt\LocalRecord
"""
last_p_file_url = rootPath + '\AutoDailyOpt\LocalRecord\last_p.json'


def readLastP(stk_code):

    if os.path.exists(last_p_file_url):
        with open(last_p_file_url, 'r') as f:
            json_p = json.load(f)

        if stk_code in json_p.keys():
            return json_p[stk_code]
        else:
            return -1
    else:
        with open(last_p_file_url, 'w') as f:
            json.dump(obj={}, fp=f)


def saveLastP(stk_code, p):
    with open(last_p_file_url, 'r') as f:
        json_p = json.load(f)

    json_p[stk_code] = p

    with open(last_p_file_url, 'w') as f:
        json.dump(obj=json_p, fp=f)

    print('函数 saveLastP：' + stk_code + '历史price发生修改！修正为'+str(p))


if __name__ == '__main__':
    saveLastP('000001', 25)
    
    end = 0
