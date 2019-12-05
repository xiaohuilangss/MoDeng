# encoding=utf-8

"""
本脚本计算最高点与最低点的信息

"""
import pickle

from CornerDetectAndAutoEmail.AveMaxMinDetect.Global import h_l_pot_info_url
from Config.GlobalSetting import g_total_stk_info_mysql
from HuiCe.Sub import get_name_by_stk_code
from SendMsgByQQ.QQGUI import send_qq
import os
"""
存储最高点和最低点的数据

思路：
对于关心的stk，待其接近   指定期限的最高点或者最低点时，发送消息通知！

需要指定的参数：

时期长度：多少天？（月线、半年线、年线）
接近程度：百分比

"""
from Config.AutoStkConfig import stk_list
import tushare as ts
from SDK.MyTimeOPT import get_current_date_str, add_date_str
import numpy as np
import pandas as pd


# h_l_pot_info = pd.DataFrame()

def get_h_l_pot(stk_list):
    """
    给定stklist，给出他们的“年度”、“半年度”、“月度”最高点和最低点！
    :param stk_list:
    :return:

      half_year_high  half_year_low  month_high  month_low     stk  year_high  \
0         1700.50        1205.03     1700.50    1316.10     cyb   1900.480
1         3106.42        2464.36     3106.42    2653.90      sh   3326.700
2         9700.49        7089.44     9700.49    7919.05      sz  11326.270
3           16.77          10.26       16.77      12.45  300508     19.656
4            8.94           5.68        8.94       7.79  000625     11.653
5            4.42           2.56        4.42       2.74  000725      5.972
    """

    current_date = get_current_date_str()               # 获取当前日期
    years_before = add_date_str(current_date, -365)     # 一年前日期
    half_year = add_date_str(current_date, -180)        # 半年前日期
    month_before = add_date_str(current_date, -30)      # 一月前日期

    # 存储结果的list
    MaxMinInfoList = []

    for stk in stk_list:

        # 下载数据
        df = ts.get_k_data(stk, start=years_before)

        # 计算年度高低点
        year_low = np.min(df['close'])
        years_high = np.max(df['close'])

        # 计算半年度高低点
        half_year_low = np.min(df[df['date'] > half_year]['close'])
        half_year_high = np.max(df[df['date'] > half_year]['close'])

        # 计算月度高低点
        month_low = np.min(df[df['date'] > month_before]['close'])
        month_high = np.max(df[df['date'] > month_before]['close'])

        MaxMinInfoList.append({
            'stk': stk,
            'year_low': year_low,
            'year_high': years_high,
            'half_year_low': half_year_low,
            'half_year_high': half_year_high,
            'month_low': month_low,
            'month_high': month_high
        })

    # 高低点转为df，这一天不再更改
    df_high_low_pot = pd.DataFrame(MaxMinInfoList)

    return df_high_low_pot


def lineJudge(df_H_L_Pot_index, current_price, df_info, line_str, neighbor_len=0.02):

    """
    判断年线、半年线及月线情况

    :param current_price:
    :param df_info:
    :param line_str:        ‘year’ ‘half_year’ ‘month’
    :return:
    """

    df_H_L_Pot = df_info
    stk = df_H_L_Pot_index

    line_name = {
        'year': u'年线',
        'half_year': u'半年线',
        'month': u'月线'
    }.get(line_str)

    if 0 <= current_price - df_H_L_Pot.loc[stk, line_str+'_low'] < df_H_L_Pot.loc[stk, line_str+'_low'] * neighbor_len:  # 下探年线
        df_H_L_Pot.loc[stk, line_str+'_status'] = u'接近'+line_name+'最低点'

    elif current_price - df_H_L_Pot.loc[stk, line_str+'_low'] < 0:
        df_H_L_Pot.loc[stk, line_str+'_status'] = u'跌破'+line_name+'最低点'

    elif 0 <= df_H_L_Pot.loc[stk, line_str+'_high'] - current_price < df_H_L_Pot.loc[
        stk, line_str+'_high'] * neighbor_len:  # 上攻年线高点
        df_H_L_Pot.loc[stk, line_str+'_status'] = u'接近'+line_name+'最高点'

    elif df_H_L_Pot.loc[stk, line_str+'_high'] - current_price < 0:
        df_H_L_Pot.loc[stk, line_str+'_status'] = u'攻破'+line_name+'最高点'

    else:
        df_H_L_Pot.loc[stk, line_str+'_status'] = u'正常'

    return df_H_L_Pot


def initPotInfo(df_H_L_Pot):

    """ 设置默认状态，皆为false  """
    df_H_L_Pot['year_status_last'] = u'正常'
    df_H_L_Pot['half_year_status_last'] = u'正常'
    df_H_L_Pot['month_status_last'] = u'正常'

    return df_H_L_Pot


def judgeAndSendMsg():
    """
    按频率调用，
    :return:
    """
    if os.path.exists(h_l_pot_info_url):
        with open(h_l_pot_info_url, 'rb') as f:
            h_l_pot_info = pickle.load(f)
    else:
        print('函数 judgeAndSendMsg: 加载高低信息失败！')
        return

    df_H_L_Pot = h_l_pot_info

    for stk in df_H_L_Pot.index:

        # 获取该stk的实时价格
        current_price = float(ts.get_realtime_quotes(df_H_L_Pot.loc[stk, 'stk'])['price'].values[0])

        # 将当前价格保存，用于验证计算准确性
        df_H_L_Pot.loc[stk, 'current_price'] = current_price

        """ 年线判断 """
        df_H_L_Pot = lineJudge(df_H_L_Pot_index=stk, current_price=current_price, df_info=df_H_L_Pot, line_str='year')

        """ ----------------- 半年线判断 -----------------"""
        df_H_L_Pot = lineJudge(df_H_L_Pot_index=stk, current_price=current_price, df_info=df_H_L_Pot, line_str='half_year')

        """ ----------------- 月线判断 ----------------"""
        df_H_L_Pot = lineJudge(df_H_L_Pot_index=stk, current_price=current_price, df_info=df_H_L_Pot, line_str='month')

    """ 检查并发送消息 """
    for idx in df_H_L_Pot.index:

        # 遍历年线、半年线和月线
        for sts in ['year_status', 'half_year_status', 'month_status']:
            if (df_H_L_Pot.loc[idx, sts] != u'正常') & (df_H_L_Pot.loc[idx, sts] != df_H_L_Pot.loc[idx, sts + '_last']):
                send_qq(u'影子',
                        'stk:' + get_name_by_stk_code(g_total_stk_info_mysql, df_H_L_Pot.loc[idx, 'stk']) + '\n' +
                        '当前价格：' + str(df_H_L_Pot.loc[idx, 'current_price']) + '\n' +
                        '事件： “' + df_H_L_Pot.loc[idx, sts + '_last'] +'” --> “' + df_H_L_Pot.loc[idx, sts] +'”' +
                        '\n\n')

                df_H_L_Pot.loc[idx, sts + '_last'] = df_H_L_Pot.loc[idx, sts]

    with open(h_l_pot_info_url, 'wb') as f:
        pickle.dump(h_l_pot_info, f)

    print('函数 judgeAndSendMsg: 完成本次判断！')


def update_price_ratio_info():
    """
    :param df_H_L_Pot:
    :return:
    """

    # 将结果序列化
    with open(price_ratio_info_url, 'wb') as f:
        pickle.dump(h_l_pot_info, f)

    send_qq(u'影子', '高底线信息更新成功！')


def updatePotInfo():
    """
    :param df_H_L_Pot:
    :return:
    """
    # h_l_pot_info_url = '.\InfoRestore\df_H_L_Pot.pkl'
    if os.path.exists(h_l_pot_info_url):
        with open(h_l_pot_info_url, 'rb') as f:
            try:
                h_l_pot_info = pickle.load(f)
            except:
                h_l_pot_info = pd.DataFrame()
    else:
        h_l_pot_info = pd.DataFrame()

    if h_l_pot_info.empty:
        h_l_pot_info = initPotInfo(get_h_l_pot(stk_list))
    else:
        new_pot_info = get_h_l_pot(stk_list)

        h_l_pot_info = pd.concat([
            h_l_pot_info.drop(['half_year_high', 'half_year_low', 'month_high', 'month_low', 'year_high', 'year_low'], 1),
            new_pot_info.drop('stk', 1)
        ], axis=1)

    # 将结果序列化
    with open(h_l_pot_info_url, 'wb') as f:
        pickle.dump(h_l_pot_info, f)

    send_qq(u'影子', '高底线信息更新成功！')


# ------------------------------------- 测试 -----------------------------------
#
# df_H_L_Pot = get_h_l_pot(stk_list)
#
# df_H_L_Pot = initPotInfo(df_H_L_Pot)
#
# df_H_L_Pot = judgeAndSendMsg(df_H_L_Pot)

"""
对不同的点，

上攻采用：
进攻、占领、丢失三种报告


对于下落：
防守、沦陷、收复三种报告

half_year_high  half_year_low  month_high  month_low   year_low  year_high

"""


