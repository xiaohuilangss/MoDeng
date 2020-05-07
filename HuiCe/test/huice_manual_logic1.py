# encoding=utf-8

"""
测试策略：
抓取乖离度偏差过大的交易机会

入场时机：
bias偏离到一定值，并开始回归

止盈：
1、与偏离度成比例的止盈点

止损：
1、0.2%
"""

from DataSource.auth_info import jq_login
from pylab import *

from Experiment.BIAS.bias_class import BIAS
from HuiCe.sub.huice_manual_logic_demo import HuiCe


class ManualLogic(HuiCe):
    def __init__(self, stk):
        super().__init__(stk, freq='30m')

        # 策略相关参数
        self.span_q = 5
        self.span_s = 30

        self.bias_input_threshold = 0.8     # bias偏离5块钱入场
        self.stop_earn_threshold = 1        # 赚5块钱止盈
        self.stop_loss_threshold = 4        # 赔一块钱止损

        self.bias_col_name = 'bias'+str(self.span_q)+str(self.span_s)

        self.earn = 0
        
    def hc_data_pro(self, count, freq):
        """
        根据本hc策略定制数据，进行相应的数据准备
        :return:
        """

        ml.down_minute_data(count=10000, freq=freq)

        # 加入均线，供画图使用
        self.add_mean_col('close', self.span_s)
        self.add_mean_col('close', self.span_q)

        # 增加乖离度
        self.data = BIAS.add_bias_rank_public(self.data, span_q=self.span_q, span_s=self.span_s)

        # 将乖离度下移，便于前后对比
        self.data['bias'+str(self.span_q)+str(self.span_s)+'before'] = self.data['bias'+str(self.span_q)+str(self.span_s)].shift(1)

        # 增加相关指数
        self.add_index()

    def reset_status(self):
        """
        重置状态
        :return:
        """
        self.status = 0             # 0:空闲 -1:neg 1:pos
        self.input_p_target = None
        self.input_p_real = None
        self.p_max = None

    def get_idx_data(self, idx):
        p_now = self.data.loc[idx, 'close']
        # m_diff = self.data.loc[idx, 'MACD_diff']
        # m_rank = self.data.loc[idx, 'MACD_rank']
        # m_sig_diff = self.data.loc[idx, 'MACDsignal_diff']
        # m20 = self.data.loc[idx, 'close_m20']
        bias = self.data.loc[idx, self.bias_col_name]
        bias_diff = bias - self.data.loc[idx, self.bias_col_name+'before']

        bias_rank = self.data.loc[idx, self.bias_col_name+'_rank']

        return p_now, bias_rank, bias_diff

    def input_judge(self, idx):
        """
        判断是否可以下网
        :return:
        """
        if self.status != 0:
            return
        
        # 获取当前数据
        p_now, bias, bias_diff = self.get_idx_data(idx)

        # 做多判断
        if (bias < 1-self.bias_input_threshold) & (bias_diff >= 0):
            self.opt_pos_in(idx)

        # 做空判断
        elif (bias > self.bias_input_threshold) & (bias_diff <= 0):
            self.opt_neg_in(idx)
            
    def stop_earn_judge(self, idx):
        """
        止盈判断
        :param idx:
        :return:
        """
        
        if self.status == 0:
            return

        p_now, bias, bias_diff = self.get_idx_data(idx)
        
        # 更新极值
        self.update_max_p(p_now)
        
        # 进行判断
        if self.status == 1:
            if p_now - self.input_p_real >= self.stop_earn_threshold:
                
                # opt
                self.opt_pos_out(idx)
                
                # status update
                self.log = self.log + '止盈平多 p:%s, earn:%s\n' % (str(p_now), str(p_now-self.input_p_real))
                self.earn = self.earn + p_now-self.input_p_real
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()
                
        elif self.status == -1:
            if self.input_p_real - p_now >= self.stop_earn_threshold:
                
                # opt
                self.opt_neg_out(idx)
        
                # status update
                self.log = self.log + '止盈平空 p:%s, earn:%s\n' % (
                str(p_now), str(self.input_p_real - p_now))
                self.earn = self.earn + self.input_p_real - p_now
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()
                
    def stop_loss_judge(self, idx, thd):
        
        if self.status == 0:
            return
        
        # 获取实时值
        p_now, bias, bias_diff = self.get_idx_data(idx)
        
        if self.status == 1:
            if p_now - self.input_p_real < -self.stop_loss_threshold:
                
                # opt
                self.opt_pos_loss(idx)
            
                # status update
                self.log = self.log + '止损平多 at p:%s, loss:%s\n' % (
                str(p_now), str())
                self.earn = self.earn - (self.input_p_real-p_now)
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()
    
        elif self.status == -1:
            if p_now - self.input_p_real > self.stop_loss_threshold:
                
                # opt
                self.opt_neg_loss(idx)
            
                # status update
                self.log = self.log + '止损平空 at p:%s, loss:%s\n' % (
                    str(p_now), str(p_now - self.input_p_real))
                self.earn = self.earn - (p_now - self.input_p_real)
                self.data.loc[idx, 'earn'] = self.earn
                self.reset_status()

    def execute_hc(self):
        """
        主循环
        :return:
        """

        for idx in self.data.index:

            p_now = self.data.loc[idx, 'close']

            self.input_judge(idx)
            self.stop_earn_judge_by_max(idx, p_now, self.stop_earn_threshold)
            self.stop_loss_judge_by_input(idx=idx, p_now=p_now, thd=0.25/100)
            
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
        # ax[0].plot(df['id'], df['close_m20'], 'y--', label='m20')
        
        ax[0].plot(df_b['id'], df_b['close'], 'g*', label='b', markersize=10)
        ax[0].plot(df_s['id'], df_s['close'], 'r*', label='s', markersize=10)
        
        ax[0].plot(df_b_loss['id'], df_b_loss['close'], 'g^', label='b_loss', markersize=10)
        ax[0].plot(df_s_loss['id'], df_s_loss['close'], 'r^', label='s_loss', markersize=10)

        ax[1].plot(df['id'], df[self.bias_col_name+'_rank'], 'y--', label=self.bias_col_name+'_rank')

        # ax[1].bar(df['id'], df['MACD_rank'])
        # ax[2].plot(df['id'], df['MACDsignal'], '--', label='MACDsignal')
        # ax[2].plot(df['id'], df['MACDhist'], '--', label='MACDhist')
        
        # ffill earn
        df['earn'] = df['earn'].fillna(method='ffill')
        ax[3].plot(df['id'], df['earn'], '--', label='earn')
        
        for ax_sig in ax:
            ax_sig.legend(loc='best')
        
        plt.show()


if __name__ == '__main__':
    jq_login()

    # 数据
    ml = ManualLogic('AG2006.XSGE')
    ml.hc_data_pro(count=10000, freq='1m')
    
    # 执行
    ml.execute_hc()
    
    # 打印结果
    print(ml.log)
    
    # 图示结果
    ml.plot_result()
    
    end = 0