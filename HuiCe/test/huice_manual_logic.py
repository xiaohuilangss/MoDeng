# encoding=utf-8

"""
使用手工逻辑测试效果
"""
from DataSource.Data_Sub import get_RT_price
from DataSource.auth_info import jq_login
from DataSource.stk_data_class import StkData
from pylab import *

import pandas as pd


class HuiCe(StkData):
    def __init__(self, stk_code, freq):
        super().__init__(stk_code, freq=freq)

        # 状态
        self.status = 0             # 0:空闲 -1:neg 1:pos
        self.input_p_target = None
        self.input_p_real = None
        self.p_max = None

        self.log = ''

    def opt_pos_in(self, idx):
        self.data.loc[idx, 'bs'] = 'b'

        # status update
        self.input_p_real = self.data.loc[idx, 'close']
        self.status = 1
        self.p_max = self.data.loc[idx, 'close']
        self.log = self.log + '开多 p:%s\n' % str(self.input_p_real)

    def opt_neg_in(self, idx):
        self.data.loc[idx, 'bs'] = 's'

        # status update
        self.input_p_real = self.data.loc[idx, 'close']
        self.status = -1
        self.p_max = self.data.loc[idx, 'close']
        self.log = self.log + '开空 p:%s\n' % str(self.input_p_real)

    def opt_pos_out(self, idx):
        self.data.loc[idx, 'bs'] = 's'

    def opt_neg_out(self, idx):
        self.data.loc[idx, 'bs'] = 'b'

    def opt_pos_loss(self, idx):
        self.data.loc[idx, 'bs'] = 's_loss'
        
    def opt_neg_loss(self, idx):
        self.data.loc[idx, 'bs'] = 'b_loss'


class ManualLogic(HuiCe):
    def __init__(self, stk, freq):
        super().__init__(stk, freq=freq)
        
        self.earn = 0
        
    def hc_data_pro(self):
        """
        根据本hc策略定制数据，进行相应的数据准备
        :return:
        """
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
            
    def get_idx_data(self, idx):
        p_now = self.data.loc[idx, 'close']
        m_diff = self.data.loc[idx, 'MACD_diff']
        m_rank = self.data.loc[idx, 'MACD_rank']
        m_sig_diff = self.data.loc[idx, 'MACDsignal_diff']
        m20 = self.data.loc[idx, 'close_m20']
        
        return p_now, m_diff, m_rank, m_sig_diff, m20

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
            
    def stop_earn_judge(self, idx):
        
        if self.status == 0:
            return

        p_now, m_diff, m_rank, m_sig_diff, m20 = self.get_idx_data(idx)
        
        # 更新极值
        self.update_max_p(p_now)
        
        # 进行判断
        if self.status == 1:
            if (m_diff < 0) & (m_sig_diff < 0) & (p_now > self.input_p_real) & (p_now < m20):
                
                # opt
                self.opt_pos_out(idx)
                
                # status update
                self.log = self.log + 'Positive output at p:%s, earn:%s\n' % (str(p_now), str(p_now-self.input_p_real))
                self.earn = self.earn + p_now-self.input_p_real
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()
                
        elif self.status == -1:
            if (m_diff > 0) & (m_sig_diff > 0) & (p_now < self.input_p_real) & (p_now > m20):
                
                # opt
                self.opt_neg_out(idx)
        
                # status update
                self.log = self.log + 'Negative output at p:%s, earn:%s\n' % (
                str(p_now), str(self.input_p_real - p_now))
                self.earn = self.earn + self.input_p_real - p_now
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()
                
    def stop_loss_judge(self, idx, thd):
        
        if self.status == 0:
            return
        
        # 获取实时值
        p_now, m_diff, m_rank, m_sig_diff, m20 = self.get_idx_data(idx)
        
        if self.status == 1:
            if (p_now - self.input_p_real) / self.input_p_real < -thd:
                
                # opt
                self.opt_pos_loss(idx)
            
                # status update
                self.log = self.log + 'Positive output at p:%s, loss:%s\n' % (
                str(p_now), str())
                self.earn = self.earn - (self.input_p_real-p_now)
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()
    
        elif self.status == -1:
            if (p_now - self.input_p_real) / self.input_p_real > thd:
                
                # opt
                self.opt_neg_loss(idx)
            
                # status update
                self.log = self.log + 'Negative output at p:%s, loss:%s\n' % (
                    str(p_now), str(p_now - self.input_p_real))
                self.earn = self.earn - (p_now - self.input_p_real)
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()
                
    def stop_time_line(self):
        """
        到时停止处理
        :return:
        """
        pass
    
    def execute_hc(self):
        """
        主循环
        :return:
        """

        for idx in self.data.index:
            self.input_judge(idx)
            self.stop_earn_judge(idx)
            self.stop_loss_judge(idx=idx, thd=0.25/100)
            
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