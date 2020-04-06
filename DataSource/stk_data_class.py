# encoding=utf-8
import calendar

import jqdatasdk
import talib
import tushare as ts
import jqdatasdk as jq
import numpy as np
import pandas as pd
import math

from DataSource.Data_Sub import get_k_data_JQ, add_stk_index_to_df, Index
from DataSource.LocalData.update_local_data import LocalData
from DataSource.auth_info import jq_login
from DataSource.data_pro import cal_df_col_rank
from SDK.DataPro import relative_rank
from SDK.MyTimeOPT import get_current_date_str, add_date_str


class StkData:
    """
    stk数据基础类，用来准备一些基本的数据
    数据预处理所用函数皆在于此
    """
    
    def __init__(self, stk_code, freq='1d'):
        
        self.freq = freq
        self.stk_code = stk_code
        
        self.data = pd.DataFrame()
        self.data = pd.DataFrame()
        self.week_data = pd.DataFrame()
        self.month_data = pd.DataFrame()
        
        # 通用变量，便于后续功能扩展之用！
        self.general_variable = None
        
    def add_col_rank(self, col):
        """
        对某一列进行排名化
        :return:
        """
        self.data = cal_df_col_rank(self.data, col)
    
    def read_local_data(self, local_dir):
        self.data = LocalData.read_stk(local_dir=local_dir, stk_=self.stk_code).tail(40)
        
    def down_minute_data(self, count=400, freq=None):
        if pd.isnull(freq):
            self.data = get_k_data_JQ(self.stk_code, count=count,
                                      end_date=add_date_str(get_current_date_str(), 1), freq=self.freq)
        else:
            self.data = get_k_data_JQ(self.stk_code, count=count,
                                      end_date=add_date_str(get_current_date_str(), 1), freq=freq)
    
    def down_day_data(self, count=150, start_date=None, end_date=None):
        self.data = get_k_data_JQ(
            self.stk_code,
            count=count,
            start_date=start_date,
            end_date=end_date,
            freq=self.freq)
    
    def add_week_month_data(self):
        """
        给定日线数据，计算周线/月线指标！
        :return:
        """
        
        df = self.data
        
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
    
    @staticmethod
    def normal(list_):
        """
        列表归一化
        :param list_:
        :return:
        """
        
        c = list_
        return list((c - np.min(c)) / (np.max(c) - np.min(c)))
    
    @staticmethod
    def cal_rank_sig(sig, total):
        return relative_rank(total, sig)
    
    @staticmethod
    def cal_rank(list_):
        """
        计算排名
        :return:[0, 100], 排名为0表示为这个序列中的最小值，排名为100表示为这个序列的最大值
        """
        
        return [StkData.cal_rank_sig(x, list_) for x in list_]
    
    def cal_diff_col(self, col):
        df = self.data
        df[col + '_last'] = df[col].shift(1)
        self.data[col+'_diff'] = df.apply(lambda x: x[col] - x[col + '_last'], axis=1)

    def add_index(self):
        """
        向日线数据中增加常用指标
        :return:
        """
        self.data = add_stk_index_to_df(self.data)

        # 增加其他指标
        idx = Index(self.data)

        idx.add_cci(5)
        idx.add_cci(20)

        self.data = idx.stk_df

    def add_sar_diff(self):
        self.data['sar_close_diff'] = self.data.apply(lambda x: x['SAR'] - x['close'], axis=1)

    def add_kd_diff(self):
        """
        向日线数据中增加kd的差值值
        :return:
        """
        self.data['kd_diff'] = self.data.apply(lambda x: (x['slowk'] - x['slowd']), axis=1)

    def add_boll_width(self):
        """
        向日线数据中增加布林线宽度值
        :return:
        """
        self.data['boll_width'] = self.data.apply(lambda x: x['upper'] - x['lower'], axis=1)

    def add_rank_col(self, col_name):
        """
        对日线数据的某一个字段进行排名华
        :param col_name:
        :return:
        """
        self.data[col_name + '_rank'] = self.cal_rank(self.data[col_name])
        
    def add_mean_col(self, col, m):
        """
        求某一列的mean
        :param col:
        :param m:
        :return:
        """
        self.data[col+'_m'+str(m)] = self.data[col].rolling(window=m).mean()


class StkDataRT(StkData):
    """
    包含对一只股票进行实时计算的方法
    """
    def __init__(self, stk_code):
        super().__init__(stk_code)
        # 记录上次sar的状态，在close之上为True，反之为Flase，初始化为None
        self.sar_last = None

    def check_sar_status_change(self):
        """
        检查sar指标的波动情况
        :return:
        0: sar状态没有变化
        1：向上突破
        -1：向下突破
        """
        # 下载实时数据
        self.down_minute_data(count=20, freq='1m')

        # 计算sar指数
        self.data['sar'] = talib.SAR(self.data.high, self.data.low, acceleration=0.05, maximum=0.2)

        # 获取sar最新状态
        row_tail = self.data.tail(1)
        sar_status_now = row_tail['sar'].values[0] > row_tail['close'].values[0]

        if pd.isnull(self.sar_last):
            self.sar_last = sar_status_now
            return 0

        if sar_status_now != self.sar_last:
            if sar_status_now:
                return 1
            else:
                return -1
        else:
            return 0


if __name__ == '__main__':

    jq_login()
    sd = StkDataRT('300183')

    sd.down_minute_data(count=1000, freq='5m')
    sd.add_index()
    sd.data['id'] = list(range(len(sd.data)))
    sd.data.plot('id', ['close', 'SAR'], style=['*--', '*--'])

    for i in range(10):
        print(str(sd.check_sar_status_change()))
