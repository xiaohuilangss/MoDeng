# encoding=utf-8

"""
class about statistical learning
"""
from DataSource.auth_info import jq_login
from DataSource.stk_data_class import StkData
from pylab import *
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
        self.add_average_pn(m)
        df = self.data
        
        df = df.reset_index().reset_index()
        
        df_p = df[df.apply(lambda x: x['m_pn_'+str(m)], axis=1)]
        df_n = df[df.apply(lambda x: not x['m_pn_' + str(m)], axis=1)]
        
        fig, ax = subplots(ncols=1, nrows=1)

        ax.plot(df['level_0'], df['close'], 'b*--', label='close')
        ax.plot(df_p['level_0'], df_p['close'], 'r*', label='close_m'+str(m)+'_p')
        ax.plot(df_n['level_0'], df_n['close'], 'g*', label='close_m' + str(m) + '_n')
        ax.legend(loc='best')
        ax = add_axis(ax, df['datetime'], 60, fontsize=5, rotation=90)
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
        df = self.data
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
            }
        
        return pd.DataFrame([seg_pro(x[1]) for x in seg_list])


if __name__ == '__main__':
    
    jq_login()
    self = AverageStatics('000001')
    self.down_day_data(count=1000)
    self.add_average_line(20)
    m=20
    self.plot_average(20)
    end = 0