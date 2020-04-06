# coding=utf-8

from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']

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


# 调试文件存储路径
g_debug_file_url = "F:/MYAI/文档资料/用于调试的过程文件/"

# 数据存放路径
g_wr_file_url = "F:/MYAI/文档资料/用于读取的文件/"


# --------------------------调试标志位--------------------------------------
g_find_case_debug_enable = False                        # “搜寻案例”调试标志位
g_find_case_debug_file_name = "findCase_db.txt"         # “搜寻案例”调试文件名字

g_lstm_debug_enable = True                              # “LSTM”调试标志位
g_lstm_debug_file_name = "lstm_db.txt"                  # “LSTM”调试文件名字



