# encoding=utf-8

"""

"""
import calendar
import pandas as pd
import talib
from pylab import *

from Config.AutoStkConfig import plot_current_days_amount
from DataSource.Data_Sub import get_k_data_JQ, my_pro_bar
from Experiment.CornerDetectAndAutoEmail.Sub import addStkIndexToDf
from Experiment.MACD_Stray_Analysis.Demo1 import plot_W_M
from SDK.MyTimeOPT import add_date_str, get_current_date_str
from SDK.PlotOptSub import addXticklabel_list, addXticklabel


def gen_Hour_MACD_Pic(stk_code, source='jq', title=''):
    if source == 'jq':
        df_30 = get_k_data_JQ(stk_code, start_date=add_date_str(get_current_date_str(), -20), end_date=add_date_str(get_current_date_str(), 1), freq='30m')
        df_60 = get_k_data_JQ(stk_code, start_date=add_date_str(get_current_date_str(), -20), end_date=add_date_str(get_current_date_str(), 1), freq='60m')
    elif source == 'ts':
        df_30 = my_pro_bar(stk_code, start=add_date_str(get_current_date_str(), -20), freq='30min')
        df_60 = my_pro_bar(stk_code, start=add_date_str(get_current_date_str(), -20), freq='60min')

    # 去掉volume为空的行
    df_30 = df_30.loc[df_30.apply(lambda x: not (x['volume'] == 0), axis=1), :]
    df_60 = df_60.loc[df_60.apply(lambda x: not (x['volume'] == 0), axis=1), :]

    df_30['MACD'], _, _ = talib.MACD(df_30.close,
                                     fastperiod=12, slowperiod=26,
                                     signalperiod=9)

    df_60['MACD'], _, _ = talib.MACD(df_60.close,
                                     fastperiod=12, slowperiod=26,
                                     signalperiod=9)

    # 生成图片
    df_30 = df_30.dropna()
    df_60 = df_60.dropna()

    fig, ax = plt.subplots(ncols=1, nrows=4)

    ax[0].plot(range(0, len(df_30)), df_30['close'], 'g*--', label='close_30min')
    ax[1].bar(range(0, len(df_30)), df_30['MACD'], label='MACD_30min')
    ax[2].plot(range(0, len(df_60)), df_60['close'], 'g*--', label='close_60min')
    ax[3].bar(range(0, len(df_60)), df_60['MACD'], label='MACD_60min')

    # 设置下标
    ax[1] = addXticklabel_list(
        ax[1],
        list([str(x)[-11:-3] for x in df_30['datetime']]),
        30, rotation=45)

    ax[3].set_xticks(list(range(0, len(df_60['datetime']))))
    ax[3].set_xticklabels(list([str(x)[-11:-3] for x in df_60['datetime']]), rotation=45)

    for ax_sig in ax:
        ax_sig.legend(loc='best')
    plt.title(stk_code + title)
    fig.tight_layout()
    plt.subplots_adjust(wspace=0, hspace=1)  # 调整子图间距
    # plt.close()

    return fig


def gen_W_M_MACD_Pic(stk_code):
    """

    :param stk_code:
    :param towho:
    :return:
    """

    # 获取今天的情况，涨幅没有超过3%的不考虑
    # df_now = get_k_data_JQ(stk_code, count=2, end_date=get_current_date_str()).reset_index()
    #
    # if (df_now.tail(1)['close'].values[0]-df_now.head(1)['close'].values[0])/df_now.head(1)['close'].values[0] < 0.03:
    #     print('函数week_MACD_stray_judge：' + stk_code + '涨幅不够！')
    #     return False

    df = get_k_data_JQ(stk_code, count=400, end_date=get_current_date_str()).reset_index()

    if len(df) < 350:
        print('函数week_MACD_stray_judge：'+stk_code + '数据不足！')
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

    return fig


def gen_Day_Pic(stk_df, stk_code=''):
    """
    函数功能：给定stk的df，已经确定stk当前处于拐点状态，需要将当前stk的信息打印成图片，便于人工判断！
    :param stk_df           从tushare下载下来的原生df
    :param root_save_dir    配置文件中定义的存储路径
    :return:                返回生成图片的路径
    """
    """
    规划一下都画哪些图
    1、该stk整体走势，包括60日均线、20日均线和收盘价
    2、stk近几天的MACD走势
    """

    """
    在原数据的基础上增加均线和MACD
    """

    # 按升序排序
    stk_df = stk_df.sort_values(by='date', ascending=True)

    stk_df['M20'] = stk_df['close'].rolling(window=20).mean()
    stk_df['M60'] = stk_df['close'].rolling(window=60).mean()
    stk_df['MACD'], stk_df['MACDsignal'], stk_df['MACDhist'] = talib.MACD(stk_df.close,
                                                                                fastperiod=12, slowperiod=26,
                                                                                signalperiod=9)

    fig, ax = plt.subplots(nrows=4, ncols=1)

    ax[0].plot(range(0, len(stk_df['date'])), stk_df['M20'], 'b--', label='20日均线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['M60'], 'r--', label='60日均线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['close'], 'g*--', label='收盘价', linewidth=0.5, markersize=1)

    ax[1].bar(range(0, len(stk_df['date'])), stk_df['MACD'], label='MACD')

    # 准备下标
    xticklabels_all_list = list(stk_df['date'].sort_values(ascending=True))
    xticklabels_all_list = [x.replace('-', '')[2:] for x in xticklabels_all_list]

    for ax_sig in ax[0:2]:
        ax_sig = addXticklabel_list(ax_sig, xticklabels_all_list, 30, rotation=45)
        ax_sig.legend(loc='best', fontsize=5)

    # 画出最近几天的情况（均线以及MACD）
    stk_df_current = stk_df.tail(plot_current_days_amount)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['M20'], 'b--', label='20日均线', linewidth=2)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['M60'], 'r--', label='60日均线', linewidth=2)
    ax[2].plot(range(0, len(stk_df_current['date'])), stk_df_current['close'], 'g*-', label='收盘价', linewidth=1, markersize=5)
    ax[3].bar(range(0, len(stk_df_current['date'])), stk_df_current['MACD'], label='MACD')

    # 准备下标
    xticklabels_all_list = list(stk_df_current['date'].sort_values(ascending=True))
    xticklabels_all_list = [x.replace('-', '')[2:] for x in xticklabels_all_list]

    for ax_sig in ax[2:4]:
        ax_sig = addXticklabel_list(ax_sig, xticklabels_all_list, 30, rotation=45)
        ax_sig.legend(loc='best', fontsize=5)

    fig.tight_layout()                          # 调整整体空白
    plt.subplots_adjust(wspace=0, hspace=1)     # 调整子图间距

    # 检查日级别的MACD是否有异常
    attention = False
    MACD_list = stk_df_current.tail(3)['MACD'].values

    if MACD_list[1] == np.min(MACD_list):
        plt.title(stk_code + '日级别 MACD 见底了！')
        attention = True
    elif MACD_list[1] == np.max(MACD_list):
        plt.title(stk_code + '日级别 MACD 到顶了！')
        attention = True

    return fig, ax, attention


def gen_Idx_Pic(stk_df, stk_code=''):
    """
    打印常用指标
    """
    # 按升序排序
    stk_df = stk_df.sort_values(by='date', ascending=True)

    """
    增加指标

    'RSI5', 'RSI12', 'RSI30'
    'SAR'
    'slowk', 'slowd'
    'upper', 'middle', 'lower' 
    'MOM'
    """
    stk_df = addStkIndexToDf(stk_df).tail(60)

    fig, ax = plt.subplots(nrows=5, ncols=1)

    ax[0].plot(range(0, len(stk_df['date'])), stk_df['RSI5'], 'b--', label='RSI5线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['RSI12'], 'r--', label='RSI12线', linewidth=1)
    ax[0].plot(range(0, len(stk_df['date'])), stk_df['RSI30'], 'g*--', label='RSI30', linewidth=0.5, markersize=1)
    ax[0].plot(range(0, len(stk_df['date'])), [20 for a in range(len(stk_df['date']))], 'b--', linewidth=0.3)
    ax[0].plot(range(0, len(stk_df['date'])), [80 for a in range(len(stk_df['date']))], 'b--', linewidth=0.3)
    ax[0].set_ylim(0, 100)

    ax[1].plot(range(0, len(stk_df['date'])), stk_df['SAR'], 'r--', label='SAR', linewidth=0.5, markersize=1)
    ax[1].plot(range(0, len(stk_df['date'])), stk_df['close'], 'g*--', label='close', linewidth=0.5, markersize=1)

    ax[2].plot(range(0, len(stk_df['date'])), stk_df['slowk'], 'g*--', label='slowk', linewidth=0.5, markersize=1)
    ax[2].plot(range(0, len(stk_df['date'])), stk_df['slowd'], 'r*--', label='slowd', linewidth=0.5, markersize=1)
    ax[2].plot(range(0, len(stk_df['date'])), [20 for a in range(len(stk_df['date']))], 'b--', linewidth=0.3)
    ax[2].plot(range(0, len(stk_df['date'])), [80 for a in range(len(stk_df['date']))], 'b--', linewidth=0.3)
    ax[2].set_ylim(0, 100)

    ax[3].plot(range(0, len(stk_df['date'])), stk_df['upper'], 'r*--', label='布林上线', linewidth=0.5, markersize=1)
    ax[3].plot(range(0, len(stk_df['date'])), stk_df['middle'], 'b*--', label='布林均线', linewidth=0.5, markersize=1)
    ax[3].plot(range(0, len(stk_df['date'])), stk_df['lower'], 'g*--', label='布林下线', linewidth=0.5, markersize=1)

    ax[4].plot(range(0, len(stk_df['date'])), stk_df['MOM'], 'g*--', label='MOM', linewidth=0.5, markersize=1)

    # 准备下标
    xlabel_series = stk_df.apply(lambda x: x['date'][2:].replace('-', ''), axis=1)
    ax[0] = addXticklabel(ax[0], xlabel_series, 40, rotation=45)
    ax[1] = addXticklabel(ax[1], xlabel_series, 40, rotation=45)
    ax[2] = addXticklabel(ax[2], xlabel_series, 40, rotation=45)
    ax[3] = addXticklabel(ax[3], xlabel_series, 40, rotation=45)
    ax[4] = addXticklabel(ax[4], xlabel_series, 40, rotation=45)

    for ax_sig in ax:
        ax_sig.legend(loc='best', fontsize=5)

    fig.tight_layout()  # 调整整体空白
    plt.subplots_adjust(wspace=0, hspace=0)  # 调整子图间距

    # 检查SAR
    attention = False
    sar_tail = stk_df.tail(2)
    sar_tail['compare'] = sar_tail.apply(lambda x: x['SAR'] - x['close'], axis=1)

    if sar_tail.head(1)['compare'].values[0] * sar_tail.tail(1)['compare'].values[0] < 0:
        plt.title(stk_code + ' 注意 SAR 指标异动！')
        attention = True

    return fig, ax, attention