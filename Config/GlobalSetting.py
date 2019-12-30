# coding=utf-8
import matplotlib
# matplotlib.use('Agg')
from sqlalchemy import create_engine
from SDK.DBOpt import *
import pymysql
from pylab import *
import tensorflow as tf
import tushare as ts
from pandas import DataFrame
import pandas as pd
import numpy as np

mpl.rcParams['font.sans-serif'] = ['SimHei']

import os
# localDBAddr = {'host': 'localhost',
#                'port': 3306,
#                'user': 'root',
#                'passwd': 'myDBpassword',
#                'db': 'stk_k_data',
#                'charset': 'utf8'}
#
#
# db_info = {'user': 'root',
#            'password': 'myDBpassword',
#            'host': 'localhost',
#            'database': 'stockhistdata'
#            }
#
# # db_JQ_money_flow = {'host': 'localhost',
# #                 'port': 3306,
# #                 'user': 'root',
# #                 'password': 'myDBpassword',
# #                 'database': 'stk_k_data',
# #                 'charset': 'utf8'}
#
# db_info_k = {'host': 'localhost',
#                 'port': 3306,
#                 'user': 'root',
#                 'password': 'myDBpassword',
#                 'database': 'stk_k_data',
#                 'charset': 'utf8'}
#
# db_info_tick = {'host': 'localhost',
#                 'port': 3306,
#                 'user': 'root',
#                 'password': 'myDBpassword',
#                 'database': 'stk_tick_data',
#                 'charset': 'utf8'}
#
# db_info_basic = {'host': 'localhost',
#                  'port': 3306,
#                  'user': 'root',
#                  'password': 'myDBpassword',
#                  'database': 'stk_basic_data',
#                  'charset': 'utf8'}
#
# db_info_dd = {'host': 'localhost',
#                  'port': 3306,
#                  'user': 'root',
#                  'password': 'myDBpassword',
#                  'database': 'stk_dd_data',
#                  'charset': 'utf8'}
#
# db_info_stkBasics = {'host': 'localhost',
#                      'port': 3306,
#                      'user': 'root',
#                      'password': 'myDBpassword',
#                      'database': 'stk_stkBasics_data',
#                      'charset': 'utf8'}
#
# engine = create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % db_info)
# engine_k = create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % db_info_k)
# engine_tick = create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % db_info_tick)
# engine_basic = create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % db_info_basic)
# engine_dd = create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % db_info_dd)
# engine_stkBasics = create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % db_info_stkBasics)
#
#
# conn_tick = pymysql.connect(
#     host=db_info_tick['host'],
#     port=db_info_tick['port'],
#     user=db_info_tick['user'],
#     passwd=db_info_tick['password'],
#     db=db_info_tick['database'],
#     charset=db_info_tick['charset']
#     )
#
# conn_k = pymysql.connect(
#     host=db_info_k['host'],
#     port=db_info_k['port'],
#     user=db_info_k['user'],
#     passwd=db_info_k['password'],
#     db=db_info_k['database'],
#     charset=db_info_k['charset']
#     )
#
# conn_basic = pymysql.connect(
#     host=db_info_basic['host'],
#     port=db_info_basic['port'],
#     user=db_info_basic['user'],
#     passwd=db_info_basic['password'],
#     db=db_info_basic['database'],
#     charset=db_info_basic['charset']
#     )
#
# conn_dd = pymysql.connect(
#     host=db_info_basic['host'],
#     port=db_info_basic['port'],
#     user=db_info_basic['user'],
#     passwd=db_info_basic['password'],
#     db=db_info_basic['database'],
#     charset=db_info_basic['charset']
#     )
#
# conn_stkBasics = pymysql.connect(
#     host=db_info_stkBasics['host'],
#     port=db_info_stkBasics['port'],
#     user=db_info_stkBasics['user'],
#     passwd=db_info_stkBasics['password'],
#     db=db_info_stkBasics['database'],
#     charset=db_info_stkBasics['charset']
#     )
#
# # table name info
total_stk_info_table_name = 'basic_stk_info'
#
# # db name info
stk_k_data_db_name = 'stk_k_data'
stk_basic_data_db_name = 'stk_basic_data'
stk_tick_data_db_name = 'stk_tick_data'
stk_dd_data_db_name = 'stk_dd_data'
stk_stkBasics_data_db_name = 'stk_stkBasics_data'
#
#
stk_profit_data_db_name     = 'stk_profit_data'
stk_growth_data_db_name     = 'stk_growth_data'
stk_operation_data_db_name  = 'stk_operation_data'
stk_debtpaying_data_db_name = 'stk_debtpaying_data'
stk_cashflow_data_db_name   = 'stk_cashflow_data'
stk_industry_data_db_name   = 'stk_industry_data'
stk_days_all_data_db_name   = 'stk_days_all_data'


# 新方式：lacalDBInfo包括除了“数据库名”之外的其他参数
localDBInfo = {'host': 'localhost',
               'port': 3306,
               'user': 'root',
               'password': 'yourpasswd',
               'charset': 'utf8'}


src_current = 'sn'

# 全局数据下载重试延时参数（秒）
gSleepTime = 10

plot_current_days_amount = 40   # 画出近期的stk走势情况，该参数指示最近取的天数
tailLengthForMACD = 150         # 在计算MACD时，因为之用最近的几个数，所以不需要往前延伸太多，以节省计算量


# 所有stk信息：

# 读取total stk 信息
# g_total_stk_info_mysql = get_total_table_data(conn_basic, total_stk_info_table_name)

# stk code信息
# g_total_stk_code = g_total_stk_info_mysql.code

# 调试文件存储路径
g_debug_file_url = "F:/MYAI/文档资料/用于调试的过程文件/"

# 数据存放路径
g_wr_file_url = "F:/MYAI/文档资料/用于读取的文件/"



# stk基本信息
# stk_basic = ts.get_stock_basics()


# --------------------------调试标志位--------------------------------------
g_find_case_debug_enable = False                        # “搜寻案例”调试标志位
g_find_case_debug_file_name = "findCase_db.txt"         # “搜寻案例”调试文件名字

g_lstm_debug_enable = True                              # “LSTM”调试标志位
g_lstm_debug_file_name = "lstm_db.txt"                  # “LSTM”调试文件名字



