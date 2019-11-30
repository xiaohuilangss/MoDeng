# encoding=utf-8

from jqdatasdk import *
import json
import tushare as ts

from Config.AutoGenerateConfigFile import data_source_url


def jq_login():
    with open(data_source_url, 'r') as f:
        r = json.load(f)
    
    # 登录聚宽数据
    auth(r['JQ_Id'], r['JQ_passwd'])


def ts_login():
    with open(data_source_url, 'r') as f:
        r = json.load(f)
        
    # 登录tushare数据
    ts.set_token(r['TS_token'])