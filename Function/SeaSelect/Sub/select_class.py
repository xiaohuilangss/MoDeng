# encoding=utf-8

"""
海选使用的类
"""
import calendar
import math
import talib
import pandas as pd
import numpy as np
import tushare as ts
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from DataSource.Data_Sub import get_k_data_JQ
from DataSource.auth_info import jq_login
from Function.SeaSelect.Sub.reportlab_sub import add_front, print_k_to_pdf, add_tail_page
from SDK.MyTimeOPT import add_date_str, get_current_date_str


class SeaSelect:
    def __init__(self, stk_code):

        self.stk_code = stk_code

        self.hour_data = None
        self.day_data = None
        self.week_data = None
        self.month_data = None

        self.age = None
        self.cp = None

        self.close_rank = None

    @staticmethod
    def down_basic():
        """
        从tushare中下载股票基本数据
        :return:
        """
        df = ts.get_stock_basics().reset_index()
        return dict(df.loc[:, ['code', 'timeToMarket']].to_dict(orient='split')['data'])

    def cal_age(self, code2timeToMarket):
        self.age = int(get_current_date_str()[:4]) - int(str(code2timeToMarket[self.stk_code])[:4])

    def data(self, kind):
        if kind == 'd':
            return self.day_data
        elif kind == 'h':
            return self.hour_data
        elif kind == 'w':
            return self.week_data
        elif kind == 'm':
            return self.month_data

    @staticmethod
    def down_today():
        """
        从tushare中下载当日数据
        :return:
        """
        df_today = ts.get_today_all()
        return dict(df_today.loc[:, ['code', 'changepercent']].to_dict(orient='split')['data'])

    def get_cp(self, ts_today_dict):
        try:
            self.cp = ts_today_dict[self.stk_code]
        except Exception as e_:
            print('类SeaSelect：股票'+self.stk_code + '计算当日涨跌幅出错！原因：\n' + str(e_))

    def down_hour_data(self):
        self.hour_data = get_k_data_JQ(self.stk_code, count=120,
                              end_date=add_date_str(get_current_date_str(), 1), freq='30m')

    def down_day_data(self):
        self.day_data = get_k_data_JQ(self.stk_code, count=400)

    def add_sar(self, kind):
        """
        向df中增加sar指标
        :param kind:
        :return:
        """
        self.data(kind)['SAR'] = talib.SAR(self.data(kind).high, self.data(kind).low, acceleration=0.05, maximum=0.2)

    def add_macd(self, kind):

        self.data(kind)['MACD'], self.data(kind)['MACDsignal'], self.data(kind)['MACDhist'] = talib.MACD(
            self.data(kind).close,
            fastperiod=6, slowperiod=12,
            signalperiod=9)

    def add_week_month_data(self):
        """
        给定日线数据，计算周线/月线指标！
        :return:
        """

        df = self.day_data

        if len(df) < 350:
            print('函数week_MACD_stray_judge：' + self.stk_code + '数据不足！')
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

        # 隔着20个取一个（月线）
        df_month = df_floor.loc[::20, :]

        self.week_data = df_week
        self.month_data = df_month

    def add_rsi(self, kind, span):
        df = self.data(kind)
        rsi_str = 'RSI' + str(span)
        df[rsi_str] = talib.RSI(df.close, timeperiod=span)

    def judge_rsi_sub(self, kind, span, threshold):
        """
        根据rsi来筛选股票
        :param kind:
        :param span: 5， 12， 30三种选择
        :param threshold:[0.1, 0.3]  rsi所在区间
        :return:
        """

        try:
            # 增加rsi指数
            rsi_str = 'RSI' + str(span)
            self.add_rsi(kind, span)

            df = self.data(kind)

            # 判断是否符合标准
            rsi_now = df.tail(1)[rsi_str].values[0]
            if (rsi_now >= threshold[0]) & (rsi_now <= threshold[1]):
                return True
            else:
                return False
        except Exception as e:
            print('函数judge_rsi_sub：出错！\n' + str(e))
            return False

    def sar_stray_judge_sub(self, kind):
        """
        判断sar的反转情况，返回三种值
        -1, 0， 1
        -1：向下反转
        0：未反转
        1：向上反转
        :return:
        """
        df = self.data(kind)

        try:
            df_tail = df.tail(2).reset_index()

            if (df_tail.loc[1, 'SAR'] >= df_tail.loc[1, 'close']) & (df_tail.loc[0, 'SAR'] <= df_tail.loc[0, 'close']):
                return -1
            elif (df_tail.loc[1, 'SAR'] <= df_tail.loc[1, 'close']) & (
                    df_tail.loc[0, 'SAR'] >= df_tail.loc[0, 'close']):
                return 1
            else:
                return 0
        except Exception as e:
            print('sar反转判断失败，原因：\n' + str(e))
            return 0

    def macd_stray_judge(self, kind):

        """
        对macd反转进行判断
        :return:
        """
        # 判断背离
        self.add_macd(kind)

        macd_week = self.data(kind).tail(3)['MACD'].values
        if macd_week[1] == np.min(macd_week):
            return True
        else:
            return False

    def cal_close_rank(self, kind):
        """
        计算一个序列数据，最后一个数在当前序列中的水平
        :param kind:
        :return:
        """
        c = np.array(self.data(kind)['close'])
        self.close_rank = list((c - np.min(c)) / (np.max(c) - np.min(c)))[-1]


if __name__ == '__main__':
    jq_login()

    # 下载基础数据
    df_basic = SeaSelect.down_basic()

    # 下载当天涨跌幅
    df_today = SeaSelect.down_today()

    # 创建全部股票对象
    stk_list = list(df_basic.keys())
    stk_list_ss = [SeaSelect(x) for x in stk_list]

    # 填入年龄
    [x.cal_age(df_basic) for x in stk_list_ss]

    # 删除小于4岁的孩子
    stk_list_ss = list(filter(lambda x: x.age > 4, stk_list_ss))

    # 计算增长率
    # [x.get_cp(df_today) for x in stk_list_ss]

    # 过滤掉涨幅小于4%
    # stk_list_ss = list(filter(lambda x: not pd.isnull(x.cp), stk_list_ss))
    # stk_list_ss = list(filter(lambda x: x.cp > 0.04, stk_list_ss))

    # 获取day数据
    [x.down_day_data() for x in stk_list_ss]

    # 删除数据day数据为空的单位
    stk_list_ss = list(filter(lambda x: not x.day_data.empty, stk_list_ss))

    # 计算周月数据
    [x.add_week_month_data() for x in stk_list_ss]

    # 为周数据增加macd
    [x.add_macd('w') for x in stk_list_ss]

    # 判断周反转
    stk_list_ss = list(filter(lambda x: x.macd_stray_judge('w'), stk_list_ss))

    # 计算价格排名
    [x.cal_close_rank('d') for x in stk_list_ss]

    print(str([x.stk_code for x in stk_list_ss]))

    stk_list_ss = list(sorted(stk_list_ss, key=lambda x: x.close_rank))[:6]

    stk_list = [x.stk_code for x in stk_list_ss]
    print(str(stk_list))

    c = canvas.Canvas(U"魔灯海选" + get_current_date_str() + ".pdf", pagesize=letter)
    c = add_front(c, '魔灯每日股票海选结果' + get_current_date_str(), '本文档由免费开源的量化投资软件“魔灯”自动生成 末尾公众号内有软件介绍', pagesize=letter)
    for stk in stk_list:
        c = print_k_to_pdf(c, stk, get_current_date_str())
    c = add_tail_page(c)
    c.save()

    end = 0

