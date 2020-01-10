# encoding=utf-8
import matplotlib
matplotlib.use('Agg')

import calendar
import multiprocessing
import talib
import pandas as pd
import tushare as ts
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from DataSource.Code2Name import code2name
from DataSource.Data_Sub import get_k_data_JQ
from DataSource.auth_info import jq_login, logout
from Experiment.CornerDetectAndAutoEmail.Sub import genStkIdxPicForQQ, genStkPicForQQ
from Function.SeaSelect.Sub.reportlab_sub import add_front, print_k_to_pdf, add_tail_page
from Function.SeaSelect.gen_pic import gen_stk_sea_select_pic
from SDK.Gen_Stk_Pic_Sub import gen_hour_macd_values, gen_half_hour_sar

from SDK.SendMsgByQQ.QQGUI import send_qq
from SDK.SendMsgByQQ.SendPicByQQ import send_pic_qq

from pylab import *
from SDK.MyTimeOPT import get_current_date_str, add_date_str


def download_stk_list_day_data(stk_list, days=None):
    """
    给定stk_list,下载日期数据,以tuple的形式返回
    :return:
    """

    jq_login()
    stk_list_data = [(x, get_k_data_JQ(x,count=days)) for x in stk_list]
    stk_list_data = list(filter(lambda x: not x[1].empty, stk_list_data))
    logout()

    return stk_list_data


def download_stk_list_hour_data(stk_list):
    """
    给定stk_list,下载半小时数据,以tuple的形式返回
    :return:
    """

    jq_login()
    stk_list_data = [(x, get_k_data_JQ(x, count=120,
                              end_date=add_date_str(get_current_date_str(), 1), freq='30m')) for x in stk_list]

    # 清除空值
    stk_list_data = list(filter(lambda x: not x[1].empty, stk_list_data))

    logout()

    return stk_list_data


def judge_rsi_sub(df, span, threshold):
    """
    根据rsi来筛选股票
    :param 包含rsi的df数据
    :param span: 5， 12， 30三种选择
    :param threshold:[0.1, 0.3]  rsi所在区间
    :return:
    """
    try:
        # 增加rsi指数
        rsi_str = 'RSI' + str(span)
        df[rsi_str] = talib.RSI(df.close, timeperiod=span)

        # 判断是否符合标准
        rsi_now = df.tail(1)[rsi_str].values[0]
        if (rsi_now >= threshold[0]) & (rsi_now <= threshold[1]):
            return True
        else:
            return False
    except Exception as e:
        print('函数judge_rsi_sub：出错！\n' + str(e))
        return False


def judge_rsi(stk_data_list, span, threshold):
    """

    :return:
    """
    stk_result_list = [(x[0], judge_rsi_sub(x[1], span, threshold)) for x in stk_data_list]

    return [r[0] for r in list(filter(lambda x: x[1], stk_result_list))]


def week_macd_judge(stk_data_list):
    """
    输入[（股票代码，day数据）,...]，返回周线macd属于转折的股票list
    之所以要封装到一个函数中，是因为在多进程中需要一个函数来完成
    :param stk_data_list:
    :return:
    """

    stk_result_list = [(x[0], week_macd_judge_sub(x[1], x[0])) for x in stk_data_list]

    return [r[0] for r in list(filter(lambda x: x[1], stk_result_list))]


def hour_sar_judge(stk_data_list):
    """
    筛选小时SAR反转的股票
    :param stk_data_list:
    :return:
    """
    stk_result_list = [(x[0], sar_stray_judge_sub(gen_half_hour_sar(x[1]))) for x in stk_data_list]
    return [r[0] for r in list(filter(lambda x: x[1] == 1, stk_result_list))]


def week_macd_judge_sub(df_day, stk_code='', debug=False):
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
        df_week = get_week_month_index_data_sub(df_day, stk_code='')[0]

        # 判断周线转折
        return macd_stray_judge_sub(df_week, debug_plot=False)

    except Exception as e:
        print('周反转判断失败，原因：\n' + str(e))
        return False


def get_week_month_index_data_sub(df_stk, stk_code=''):
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


def sar_stray_judge_sub(df_stk, debug=False):
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


def macd_stray_judge_sub(df_week, debug_plot=False):

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


def cal_level_sub(c):
    """
    计算一个序列数据，最后一个数在当前序列中的水平
    :param p_array:
    :return:
    """
    # 进行归一化
    c = (c - np.min(c)) / (np.max(c) - np.min(c))

    return c[-1]


def cal_stk_p_level_sub(c):
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

    df_total = ts.get_stock_basics()[2000:]

    # 过滤掉年龄小于四岁的
    df_stk = df_total[df_total.apply(lambda x: int(str(x['timeToMarket'])[:4]) <= int(get_current_date_str()[:4])-4, axis=1)]
    print('已过滤掉上市小于4年的股票！')
    stk_list = list(df_stk.index)

    """ --------------------------------- 根据日线rsi筛选数据 ------------------------------- """
    tic = time.time()
    stk_day_data = download_stk_list_day_data(stk_list, days=400)
    print('已下载day数据！耗时%0.2f分钟' % ((time.time()-tic)/60))

    tic = time.time()
    pool = multiprocessing.Pool(4)
    stk_list = pool.apply_async(judge_rsi, (stk_day_data, 5, [0, 30],)).get()
    pool.close()
    pool.join()
    print('已过符合RSI条件的股票！耗时%0.2f分钟' % ((time.time()-tic)/60) + '\n筛选结果为：\n' + str(stk_list))


    """ --------------------------------- 半小时sar反转的股票 ------------------------------- """

    # 下载半小时数据
    tic = time.time()
    stk_hour_data = download_stk_list_hour_data(stk_list)
    print('已下载完小时数据！耗时%0.2f分钟' % ((time.time()-tic)/60.0))

    tic = time.time()
    pool = multiprocessing.Pool(4)
    stk_list = pool.apply_async(hour_sar_judge, (stk_hour_data,)).get()
    pool.close()
    pool.join()
    print('已过滤出半小时sar转折的股票！耗时%0.2f分钟' % ((time.time()-tic)/60))

    """ --------------------------------- 根据week反转情况进行过滤，保留有反转的股票 ------------------------------- """
    # tic = time.time()
    # stk_day_data = download_stk_list_day_data(stk_list, days=300)
    # print('已下载day数据！耗时%0.2f分钟' % ((time.time()-tic)/60))
    #
    # tic = time.time()
    # pool = multiprocessing.Pool(4)
    # stk_list = pool.apply_async(week_macd_judge, (stk_day_data,)).get()
    # pool.close()
    # pool.join()
    # print('已过滤出周线macd转折的股票！耗时%0.2f分钟' % ((time.time()-tic)/60))

    print('最终筛选的股票为：' + str(stk_list))

    for stk in stk_list:

        # 将选定的股票的走势图打印到本地
        gen_stk_sea_select_pic(stk)

    print('开始生成pdf...')

    # 生成pdf
    c = canvas.Canvas(U"魔灯海选" + get_current_date_str() + ".pdf", pagesize=letter)
    c = add_front(c, '魔灯每日股票海选结果' + get_current_date_str(), '本文档由免费开源的量化投资软件“魔灯”自动生成 末尾公众号内有软件介绍', pagesize=letter)
    for stk in stk_list:
        c = print_k_to_pdf(c, stk, get_current_date_str())
    c = add_tail_page(c)
    c.save()


if __name__ == '__main__':



    sea_select()

    stk_list = ['601318', '600027', '600961', '002410', '002172', '000959', '000766', '601633', '300136', '600557', '002724', '603008', '300499', '002581', '300300']
    # for stk in stk_list:
    #
    #     # 将选定的股票的走势图打印到本地
    #     gen_stk_sea_select_pic(stk)
    #
    # print('开始生成pdf...')

    # 生成pdf
    c = canvas.Canvas(U"魔灯海选" + get_current_date_str() + ".pdf", pagesize=letter)
    c = add_front(c, '魔灯每日股票海选结果' + get_current_date_str(), '本文档由免费开源的量化投资软件“魔灯”自动生成 末尾公众号内有软件介绍', pagesize=letter)
    for stk in stk_list:
        c = print_k_to_pdf(c, stk, get_current_date_str())
    c = add_tail_page(c)
    c.save()

    df = ts.get_stock_basics()

    end = 0