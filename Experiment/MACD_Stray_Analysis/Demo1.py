# encoding=utf-8

"""


"""
import calendar
import pandas as pd
import talib
import numpy as np
import tushare as ts
import math
import matplotlib
# matplotlib.use('agg')
from io import BytesIO


from Experiment.CornerDetectAndAutoEmail.Sub import genStkIdxPicForQQ, genStkPicForQQ
from Experiment.RelativeRank.Sub import get_k_data_JQ

from SendMsgByQQ.QQGUI import send_qq
from SendMsgByQQ.SendPicByQQ import send_pic_qq, send_pic_qq_data
from PIL import Image

from pylab import *
from SDK.MyTimeOPT import get_current_date_str, add_date_str


def plot_W_M(df_w, df_m):
    """

    :param df_w:
    :param df_m:
    :return:
    """
    """ --------------------------------------- 生成图片 -------------------------------------"""
    fig, ax = subplots(ncols=1, nrows=4)

    ax[0].plot(range(0, len(df_w['date'])), df_w['close'], 'g*--', label='close')
    ax[1].bar(range(0, len(df_w['date'])), df_w['MACD'],  label='week_macd')
    ax[1].plot(range(0, len(df_w['date'])), [0 for x in range(0, len(df_w['date']))], 'r--', label='week_macd')

    ax[2].plot(range(0, len(df_m['date'])), df_m['close'], 'g*--', label='close')
    ax[3].bar(range(0, len(df_m['date'])), df_m['MACD'],  label='month_macd')
    ax[3].plot(range(0, len(df_m['date'])), [0 for x in range(0, len(df_m['date']))], 'r--', label='month_macd')

    return fig, ax

def send_W_M_Macd(stk_code, towho):
    """

    :param stk_code:
    :param towho:
    :return:
    """

    # 获取今天的情况，涨幅没有超过3%的不考虑
    # df_now = get_k_data_JQ(stk_code, count=2, end_date=get_current_date_str()).reset_index()
    #
    # if (df_now.tail(1)['close'].values[0]-df_now.head(1)['close'].values[0])/df_now.head(1)['close'].values[0] < 0.03:
    #     print('函数week_macd_stray_judge：' + stk_code + '涨幅不够！')
    #     return False

    df = get_k_data_JQ(stk_code, count=400, end_date=get_current_date_str()).reset_index()

    if len(df) < 350:
        print('函数week_macd_stray_judge：'+stk_code + '数据不足！')
        return False

    # 规整
    df_floor = df.tail(math.floor(len(df)/20)*20-19)

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

    # 获取最后的日期
    date_last = df_floor_slice_5.tail(1)['date'].values[0]

    # 计算指标
    df_floor_slice_5['MACD'], df_floor_slice_5['MACDsignal'], df_floor_slice_5['MACDhist'] = talib.MACD(df_floor_slice_5.close,
                                                                          fastperiod=6, slowperiod=12,
                                                                          signalperiod=9)

    # 隔着20个取一个（月线）
    df_floor_slice_20 = df_floor.loc[::20, :]

    # 计算指标
    df_floor_slice_20['MACD'], df_floor_slice_20['MACDsignal'], df_floor_slice_20['MACDhist'] = talib.MACD(
        df_floor_slice_20.close,
        fastperiod=4,
        slowperiod=8,
        signalperiod=9)

    """ --------------------------------------- 生成图片 -------------------------------------"""
    fig, ax = plot_W_M(df_floor_slice_5, df_floor_slice_20)

    # 增加标题
    plt.title(stk_code + 'month-stray' + date_last)

    # 发送图片
    send_pic_qq(towho, fig)

    # 关闭图片
    plt.close()


def week_macd_stray_judge(stk_code, towho, debug_plot=False):

    try:
        # 获取今天的情况，涨幅没有超过3%的不考虑
        df_now = get_k_data_JQ(stk_code, count=2, end_date=get_current_date_str()).reset_index()

        if (df_now.tail(1)['close'].values[0]-df_now.head(1)['close'].values[0])/df_now.head(1)['close'].values[0] < -0.05:
            print('函数week_macd_stray_judge：' + stk_code + '涨幅不够！')
            return False, pd.DataFrame()

        df = get_k_data_JQ(stk_code, count=400, end_date=get_current_date_str()).reset_index()

        if len(df) < 350:
            print('函数week_macd_stray_judge：'+stk_code + '数据不足！')
            return False, pd.DataFrame()

        # 规整
        df_floor = df.tail(math.floor(len(df)/20)*20-19)

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

        # 计算指标
        df_floor_slice_5['MACD'], df_floor_slice_5['MACDsignal'], df_floor_slice_5['MACDhist'] = talib.MACD(df_floor_slice_5.close,
                                                                              fastperiod=6, slowperiod=12,
                                                                              signalperiod=9)

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

        # 判断背离
        macd_5 = df_floor_slice_5.tail(3)['MACD'].values
        macd_20 = df_floor_slice_20.tail(4)['MACD'].values
        if (macd_5[1] == np.min(macd_5)) & (macd_20[1] != np.max(macd_20)) & (macd_20[2] != np.max(macd_20)):

            if debug_plot:
                """ --------------------------------------- 生成图片 -------------------------------------"""
                fig, ax = plot_W_M(df_floor_slice_5, df_floor_slice_20)

                # 增加标题
                plt.title(stk_code + 'month-stray' + date_last)

                # 发送图片
                send_pic_qq(towho, fig)

                # 关闭图片
                plt.close()
            return True, df
        else:
            return False, pd.DataFrame()
    except Exception as e:
        send_qq(towho, stk_code + '出错：\n' + str(e))
        return False, pd.DataFrame()

def calStkPlevel(c):
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


def checkWeekStrayForAll():

    towho = '影子2'
    send_qq(towho, '以下是今晚海选结果：')

    df_total = ts.get_stock_basics()

    # 过滤掉年龄小于四岁的
    df_age_filter = df_total[df_total.apply(lambda x: int(str(x['timeToMarket'])[:4]) <= int(get_current_date_str()[:4]) - 4, axis=1)]

    # 根据week反转情况进行过滤，保留有反转的单位
    df_age_filter_stray = list(df_age_filter.reset_index().apply(lambda x: (x['code'], week_macd_stray_judge(x['code'], towho)), axis=1))

    # 过滤掉非反转的情况
    df_age_f2 = list(filter(lambda x: x[1][0], df_age_filter_stray))

    # 增加stk的水平信息
    df_level = [(x[0], x[1][1], calStkPlevel(x[1][1]['close'].values)) for x in df_age_f2]

    # 按总体水平排序，筛选优异者
    df_level.sort(key=lambda x: x[2]['total_last'])
    df_level = df_level[:math.floor(len(df_level)/3*2)]

    # 按照近30的波动率进行排序,筛选优异者
    df_level.sort(key=lambda x: x[2]['std'], reverse=True)
    df_level = df_level[:math.floor(len(df_level) / 3 * 2)]

    # 按照近30的水平排序，留下最后8只
    df_level.sort(key=lambda x: x[2]['t30_last'], reverse=False)
    df_level = df_level[:np.min([math.floor(len(df_level) / 3 * 2), 15])]

    # 打印信息
    stk_list = [k[0] for k in df_level]

    for stk in stk_list:

        # 打印周与月信息
        send_W_M_Macd(stk_code=stk, towho=towho)

        # 打印日线信息
        df = get_k_data_JQ(stk, count=400, end_date=get_current_date_str())
        fig, _, _ = genStkPicForQQ(df)

        plt.title(str(stk))
        send_pic_qq(towho, fig)
        plt.close()

        fig, _, _ = genStkIdxPicForQQ(df)

        plt.title(str(stk))
        send_pic_qq(towho, fig)
        plt.close()


if __name__ == '__main__':

    from DataSource.auth_info import *

    # week_macd_stray_judge('603421', '影子')


    checkWeekStrayForAll()
    send_W_M_Macd('000001', '影子')

    r = calendar.weekday(2019, 12, 5)
    # week_macd_stray_judge('300508', '影子')

    checkWeekStrayForAll()

    stk_code = '600707'
    df = get_k_data_JQ(stk_code, count=600, end_date=get_current_date_str()).reset_index()

    # 规整
    df_floor = df.tail(math.floor(len(df)/20)*20-19)

    # 取均值
    df_floor['close_m5'] = df_floor['close'].rolling(window=5).mean()

    # 增加每周的星期几
    df_floor['day'] = df_floor.apply(lambda x: calendar.weekday(int(x['date'].split('-')[0]), int(x['date'].split('-')[1]), int(x['date'].split('-')[2])), axis=1)

    # 隔着5个取一个
    # df_floor_slice_5 = df_floor.loc[::5, :]
    if df_floor.tail(1)['day'].values[0] != 4:
        df_floor_slice_5 = pd.concat([df_floor[df_floor.day==4], df_floor.tail(1)], axis=0)
    else:
        df_floor_slice_5 = df_floor[df_floor.day==4]

    # 计算指标
    df_floor_slice_5['MACD'], df_floor_slice_5['MACDsignal'], df_floor_slice_5['MACDhist'] = talib.MACDEXT(df_floor_slice_5.close,
                                                                          fastperiod=6, slowperiod=12,
                                                                          signalperiod=9)

    df_floor_slice_5['MACD'] = df_floor_slice_5.apply(lambda x: 2*x['MACD'], axis=1)

    df_floor_slice_5['close_M26'] = df_floor_slice_5['close'].rolling(window=26).mean()
    df_floor_slice_5['close_M12'] = df_floor_slice_5['close'].rolling(window=12).mean()

    df_floor_slice_5['diff'] = df_floor_slice_5.apply(lambda x: x['close_M12'] - x['close_M26'], axis=1)
    df_floor_slice_5['diff_M9'] = df_floor_slice_5['diff'].rolling(window=9).mean()

    df_floor_slice_5['myMACD'] = df_floor_slice_5.apply(lambda x: 2*(x['diff'] - x['diff_M9']), axis=1)


    checkWeekStrayForAll()




    """
    画图
    df_floor_slice_5.plot('date', ['close', 'MACD', 'myMACD'], subplots=True, style=['--*', '*', '*'])
    """

    end = 0