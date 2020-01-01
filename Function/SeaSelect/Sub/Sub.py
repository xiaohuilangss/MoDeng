# encoding=utf-8

import calendar
import talib
import pandas as pd
import tushare as ts

from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_k_data_JQ
from DataSource.auth_info import jq_login, logout
from Experiment.CornerDetectAndAutoEmail.Sub import genStkIdxPicForQQ, genStkPicForQQ
from Function.SeaSelect.gen_pic import gen_stk_sea_select_pic
from SDK.Gen_Stk_Pic_Sub import gen_hour_macd_values

from SDK.SendMsgByQQ.QQGUI import send_qq
from SDK.SendMsgByQQ.SendPicByQQ import send_pic_qq

from pylab import *
from SDK.MyTimeOPT import get_current_date_str, add_date_str


def download_stk_list_day_data(stk_list):
    """
    给定stk_list,下载日期数据,以tuple的形式返回
    :return:
    """

    jq_login()
    stk_list_data = [(x, get_k_data_JQ(x)) for x in stk_list]
    logout()

    return stk_list_data


def download_stk_list_hour_data(stk_list):
    """
    给定stk_list,下载半小时数据,以tuple的形式返回
    :return:
    """

    jq_login()
    stk_list_data = [(x, gen_hour_macd_values(x)) for x in stk_list]
    logout()

    return stk_list_data


def week_macd_judge(df_day, stk_code='', debug=False):
    """
    判断周线macd的反转情况
    :param df_day: df_day = get_k_data_JQ(stk_code, 800)
    :param stk_code:
    :return:
    """
    try:
        if debug:
            print('开始计算' + str(stk_code) + '的周线macd判断！')

        # 计算周线数据
        df_week = get_week_month_index_data(df_day, stk_code='')[0]

        # 判断周线转折
        return week_macd_stray_judge_sub(df_week, debug_plot=False)

    except Exception as e:
        print('周反转判断失败，原因：\n' + str(e))
        return False


def get_week_month_index_data(df_stk, stk_code=''):
    """
    给定日线数据，计算周线/月线指标！
    :param df_stk:
     
     get_k_data_JQ(stk_code, count=400, end_date=get_current_date_str()).reset_index()
    
    :return:
    """

    df = df_stk

    if len(df) < 350:
        print('函数week_MACD_stray_judge：' + stk_code + '数据不足！')
        return False, pd.DataFrame()

    # 规整
    df_floor = df.tail(math.floor(len(df) / 20) * 20 - 19)

    # 增加每周的星期几
    df_floor['day'] = df_floor.apply(
        lambda x: calendar.weekday(int(x['date'].split('-')[0]), int(x['date'].split('-')[1]),
                                   int(x['date'].split('-')[2])), axis=1)

    # 隔着5个取一个
    if df_floor.tail(1)['day'].values[0] != 4:
        df_week = pd.concat([df_floor[df_floor.day == 4], df_floor.tail(1)], axis=0)
    else:
        df_week = df_floor[df_floor.day == 4]

    # 计算指标
    df_week['MACD'], df_week['MACDsignal'], df_week['MACDhist'] = talib.MACD(
        df_week.close,
        fastperiod=6, slowperiod=12,
        signalperiod=9)

    # 隔着20个取一个（月线）
    df_month = df_floor.loc[::20, :]

    # 计算指标
    df_month['MACD'], df_month['MACDsignal'], df_month['MACDhist'] = talib.MACD(
        df_month.close,
        fastperiod=4,
        slowperiod=8,
        signalperiod=9)
    
    return df_week, df_month


def sar_stray_judge(df_stk, debug=False):
    """
    判断sar的反转情况，返回三种值
    -1, 0， 1
    -1：向下反转
    0：未反转
    1：向上反转
    
    :param df_stk:
    :return:
    """
    try:
        df_tail = df_stk.tail(2).reset_index()

        if (df_tail.loc[1, 'SAR'] >= df_tail.loc[1, 'close']) & (df_tail.loc[0, 'SAR'] <= df_tail.loc[0, 'close']):
            return -1
        elif (df_tail.loc[1, 'SAR'] <= df_tail.loc[1, 'close']) & (df_tail.loc[0, 'SAR'] >= df_tail.loc[0, 'close']):
            return 1
        else:
            return 0
    except Exception as e:
        print('sar反转判断失败，原因：\n' + str(e))
        return 0


def week_macd_stray_judge_sub(df_week, debug_plot=False):

    """
    对周线macd反转进行判断
    :param stk_code:
    :param towho:
    :param debug_plot:
    :return:
    """
    # 判断背离
    macd_week = df_week.tail(3)['MACD'].values
    if macd_week[1] == np.min(macd_week):
        return True
    else:
        return False


def stk_sea_select(stk_code, tc):

    try:

        """ ------------------------ 下载原始数据 ------------------------------- """
        df = get_k_data_JQ(stk_code, count=400, end_date=get_current_date_str()).reset_index()

        if len(df) < 350:
            print('函数week_MACD_stray_judge：'+stk_code + '数据不足！')
            return False, pd.DataFrame()

        # 规整
        df_floor = df.tail(math.floor(len(df)/20)*20-19)

        """ ------------------------ 判断周线是否达标 ------------------------------- """
        # 增加每周的星期几
        df_floor['day'] = df_floor.apply(
            lambda x: calendar.weekday(int(x['date'].split('-')[0]), int(x['date'].split('-')[1]),
                                       int(x['date'].split('-')[2])), axis=1)

        # 增加每周的星期几
        df_floor['day'] = df_floor.apply(lambda x: calendar.weekday(int(x['date'].split('-')[0]), int(x['date'].split('-')[1]), int(x['date'].split('-')[2])), axis=1)

        # 隔着5个取一个
        if df_floor.tail(1)['day'].values[0] != 4:
            df_floor_slice_5 = pd.concat([df_floor[df_floor.day == 4], df_floor.tail(1)], axis=0)
        else:
            df_floor_slice_5 = df_floor[df_floor.day == 4]

        # 计算周线指标
        df_floor_slice_5['MACD'], df_floor_slice_5['MACDsignal'], df_floor_slice_5['MACDhist'] = talib.MACD(df_floor_slice_5.close,
                                                                              fastperiod=6, slowperiod=12,
                                                                              signalperiod=9)

        # 判断周线的走势,周线不是底部，直接返回
        MACD_5 = df_floor_slice_5.tail(3)['MACD'].values
        if not (MACD_5[1] == np.min(MACD_5)):
            tc.AppendText(stk_code + code2name(stk_code) + '：“周线”不符合要求！')
            return False

        """ ------------------------ 判断月线是否达标 ------------------------------- """
        # 隔着20个取一个（月线）
        df_floor_slice_20 = df_floor.loc[::20, :]

        # 计算指标
        df_floor_slice_20['MACD'], df_floor_slice_20['MACDsignal'], df_floor_slice_20['MACDhist'] = talib.MACD(
            df_floor_slice_20.close,
            fastperiod=4,
            slowperiod=8,
            signalperiod=9)

        # 获取最后的日期
        date_last = df_floor_slice_5.tail(1)['date'].values[0]

        # 判断月线的走势，不符合条件直接返回
        MACD_20 = df_floor_slice_20.tail(4)['MACD'].values
        if not ((MACD_20[1] != np.max(MACD_20)) & (MACD_20[2] != np.max(MACD_20))):
            tc.AppendText(stk_code + code2name(stk_code) + '：“月线”不符合要求！')
            return False

        """ ------------------------ 判断日线SAR是否达标 ------------------------------- """

        # 判断日线SAR指标
        df_floor['SAR'] = talib.SAR(df_floor.high, df_floor.low, acceleration=0.05, maximum=0.2)
        if df_floor.tail(1)['SAR'].values[0] > df_floor.tail(1)['SAR'].values[0]:
            tc.AppendText(stk_code + code2name(stk_code) + '：“日线SAR指标”不符合要求！')
            return False

        """ ------------------------ 判断半小时SAR是否达标 ------------------------------- """
        df_half_hour = get_k_data_JQ(stk_code, count=120,
                              end_date=add_date_str(get_current_date_str(), 1), freq='30m')

        # 判断日线SAR指标
        df_half_hour['SAR'] = talib.SAR(df_half_hour.high, df_half_hour.low, acceleration=0.05, maximum=0.2)
        if df_half_hour.tail(1)['SAR'].values[0] > df_half_hour.tail(1)['SAR'].values[0]:
            tc.AppendText(stk_code + code2name(stk_code) + '：“半小时SAR指标”不符合要求！')
            return False

        # 符合要求，返回True
        tc.AppendText(stk_code + code2name(stk_code) + '：符合要求！')
        return True

    except Exception as e:
        tc.AppendText(stk_code + '出错：\n' + str(e))
        return False


def cal_stk_p_level(c):
    """
    计算stk水平，包括总水平，近30水平以及近30的波动率
    :param p_array:
    :return:
    """
    # 进行归一化
    c = (c - np.min(c)) / (np.max(c) - np.min(c))

    # 最后30个数
    c_tail30 = c[-30:]

    # 进行归一化
    c_t30 = (c_tail30 - np.min(c_tail30))/(np.max(c_tail30) - np.min(c_tail30))

    # 计算最后30个数的标准差
    c_t30_std = np.std(c_t30)

    return {
        'std': c_t30_std,
        'total_last': c[-1],
        't30_last': c_t30[-1]
    }


def sea_select():

    jq_login()

    df_total = ts.get_stock_basics()[:200]

    # 过滤掉年龄小于四岁的
    df_stk = df_total[df_total.apply(lambda x: int(str(x['timeToMarket'])[:4]) <= int(get_current_date_str()[:4])-4, axis=1)]

    print('已过滤掉上市小于4年的股票！')

    # 根据week反转情况进行过滤，保留有反转的单位
    df_stk['week_stray'] = df_stk.reset_index().apply(lambda x: week_macd_judge(x['code'], debug=True), axis=1)
    df_stk = df_stk[list[df_stk['week_stray']]]
    print('已过滤出周线macd转折的股票！')

    # 找出半小时线反转的股票
    df_stk['hour_stray'] = df_stk.reset_index().apply(lambda x: sar_stray_judge(gen_hour_macd_values(x['code'], debug=True)[0]), axis=1)
    df_stk = df_stk[df_stk.apply(lambda x: x['hour_stray'] == 1, axis=1)]
    print('已过滤出半小时sar转折的股票！')

    # 增加stk的水平信息
    # df_level = [(x[0], x[1][1], cal_stk_p_level(x[1][1]['close'].values)) for x in df_stk]

    # 按总体水平排序，筛选优异者
    # df_level.sort(key=lambda x: x[2]['total_last'])
    # df_level = df_level[:math.floor(len(df_level)/3*2)]
    #
    # # 按照近30的波动率进行排序,筛选优异者
    # df_level.sort(key=lambda x: x[2]['std'], reverse=True)
    # df_level = df_level[:math.floor(len(df_level) / 3 * 2)]
    #
    # # 按照近30的水平排序，留下最后8只
    # df_level.sort(key=lambda x: x[2]['t30_last'], reverse=False)
    # df_level = df_level[:np.min([math.floor(len(df_level) / 3 * 2), 15])]

    logout()

    # 打印信息
    stk_list = [k[0] for k in df_stk.index]

    for stk in stk_list:

        # 将选定的股票的走势图打印到本地
        gen_stk_sea_select_pic(stk)


if __name__ == '__main__':

    sea_select()

    df = ts.get_stock_basics()

    # 遍历所有股票
    list(df.index)

    end = 0