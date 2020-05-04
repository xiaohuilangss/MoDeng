# encoding=utf-8
"""
本类用来实现均线策略相关的逻辑

"""
import copy
import matplotlib
from DataSource.auth_info import jq_login
from DataSource.stk_data_class import StkData
from Function.GenPic.gen_pic_class import GenPic
from pylab import *


class AverageLine(StkData):
    def __init__(self, stk_code):
        super().__init__(stk_code)

    def cal_close_ml_diff_sum(self, m, win):
        """
        计算close与给定均线的差值，并在给定的窗口期中进行求和
        :param win:
        :param m:
        :return:
        """
        data_df = copy.deepcopy(self.data)
        data_df['c_m'+str(m)+'_diff'] = data_df.apply(lambda x: x['close']-x['close'+'_m'+str(m)], axis=1)
        self.data['c_m'+str(m)+'_diff_sum'+str(win)] = data_df['c_m'+str(m)+'_diff'].rolling(window=win).sum()

    def plot(self):
        df = self.data

        df['idx'] = list(range(len(df)))
        fig, ax = plt.subplots(nrows=2, sharex=True)

        ax[0].plot(df['idx'], df['close'], 'g*--', label='close')
        ax[0].plot(df['idx'], df['SAR'], 'r-', label='sar')
        # ax[0].plot(df['idx'], df['close_m5'], 'y-', label='close')
        # ax[0].plot(df['idx'], df['close_m30'], 'r-', label='close')

        ax[1] = GenPic.plot_macd(ax[1], self.data, '')
        plt.show()


if __name__ == '__main__':
    jq_login()
    al = AverageLine('RB2010.XSGE')

    # 下载数据
    al.down_minute_data(count=2000, freq='1m')

    # 增加相关均线
    al.add_mean_col('close', 5)
    al.add_mean_col('close', 10)
    al.add_mean_col('close', 20)
    al.add_mean_col('close', 30)
    al.add_mean_col('close', 60)
    al.add_mean_col('close', 720)

    # 增加指标
    al.add_index()

    al.plot()

    # 增加对均线差和的计算
    al.cal_close_ml_diff_sum(60, 120)

    # 对均线进行排名
    al.add_rank_to_col('c_m60_diff_sum120')

    # 展示均线
    al.data['idx'] = list(range(len(al.data)))
    al.data.plot('idx', ['close', 'c_m60_diff_sum120'], subplots=True)
    al.data.plot('idx', ['close', 'close_m5', 'close_m60', 'close_m720'], style=['*--', '-', '-', '-'])
    al.data.plot('idx', ['close', 'MACD'], subplots=True)
    end = 0