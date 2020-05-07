# encoding=utf-8

"""
手工逻辑回测代码，有做空，支持期货交易
"""
from DataSource.Data_Sub import get_RT_price
from DataSource.auth_info import jq_login
from DataSource.stk_data_class import StkData
from pylab import *

import pandas as pd


class HuiCe(StkData):
    def __init__(self, stk_code, freq='1d'):
        super().__init__(stk_code, freq=freq)

        # 状态
        self.status = 0             # 0:空闲 -1:neg 1:pos
        self.input_p_target = None
        self.input_p_real = None
        self.p_max = None

        self.log = ''

    def opt_pos_in(self, idx):
        """
        开多
        :param idx:
        :return:
        """
        self.data.loc[idx, 'bs'] = 'b'

        # status update
        self.input_p_real = self.data.loc[idx, 'close']
        self.status = 1
        self.p_max = self.data.loc[idx, 'close']
        self.log = self.log + '开多 p:%s\n' % str(self.input_p_real)

    def opt_neg_in(self, idx):
        """
        开空
        :param idx:
        :return:
        """
        self.data.loc[idx, 'bs'] = 's'

        # status update
        self.input_p_real = self.data.loc[idx, 'close']
        self.status = -1
        self.p_max = self.data.loc[idx, 'close']
        self.log = self.log + '开空 p:%s\n' % str(self.input_p_real)

    def opt_pos_out(self, idx):
        """
        止盈平多
        :param idx:
        :return:
        """
        self.data.loc[idx, 'bs'] = 's'

    def opt_neg_out(self, idx):
        """
        止盈平空
        :param idx:
        :return:
        """
        self.data.loc[idx, 'bs'] = 'b'

    def opt_pos_loss(self, idx):
        """
        止损平多
        :param idx:
        :return:
        """
        self.data.loc[idx, 'bs'] = 's_loss'
        
    def opt_neg_loss(self, idx):
        """
        止损平空
        :param idx:
        :return:
        """
        self.data.loc[idx, 'bs'] = 'b_loss'

    def update_max_p(self, p_now):
        """
        更新极值
        :return:
        """
        if self.status == 0:
            return

        if (((self.status == 1) & (p_now > self.p_max)) |
                ((self.status == -1) & (p_now < self.p_max))):
            self.p_max = p_now

    def hc_data_pro(self, count, freq):
        """
        根据本hc策略定制数据，进行相应的数据准备
        :return:
        """
        ml.down_minute_data(count=10000, freq=freq)

        self.add_rank_col('MACD')
        self.cal_diff_col('MACD')
        self.cal_diff_col('MACDsignal')
        self.add_mean_col('close', 20)

    def reset_status(self):
        """
        重置状态
        :return:
        """
        self.status = 0             # 0:空闲 -1:neg 1:pos
        self.input_p_target = None
        self.input_p_real = None
        self.p_max = None

    def input_judge(self, idx):
        """
        判断是否可以下网
        :return:
        """
        if self.status != 0:
            return

        # 获取当前数据
        p_now, m_diff, m_rank, m_sig_diff, m20 = self.get_idx_data(idx)
        self.p_max = p_now

        # 正向判断
        if (m_rank < 20) & (m_diff > 0) & (m_sig_diff > 0) & (p_now > m20):

            # opt
            self.opt_pos_in(idx)

        # 反向判断
        elif (m_rank > 80) & (m_diff < 0) & (m_sig_diff < 0) & (p_now < m20):

            # opt
            self.opt_neg_in(idx)

    def stop_earn_judge_by_max(self, idx, p_now, thd):
        """
        根据极值点进行止盈，比如做多时，价格从最高点回落了0.5%，
        做空时，价格从最低点上升了0.5%
        :param idx:
        :param thd:
        :return:
        """

        if self.status == 0:
            return

        # 更新极值
        self.update_max_p(p_now)

        # 进行判断
        if self.status == 1:
            if (p_now - self.p_max)/self.p_max < -thd:

                # opt
                self.opt_pos_out(idx)

                # status update
                self.log = self.log + '做多止盈（极值法） p:%s, earn:%s\n' % (
                str(p_now), str(p_now - self.input_p_real))
                self.earn = self.earn + p_now - self.input_p_real
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()

        elif self.status == -1:
            if (p_now - self.p_max)/self.p_max >= thd:

                # opt
                self.opt_neg_out(idx)

                # status update
                self.log = self.log + '做空止盈（极值法） p:%s, earn:%s\n' % (
                    str(p_now), str(self.input_p_real - p_now))
                self.earn = self.earn + self.input_p_real - p_now
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()

    def stop_loss_judge_by_input(self, idx, p_now, thd):
        """
        根据买入点设置止损，按亏损比例进行止损
        :param idx:
        :param thd:
        :return:
        """

        if self.status == 0:
            return

        # 进行判断
        if self.status == 1:
            if (p_now - self.p_max)/self.input_p_real < -thd:

                # opt
                self.opt_pos_out(idx)

                # status update
                self.log = self.log + '做多止损（极值法） p:%s, 损失:%s\n' % (
                str(p_now), str(p_now - self.input_p_real))
                self.earn = self.earn + p_now - self.input_p_real
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()

        elif self.status == -1:
            if (p_now - self.p_max)/self.input_p_real >= thd:

                # opt
                self.opt_neg_out(idx)

                # status update
                self.log = self.log + '做空止损（极值法） p:%s, 损失:%s\n' % (
                    str(p_now), str(self.input_p_real - p_now))
                self.earn = self.earn + self.input_p_real - p_now
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()

    def execute_hc(self):
        """
        主循环
        :return:
        """

        for idx in self.data.index:
            self.input_judge(idx)
            self.stop_earn_judge(idx)
            self.stop_loss_judge(idx=idx, thd=0.25 / 100)

    def plot_result(self):
        df = self.data
        df['id'] = list(range(len(df)))

        df_b = df[df.apply(lambda x: x['bs'] == 'b', axis=1)]
        df_s = df[df.apply(lambda x: x['bs'] == 's', axis=1)]
        df_b_loss = df[df.apply(lambda x: x['bs'] == 'b_loss', axis=1)]
        df_s_loss = df[df.apply(lambda x: x['bs'] == 's_loss', axis=1)]

        # 画图展示
        fig, ax = plt.subplots(ncols=1, nrows=4, sharex='col')

        ax[0].plot(df['id'], df['close'], 'k--', label='c')
        ax[0].plot(df['id'], df['close_m20'], 'y--', label='m20')

        ax[0].plot(df_b['id'], df_b['close'], 'g*', label='b', markersize=10)
        ax[0].plot(df_s['id'], df_s['close'], 'r*', label='s', markersize=10)

        ax[0].plot(df_b_loss['id'], df_b_loss['close'], 'g^', label='b_loss', markersize=10)
        ax[0].plot(df_s_loss['id'], df_s_loss['close'], 'r^', label='s_loss', markersize=10)

        ax[0].legend(loc='best')

        ax[1].bar(df['id'], df['MACD_rank'])
        ax[2].plot(df['id'], df['MACDsignal'], '--', label='MACDsignal')
        ax[2].plot(df['id'], df['MACDhist'], '--', label='MACDhist')

        # ffill earn
        df['earn'] = df['earn'].fillna(method='ffill')
        ax[3].plot(df['id'], df['earn'], '--', label='earn')

        for ax_sig in ax:
            ax_sig.legend(loc='best')

        plt.show()


class ManualLogic(HuiCe):
    def __init__(self, stk, freq):
        super().__init__(stk, freq=freq)
        
        self.earn = 0

    def get_idx_data(self, idx):
        p_now = self.data.loc[idx, 'close']
        m_diff = self.data.loc[idx, 'MACD_diff']
        m_rank = self.data.loc[idx, 'MACD_rank']
        m_sig_diff = self.data.loc[idx, 'MACDsignal_diff']
        m20 = self.data.loc[idx, 'close_m20']
        
        return p_now, m_diff, m_rank, m_sig_diff, m20

    def stop_time_line(self):
        """
        到时停止处理
        :return:
        """
        pass
    

        
     
if __name__ == '__main__':
    jq_login()

    # 数据
    ml = ManualLogic('AG1712.XSGE', '30m')
    ml.down_minute_data(count=10000)
    ml.add_index()
    ml.hc_data_pro()
    
    # 执行
    ml.execute_hc()
    
    # 打印结果
    print(ml.log)
    
    # 图示结果
    ml.plot_result()
    
    end = 0