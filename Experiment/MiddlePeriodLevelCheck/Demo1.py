# encoding=utf-8

"""

将关心的和持仓的股票的中等长度的小时数据保存到json文件中
"""
from Config.AutoGenerateConfigFile import data_dir
from Config.Sub import readConfig


# 获取股票列表
from DataSource.Data_Sub import get_k_data_JQ
from Experiment.RelativeRank.Sub import get_RT_price, relativeRank, checkHourMACD_callback
from Experiment.SafeStkRelaLevel.Demo1 import calRelaPLevel, sendPLevel2QQ
from SDK.MyTimeOPT import get_current_date_str, add_date_str
from SendMsgByQQ.QQGUI import send_qq
import json
import pandas as pd



def update_middle_period_hour_data():
    stk_list = readConfig()['buy_stk'] + readConfig()['concerned_stk']
    # stk_list = readConfig()['buy_stk']

    # 获取股票的小时数据
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
    current_price = get_RT_price(stk_code, source='ts')

    if stk_code in dict.keys():
        l = relativeRank(dict[stk_code], current_price)
    else:
        df_hour = get_k_data_JQ(stk_code, count=None, start_date=add_date_str(get_current_date_str(), -60), freq='60m')
        dict[stk_code] = list(df_hour['close'].values)

        l = relativeRank(list(df_hour['close'].values), current_price)

        with open(data_dir + 'middlePeriodHourData.json', 'w') as f:
            json.dump(dict, f)

    return l


def check_stklist_middle_level(stk_list, towho):
    """
    检测一系列stk的中期水平
    :param stk_list:
    :param threshold:
    :return:
    """

    # 读取历史小时数据
    with open(data_dir+'middlePeriodHourData.json', 'r') as f:
        dict = json.load(f)

    # for stk in stk_list:
    #     if check_single_stk_middle_level(stk, dict) < threshold:
    #         send_qq(towho, stk + '低于历史' + str(1-threshold)*100 + '%的时刻！')

    r = [(x, (1-check_single_stk_middle_level(x, dict)/100)) for x in list(set(stk_list))]
    r_df = pd.DataFrame(data=r, columns=['code', 'level'])

    sendPLevel2QQ(r_df, towho)


def concerned_stk_middle_check():
    towho='影子2'

    stk_list = readConfig()['buy_stk'] + readConfig()['concerned_stk']
    check_stklist_middle_level(stk_list, towho)

    # 检查小时MACD
    checkHourMACD_callback()


if __name__ == '__main__':

    from DataSource.auth_info import *

    # update_middle_period_hour_data()
    concerned_stk_middle_check()
    end = 0

