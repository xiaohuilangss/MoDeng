# encoding=utf-8
from sdk.DataPro import relative_rank
import numpy as np
import math


class RankNote:
    """
    在日线和半小时线的提示中增加当前价位的提示
    即当前价格处于历史何种水平
    以百分比衡量，0%表示处于给定时间段内的最低水平，100%表示处于给定时间段内的最高水平

    对于“给定时间段”
    半小时线为40天，日线为400天
    """
    def __init__(self):
        pass

    @staticmethod
    def cal_close_rank(df_):
        """
        计算排名子函数
        :param df_:
        :return:
        """

        close_history = df_['close']
        close_now = close_history.values[-1]

        return relative_rank(close_history, close_now)

    @staticmethod
    def print_day_close_rank(df_day):
        """
        打印日线排名
        :param df_day:
        :return:
        """
        len_origin = len(df_day)
        df_day = df_day.tail(400)
        return '\n近%d天内价位：%0.1f' % (int(np.min([len_origin, 400])), RankNote.cal_close_rank(df_day)) + '%'

    @staticmethod
    def print_hour_close_rank(df_hour):
        """
        打印小时线排名
        :param df_hour:
        :return:
        """
        len_origin = len(df_hour)
        df_hour = df_hour.tail(160)
        return '\n近%d天内价位：%0.1f' % (int(math.floor(np.min([len_origin, 160])/8)), RankNote.cal_close_rank(df_hour)) + '%'