# encoding=utf-8
import time
from jqdatasdk import *
import json
import tushare as ts

from Config.AutoGenerateConfigFile import data_source_url


def jq_login():
    with open(data_source_url, 'r') as f:
        r = json.load(f)
    
    success = False
    while not success:
        try:
            # 登录聚宽数据
            auth(r['JQ_Id'], r['JQ_passwd'])
            success = True
        except Exception as e_:
            print('链接聚宽数据失败，失败原因:\n %s \n5秒后重试...' % str(e_))
            time.sleep(5)


def ts_login():
    with open(data_source_url, 'r') as f:
        r = json.load(f)
        
    # 登录tushare数据
    ts.set_token(r['TS_token'])