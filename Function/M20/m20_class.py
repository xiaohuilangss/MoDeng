# encoding=utf-8
import pandas_profiling

from DataSource.Data_Sub import add_stk_index_to_df
from DataSource.auth_info import jq_login
from DataSource.data_pro import cal_df_col_rank
from DataSource.stk_data_class import StkData
from pylab import *
from Experiment.BIAS.bias_class import BIAS
from sdk.MyTimeOPT import minus_datetime_str, get_current_datetime_str
from sdk.PlotOptSub import add_axis
from DataSource.Data_Sub import get_k_data_JQ

import pandas as pd

"""
m20策略相关的类
"""

class StkAveData(StkData):
    def __init__(self, stk_code, freq='1d'):
        super().__init__(stk_code, freq)
        
    def add_average_line(self, m):
        self.data['m_' + str(m)] = self.data['close'].rolling(window=m).mean()

    def add_average_pn(self, m):
        """
        m：mean
        pn：positive，negative
        :param m:
        :return:
        """
        self.data['m_pn_' + str(m)] = self.data.apply(lambda x: x['close'] - x['m_' + str(m)] >= 0, axis=1)

    def add_pn_pot(self, m):
        """
        找出穿越m线的点
        :return:
        """
        self.data['m_pn_last_' + str(m)] = self.data['m_pn_' + str(m)].shift(1)
        self.data['pn_pot_' + str(m)] = self.data.apply(lambda x: x['m_pn_' + str(m)] != x['m_pn_last_' + str(m)],
                                                        axis=1)

    def plot_average(self, m):
        """
        图示m线概况
        :param m:
        :return:
        """
        self.add_average_line(m)
        self.add_average_pn(m)
        df = self.data
    
        df = df.reset_index().reset_index()
    
        df_p = df[df.apply(lambda x: x['m_pn_' + str(m)], axis=1)]
        df_n = df[df.apply(lambda x: not x['m_pn_' + str(m)], axis=1)]
    
        fig, ax = subplots(ncols=1, nrows=1)
    
        ax.plot(df['level_0'], df['close'], 'b*--', label='close')
        ax.plot(df_p['level_0'], df_p['close'], 'r*', label='close_m' + str(m) + '_p')
        ax.plot(df_n['level_0'], df_n['close'], 'g*', label='close_m' + str(m) + '_n')
        ax.legend(loc='best')
        ax = add_axis(ax, df['datetime'], 60, fontsize=5, rotation=90)
    
        plt.show()

    
class AverageStatics(StkAveData):
    def __init__(self, stk_code, freq='1d'):
        super().__init__(stk_code, freq=freq)
        self.down_day_data()

    def splice_m_seg(self, m):
        """
        运行该函数前提应该运行“add_average_pn及add_pn_pot”两个函数，
        使得数据中已有pn及pn转折点

        因为该函数单独生成另一种数据副本，所以中间操作不再self.data中进行，以便保持
        self.data的纯净。
        :param m:
        :return:
        """
    
        # 增加指数
        self.add_idx()
    
        # 增加20日线信息
        self.add_average_line(m)
        self.add_average_pn(m)
        self.add_pn_pot(m)
    
        # 分割线段
        df = self.data.dropna(axis=0)
        line_n = 0
        for idx in df.index:
            if df.loc[idx, 'pn_pot_' + str(m)]:
                line_n = line_n + 1
        
            df.loc[idx, 'm' + str(m) + '_seg_num'] = line_n
    
        # 根据分段编号进行分组，得到小段list
        seg_list = list(df.groupby(by='m' + str(m) + '_seg_num'))
    
        def seg_pro(seg):
            """
            对seg数据进行处理，总结为一个字典格式，输入的seg应该为一个df
            :param seg:
            :return:
            """
            c_list = list(seg['close'])
            return {
                'seg_length': len(seg),
                'seg_change_ratio_p': (np.max(c_list) - c_list[0]) / (c_list[0] + 0.0000000000001),
                'seg_change_ratio_n': (np.min(c_list) - c_list[0]) / (c_list[0] + 0.0000000000001),
                'bias930_rank': seg.tail(1)['bias930_rank'].values[0],
                'bias39_rank': seg.tail(1)['bias39_rank'].values[0],
                'macd_rank': seg.tail(1)['MACD_rank'].values[0],
                'seg_type': seg.tail(1)['m_pn_' + str(m)].values[0]
            }
    
        return pd.DataFrame([seg_pro(x[1]) for x in seg_list])
    
    def add_idx(self):
        self.data = add_stk_index_to_df(self.data)
        
        # 增加排名
        self.data = cal_df_col_rank(self.data, 'MACD')
        
        # 增加乖离度排名
        self.data = BIAS.add_bias_rank_public(self.data, span_q=3, span_s=9)
        self.data = BIAS.add_bias_rank_public(self.data, span_q=9, span_s=30)

    def plot(self, m):
        """
        图示m线概况
        :param m:
        :return:
        """
        self.add_average_line(m)
        self.add_average_pn(m)
        self.add_idx()
    
        df = self.data
    
        df = df.reset_index().reset_index()
    
        df_p = df[df.apply(lambda x: x['m_pn_' + str(m)], axis=1)]
        df_n = df[df.apply(lambda x: not x['m_pn_' + str(m)], axis=1)]
    
        fig, ax = subplots(ncols=1, nrows=2)
    
        ax[0].plot(df['level_0'], df['close'], 'b*--', label='close')
        ax[0].plot(df_p['level_0'], df_p['close'], 'r*', label='close_m' + str(m) + '_p')
        ax[0].plot(df_n['level_0'], df_n['close'], 'g*', label='close_m' + str(m) + '_n')
        ax[0].legend(loc='best')
        ax[0] = add_axis(ax[0], df['datetime'], 60, fontsize=5, rotation=90)
    
        ax[1].bar(df['level_0'], df['MACD'])
        plt.show()
        
        
class MNote(StkAveData):
    """
    均线提示类
    """
    def __init__(self, stk_code, m=20, freq='1d'):
        super().__init__(stk_code, freq)
        self.stk_code = stk_code
        self.freq = freq
        self.m = m
        self.last_result = None
    
    def last_m_pot_note(self, dt_now, dt_last, pot_type):
        """
        提示上次穿越的时间和类型
        :param pot_type:
        :param dt_now:
        :param dt_last:
        :return:
        """
        (days, minutes, secs) = minus_datetime_str(dt_now, dt_last)
        
        return '最近一次穿越M%s均线（freq=%s）的行为发生在 %d天 %d分钟 %d秒 之前，为“%s”类型' \
               %(str(self.m), self.freq, days, minutes, secs, {True:'涨破', False:'跌破'}.get(pot_type, '未知'))
        
    def get_last_m_stray(self):
        """
        找出上一次穿越m线的情况
        :return:
        """
        
        # 取出一副本，再进行drop操作
        df = self.data.dropna(axis=0)
        
        if df.empty:
            return '近期无穿越M%s均线（freq=%s）的行为' % (str(self.m), self.freq)
        
        # 取出最后一个转折点
        df_pot = df[df.apply(lambda x: x['pn_pot_' + str(self.m)], axis=1)]
        
        if df_pot.empty:
            return '近期无穿越M%s均线（freq=%s）的行为' % (str(self.m), self.freq)
        
        last_pot = df_pot.tail(1)
        self.last_result = last_pot['m_pn_' + str(self.m)].values[0]
        
        return self.last_m_pot_note(
            get_current_datetime_str(),
            last_pot['datetime'].values[0],
            last_pot['m_pn_' + str(self.m)].values[0])
    
    def cal_rt_m(self):
        """
        在非首次运行的情况下，进行实时均线状态提示
        :return:
        """
        pot_status_now = self.data.tail(1)['m_pn_' + str(self.m)].values[0]
        
    def m_rt_judge(self):
        
        # 获取均线数据
        if 'm' in self.freq:
            self.down_minute_data(count=60)
        else:
            self.down_day_data(count=60)
            
        self.add_average_pn(self.m)
        self.add_pn_pot(self.m)
        
        # 判断
        if pd.isnull(self.last_result):
            
            # 初次启动，判断上一次最近的转折
            return self.get_last_m_stray()
        
        else:
        