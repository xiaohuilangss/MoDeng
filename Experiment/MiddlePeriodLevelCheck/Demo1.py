# encoding=utf-8

"""

将关心的和持仓的stk的中等长度的小时数据保存到json文件中
"""
from Config.AutoGenerateConfigFile import data_dir
from Config.Sub import read_config


# 获取stk列表
from DataSource.Data_Sub import get_k_data_JQ
from Experiment.RelativeRank.Sub import get_RT_price, relativeRank, checkHourMACD_callback
# from Experiment.SafeStkRelaLevel.Demo1 import calRelaPLevel, sendPLevel2QQ
from SDK.MyTimeOPT import get_current_date_str, add_date_str
from SendMsgByQQ.QQGUI import send_qq
import json
import pandas as pd


def update_middle_period_hour_data():
    stk_list = read_config()['buy_stk'] + read_config()['concerned_stk']
    # stk_list = readConfig()['buy_stk']

    # 获取stk的小时数据
    result = {}
    for stk in stk_list:
        df_hour = get_k_data_JQ(stk, count=None, start_date=add_date_str(get_current_date_str(), -60), freq='60m')
        result[stk] = list(df_hour['close'].values)

    with open(data_dir+'middlePeriodHourData.json', 'w') as f:
        json.dump(result, f)


def check_single_stk_middle_level(stk_code, dict):
    """
    输入代码，返回level
    :param stk_code:
    :return:
    """
    # 获取当前价格
    current_price = get_RT_price(stk_code, source='jq')

    if stk_code in dict.keys():
        l = relativeRank(dict[stk_code], current_price)
    else:
        df_hour = get_k_data_JQ(stk_code, count=None, start_date=add_date_str(get_current_date_str(), -60), freq='60m')
        dict[stk_code] = list(df_hour['close'].values)

        l = relativeRank(list(df_hour['close'].values), current_price)

        with open(data_dir + 'middlePeriodHourData.json', 'w') as f:
            json.dump(dict, f)

    return l


if __name__ == '__main__':

    from DataSource.auth_info import *


    end = 0

