# encoding=utf-8

from sdk.SDKHeader import *
from DataProcess.CNNClassify.GlobalSetting_CNNtest import *

#
# """
# 准备数据：
#
#
# A、feature：
# ---------------
#
#
# “close”
# “7日均”
# “30日均”
# “60日均”
# “180日均”
#
# ['mbrg'],   '主营业务收入增长率'
# ['nprg'],   '净利润增长率'
# ['nav'],    '净资产增长率'
# ['targ'],   '总资产增长率'
# ['epsg'],   '每股收益增长率'
# ['seg'],    '股东权益增长率'
#
#
# ['business_income'],        '营业收入'
# ['gross_profit_rate'],      '毛利率'
# ['bips'],                   '每股主营业务收入'
# ['eps'],                    '每股收益'
# ['net_profit_ratio'],       '净利率'
# ['net_profits'],            '净利润'
# ['roe'],                    '净资产收益率'
#
#
# 板块指数均线（待补充）
# 大盘指数均线（待补充）
#
#
#
# B、label
# -----------
# 未来N日m30增长率？
#
#
#
# =====================================================================
#
# 思路：
#
# 以stk代码为索引，首先准备价格均线类，格式如下：
#
# 然后准备该代码相关的“盈利性”和“成长性”数据
#
# 在准备环境数据，包括“大盘均线”、“板块均线”及外围的货币环境
# """


# ------------准备数据--------------
batch_gen_cnn_data(g_total_stk_code[0:30],20,field_list_volume,time_span_list_volume,save_dir)
# batch_gen_cnn_data_only_ave(g_total_stk_code[51:500],20,save_dir_ave)


