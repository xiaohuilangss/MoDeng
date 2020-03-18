# encoding=utf-8
from DataSource.Data_Sub import get_k_data_JQ
from DataSource.auth_info import jq_login
from jqdatasdk import *
"""
some test code about futures
"""
if __name__ == '__main__':
    jq_login()

    # 获取所有futures
    a = get_all_securities(types=['futures'])
    
    df = get_k_data_JQ('IF1605.CCFX', count=200)
    df = get_price('IC1505.CCFX', start_date='2015-05-06', end_date='2015-05-08')
    
    # 获取单个
    r = get_security_info('IF1605.CCFX')
    
    end = 0