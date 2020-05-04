# encoding=utf-8

""" 本脚本是用来存储一些与stk息息相关的子函数 """

from pylab import *
from DataSource.Data_Sub import get_k_data_JQ, add_stk_index_to_df
from DataSource.auth_info import jq_login, logout
from Experiment.BIAS.bias_class import BIAS
from HuiCe.sub.retest_sub import OptRecordRetest
from SDK.MyTimeOPT import minus_date_str, get_current_date_str
from SDK.PlotOptSub import add_axis
import pandas as pd


mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

"""
对思路进行回测的模板，复制一份这个文件，在这上面针对自己的策略进行修改便可！
"""


class OptInDay:
    """
    日内策略回测
    """

    def __init__(self, stk_code, retest_span, start_date, end_date=get_current_date_str(), reseau_quick=3, reseau_slow=6, rsv_span=4, debug=False):
        """

        :param stk_code:
        :param retest_span:
        :param start_date:
        :param end_date:
        :param reseau_quick:
        :param reseau_slow:
        :param rsv_span:
        :param debug:

        用法举例：
        r = RetestReseau(stk_code='601398', retest_span=5, start_date='2019-01-01', end_date='2019-03-10', debug=True)

        # 增加动态网格
        r.add_reseau()

        # 进行回测
        r.retest()

        # 保存结果（可选）
        r.save_csv()

        # 画图展示
        r.plot()
        """
        self.start_date = start_date
        self.end_date = end_date
        self.stk_code = stk_code
        self.debug = debug
        self.retest_span = retest_span      # 回测精度，单位为分钟
        self.days = minus_date_str(end_date, start_date)                    # 回测周期

        # 计算网格用的相关参数
        self.reseau_slow = reseau_slow
        self.reseau_quick = reseau_quick
        self.rsv_span = rsv_span

        # 计算起始时因为计算指标而无法回测的数据长度
        self.max_days = np.max([self.reseau_slow, self.rsv_span])
        self.i_start = int((self.max_days + 2) * 60 * 4 / self.retest_span)

        self.data_day = pd.DataFrame()
        self.data_minute = pd.DataFrame()

        if self.days < self.max_days:
            exit('设置天数小于最小天数！')

        if not self.prepare_data():
            exit('数据初始化失败！')

        self.opt_record = OptRecordRetest(
            money=50000,
            ratio=0.5,
            start_price=self.data_minute.head(1)['close'].values[0], money_each=5000)

    @staticmethod
    def judge(reseau, rsv, current_price, stk_price_last, min_reseau, sar_diff, sar_diff_day):

        # 实时计算价差，用于“波动提示”和“最小网格限制”
        price_diff = current_price - stk_price_last
        price_diff_ratio = price_diff / stk_price_last

        # 调节 buy 和 sale 的 threshold
        thh_sale = reseau * 2 * rsv
        thh_buy = reseau * 2 * (1 - rsv)

        if math.fabs((current_price - stk_price_last) / stk_price_last) < min_reseau:
            return 0, '未触及reseau'
        elif (sar_diff >= 0) & (sar_diff_day >= 0) & ((current_price - stk_price_last) / stk_price_last > min_reseau):
            return 1, 'sale'
        elif (sar_diff <= 0) & (sar_diff_day <= 0) & ((current_price - stk_price_last) / stk_price_last < -min_reseau):
            return 2, 'buy'
        else:
            return -1, 'no opt'

    def judge_reseau(self, p_now, thh_sale, thh_buy, pcr):

        thh_sale = np.max([thh_sale, p_now*pcr])
        thh_buy = np.max([thh_buy, p_now*pcr])

        # 判断是否可以卖出
        if pd.isnull(self.opt_record.get_min_buy_p()):
            if (p_now - self.opt_record.get_last_p()) > thh_sale:
                if self.debug:
                    print('p_now:%0.3f p_last:%0.3f p_min:%s thh_sale:%0.3f' % (p_now, self.opt_record.get_last_p(), str(self.opt_record.get_min_buy_p()), thh_sale))
                if self.opt_record.opt_s(p_now):
                    return 'sale', self.opt_record.money, self.opt_record.stk_amount
                else:
                    return 'sale-fail', self.opt_record.money, self.opt_record.stk_amount
        else:
            if p_now - self.opt_record.get_min_buy_p() > thh_sale:
                if self.debug:
                    print('p_now:%0.3f p_last:%0.3f p_min:%s thh_sale:%0.3f' % (p_now, self.opt_record.get_last_p(), str(self.opt_record.get_min_buy_p()), thh_sale))
                if self.opt_record.opt_s(p_now):
                    return 'sale', self.opt_record.money, self.opt_record.stk_amount
                else:
                    return 'sale-fail', self.opt_record.money, self.opt_record.stk_amount

        # 判断是否可以买入
        if self.opt_record.get_last_p() - p_now > thh_buy:
            if self.opt_record.opt_b(p_now):
                if self.debug:
                    print('p_now:%0.3f p_last:%0.3f p_min:%s thh_buy:%0.3f' % (
                        p_now, self.opt_record.get_last_p(), str(self.opt_record.get_min_buy_p()), thh_buy))

                return 'buy', self.opt_record.money, self.opt_record.stk_amount
            else:
                return 'buy-fail', self.opt_record.money, self.opt_record.stk_amount
        else:
            return 'no-opt', self.opt_record.money, self.opt_record.stk_amount

    def prepare_data(self):
        """
        准备数据
        :return:
        """
        if self.debug:
            print('开始准备数据...')

        jq_login()

        # 准备数据
        df_m = get_k_data_JQ(self.stk_code, start_date=self.start_date, end_date=self.end_date, freq=str(self.retest_span) + 'm')
        df_m['date'] = df_m.apply(lambda x: str(x['datetime'])[:10], axis=1)

        # 增加必要index
        # self.data_minute = add_stk_index_to_df(df_m).reset_index().reset_index()

        # 增加乖离度
        df_m = BIAS.add_bias_rank_public(df=df_m, span_q=5, span_s=30)

        self.data_minute = df_m

        logout()
        return True

    def retest(self):
        """
        最终进行回测的主函数
        :return:
        """

        if self.debug:
            print('开始回测...')

        pcr = self.read_pcr()

        # 根据仓位对网格进行二次处理逻辑
        hold_ratio = 0.5                                                    # 初始仓位0.5

        for idx in self.data_minute.loc[self.i_start:, :].index:

            # 根据仓位对网格进行加权
            hold_ratio_buy = hold_ratio / ((1 - hold_ratio) + 1e-20)  # 买入加权
            hold_ratio_sale = (1 - hold_ratio) / (hold_ratio + 1e-20)  # 买入加权

            p_now = self.data_minute.loc[idx, 'close']
            thh_sale = self.data_minute.loc[idx, 'thh_sale'] * hold_ratio_sale
            thh_buy = self.data_minute.loc[idx, 'thh_buy'] * hold_ratio_buy

            opt_result, money, stk_amount = self.judge_reseau(p_now, thh_sale, thh_buy, pcr)

            self.data_minute.loc[idx, 'opt_result'] = opt_result
            self.data_minute.loc[idx, 'money'] = money
            self.data_minute.loc[idx, 'opt_result'] = opt_result

            self.data_minute.loc[idx, 'money_total'] = money + stk_amount*p_now
            self.data_minute.loc[idx, 'stk_amount'] = stk_amount
            self.data_minute.loc[idx, 'total_earn'] = self.opt_record.opt_dict['total_earn']

            # 记录仓位以及根据仓位修正后的买卖网格大小
            self.data_minute.loc[idx, 'hold_ratio'] = hold_ratio
            self.data_minute.loc[idx, 'thh_sale_modify'] = thh_sale
            self.data_minute.loc[idx, 'thh_buy_modify'] = thh_buy

            # 更新仓位
            hold_ratio = stk_amount*p_now/(money + stk_amount*p_now)

    def save_csv(self):
        if self.debug:
            print('开始保存结果为csv...')
        self.data_minute.to_csv('./temp_data/' + self.stk_code + 'huice.csv')

    def plot(self):
        if self.debug:
            print('开始可视化结果...')

        df = self.data_minute.dropna().reset_index(drop=True)
        df['stk_money_ratio'] = df.apply(lambda x: x['stk_amount']*x['close']/(x['money_total']), axis=1)

        # 筛选买卖点
        df_b = df[df['opt_result'] == 'buy']
        df_s = df[df['opt_result'] == 'sale']

        df_opt = df[df.apply(lambda x: (x['opt_result'] == 'buy') | (x['opt_result'] == 'sale'), axis=1)]

        fig, ax = plt.subplots(ncols=1, nrows=4)

        ax[0].plot(df.index, df['close'], 'k*--', label='收盘价')
        ax[0].plot(df_opt.index, df_opt['close'], 'y-', label=u'买卖阶梯', linewidth=2.5)

        ax[0].plot(df_b.index, df_b['close'], 'g*', label='买入点', markersize=10)
        ax[0].plot(df_s.index, df_s['close'], 'r*', label='卖出点', markersize=10)

        # ax[0].legend(loc='best')

        # 展示收益比
        c_origin = np.array(df['close'])
        ratio_origin = list((c_origin/c_origin[0]))

        c_reseau = np.array(df['money_total'])
        ratio_reseau = list((c_reseau/c_reseau[0]))

        ax[1].plot(df.index, ratio_origin, 'y--', label=u'不操作收益曲线')
        ax[1].plot(df.index, ratio_reseau, 'r--', label=u'网格收益曲线')
        # ax[1].legend(loc='best')

        ax[2].plot(df.index, df['stk_money_ratio'], 'b--', label=u'仓位')
        # ax[2].legend(loc='best')

        ax[3].plot(df.index, df['total_earn'], 'b--', label=u'网格收益')

        # 增加横轴
        ax[3] = add_axis(ax[3], df['date'], 20, 8)

        for ax_ in ax:
            ax_.legend(loc='best')

        plt.show()


if __name__ == '__main__':

    r = RetestReseau(stk_code='AG2006.XSGE', retest_span=60*4, start_date='2019-05-01', end_date='2019-08-10', debug=True)

    # 增加动态网格
    r.add_reseau()

    # 进行回测
    r.retest()

    # 保存结果
    r.save_csv()

    # 画图展示
    r.plot()

    end = 0
