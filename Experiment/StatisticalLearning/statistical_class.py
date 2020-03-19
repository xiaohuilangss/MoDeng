# encoding=utf-8

"""
class about statistical learning
"""
import pandas_profiling

from DataSource.Data_Sub import add_stk_index_to_df
from DataSource.auth_info import jq_login
from DataSource.data_pro import cal_df_col_rank
from DataSource.stk_data_class import StkData
from pylab import *

from Experiment.BIAS.bias_class import BIAS
from SDK.PlotOptSub import add_axis

import pandas as pd


class AverageStatics(StkData):
    def __init__(self, stk_code):
        super().__init__(stk_code)
        self.down_day_data()
        
    def add_average_line(self, m):
        self.data['m_'+str(m)] = self.data['close'].rolling(window=m).mean()

    def add_average_pn(self, m):
        """
        m：mean
        pn：positive，negative
        :param m:
        :return:
        """
        self.data['m_pn_'+str(m)] = self.data.apply(lambda x: x['close']-x['m_'+str(m)] >= 0, axis=1)

    def add_pn_pot(self, m):
        """
        找出穿越m线的点
        :return:
        """
        self.data['m_pn_last_'+str(m)] = self.data['m_pn_'+str(m)].shift(1)
        self.data['pn_pot_'+str(m)] = self.data.apply(lambda x: x['m_pn_'+str(m)] != x['m_pn_last_'+str(m)], axis=1)
    
    def plot_average(self, m):
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
        
        df_p = df[df.apply(lambda x: x['m_pn_'+str(m)], axis=1)]
        df_n = df[df.apply(lambda x: not x['m_pn_' + str(m)], axis=1)]
        
        fig, ax = subplots(ncols=1, nrows=2)

        ax[0].plot(df['level_0'], df['close'], 'b*--', label='close')
        ax[0].plot(df_p['level_0'], df_p['close'], 'r*', label='close_m'+str(m)+'_p')
        ax[0].plot(df_n['level_0'], df_n['close'], 'g*', label='close_m' + str(m) + '_n')
        ax[0].legend(loc='best')
        ax[0] = add_axis(ax[0], df['datetime'], 60, fontsize=5, rotation=90)

        ax[1].bar(df['level_0'], df['MACD'])
        plt.show()

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
                
            df.loc[idx, 'm'+str(m)+'_seg_num'] = line_n
        
        # 根据分段编号进行分组，得到小段list
        seg_list = list(df.groupby(by='m'+str(m)+'_seg_num'))
        
        def seg_pro(seg):
            """
            对seg数据进行处理，总结为一个字典格式，输入的seg应该为一个df
            :param seg:
            :return:
            """
            c_list = list(seg['close'])
            return {
                'seg_length': len(seg),
                'seg_change_ratio_p': (np.max(c_list)-c_list[0])/(c_list[0]+0.0000000000001),
                'seg_change_ratio_n': (np.min(c_list)-c_list[0])/(c_list[0]+0.0000000000001),
                'bias930_rank': seg.tail(1)['bias930_rank'].values[0],
                'bias39_rank': seg.tail(1)['bias39_rank'].values[0],
                'macd_rank': seg.tail(1)['MACD_rank'].values[0],
                'seg_type': seg.tail(1)['m_pn_'+str(m)].values[0]
            }
        
        return pd.DataFrame([seg_pro(x[1]) for x in seg_list])

    def add_idx(self):
        self.data = add_stk_index_to_df(self.data)

        # 增加排名
        self.data = cal_df_col_rank(self.data, 'MACD')

        # 增加乖离度排名
        self.data = BIAS.add_bias_rank_public(self.data, span_q=3, span_s=9)
        self.data = BIAS.add_bias_rank_public(self.data, span_q=9, span_s=30)


if __name__ == '__main__':
    
    jq_login()
    self = AverageStatics('000001')
    self.down_day_data(count=1000)
    self.plot_average(20)
    df = self.splice_m_seg(20)

    pandas_profiling.ProfileReport(df)
    profile = df.profile_report(title="oil_data")
    profile.to_file(output_file="oil_data.html")

    end = 0