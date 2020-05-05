# encoding=utf-8

""" 本脚本是用来存储一些与stk息息相关的子函数 """

from pylab import *
from DataSource.Data_Sub import get_k_data_JQ, add_stk_index_to_df
from DataSource.auth_info import jq_login, logout
from Function.GUI.GUI_main.cal_rsv_class import RSV
from Function.GUI.GUI_main.opt_record_class import OptRecord
from Function.GUI.GUI_main.reseau_judge_class import ReseauJudge
from Global_Value.file_dir import opt_record_file_url
from SDK.MyTimeOPT import minus_date_str, get_current_date_str
from SDK.Normalize import normal01
from SDK.ParallelCalculateForDf.parallel_calculate_for_df import ParallelCalculateDf
from SDK.PlotOptSub import add_axis
import pandas as pd
import copy
from SDK.TimeAndSeconds import minute_reckon_print

mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

from SDK.StdForReseau.Sub import Reseau


def bs_opt(stk_code, price, amount, opt, record_info, date, debug=False):
    """
	record_info 格式范例如下：

		record_info = {
		'floor_last': 0,
		'money_remain': 20000,
		'amount_remain': 1500,
		'M_last': -1,               # 用以记录上次的均线值，在反向操作中（本次操作与上次不同的情况）使用上次均值！
		'BS_last': 'init',          # 上次是买还是卖    "buy"   "false"     "init"
		'price_last': -1,           # 上次价格
		'BS_trend_now': 'init',
		'BS_real': 'NO_OPT'         # 本次实际操作
	}

	执行买卖操作的函数
	:param price:
	:param opt:
	:param record_info:
	:param date :           用来计算前后两次操作的间隔
	:return:
	"""
    if opt == 'buy':

        fee = cal_exchange_fee(stk_code=stk_code, stk_amount=amount, stk_price=price, buy=True)
        totalcost = price * amount + fee

        if record_info['money_remain'] >= totalcost:
            record_info['amount_remain'] = record_info['amount_remain'] + amount
            record_info['money_remain'] = record_info['money_remain'] - totalcost
            record_info['BS_last'] = 'buy'
            record_info['BS_real'] = 'buy'
            record_info['price_last'] = price

            # 更新“上次操作日期”、“连续次数”
            record_info['last_opt_date'] = date
            record_info['B_continue'] = record_info['B_continue'] + 1
            record_info['S_continue'] = 1
        else:
            record_info['BS_real'] = 'NO_OPT'
            if debug:
                print('函数 BS_opt：已无钱加仓了！')

    elif opt == 'sale':

        if record_info['amount_remain'] >= amount:
            record_info['amount_remain'] = record_info['amount_remain'] - amount
            record_info['money_remain'] = record_info['money_remain'] + price * amount - cal_exchange_fee(
                stk_code=stk_code, stk_amount=amount, stk_price=price, buy=False)
            record_info['BS_last'] = 'sale'
            record_info['BS_real'] = 'sale'
            record_info['price_last'] = price

            # 更新BS操作的连续次数
            record_info['last_opt_date'] = date
            record_info['B_continue'] = 1
            record_info['S_continue'] = record_info['S_continue'] + 1

        else:
            record_info['BS_real'] = 'NO_OPT'
            if debug:
                print('函数 BS_opt：已无stk可卖！')
    else:
        if debug:
            print('函数 BS_opt：error！不识别的操作！')

    return record_info


def which_market_stk_in(stk_code):
    """
	判断是沪市还是深市
	:param stk_code:
	:return: sh，sz

			不识别的stk代码返回空字符串
	"""

    if stk_code[0:2] == '60':
        return 'sh'

    elif stk_code[0:2] == '00' or stk_code[0:3] == '300':
        return 'sz'

    else:
        print('函数 WhichMarketStkIn：不识别的stk代码：' + stk_code)
        return ''


def cal_exchange_fee(stk_code, stk_amount, stk_price, buy=True, commissionRatio=0.00025, stampTaxRatio=0.001,
                     debug=False):
    """
	计算每笔交易的费用
	:param stk_code:
	:param stk_amount:
	:param stk_price:
	:return:
	"""

    # 计算当前交易总价格
    price_total = stk_amount * stk_price

    site = which_market_stk_in(stk_code)

    if site == '':
        if debug:
            print('函数 calExchangeFee：无法识别stk所在交易所！')
        return -1

    # 过户费 上交所每1000股收费1元
    transferFee = math.ceil(stk_amount / 1000) * 1

    # 佣金
    commission = stk_amount * stk_price * commissionRatio

    if commission < 5:
        commission = 5

    # 印花税
    stampTax = stk_amount * stk_price * stampTaxRatio

    # -------------------------------------------- 买入时 ----------------------------------------
    if buy:
        if site == 'sh':
            if debug:
                print('函数 calExchangeFee：' + '\n' +
                      # '交易stk：'+getNameByStkCode(g_total_stk_info_mysql, stk_code)+'\n'+
                      '所在交易所：' + {'sh': '上交所', 'sz': '深交所'}.get(site) + '\n' +
                      '买入卖出：' + '买入' + '\n' +
                      '印花税：' + '无' + '\n' +
                      '过户费：' + str(transferFee) + '\n' +
                      '佣金：' + str(commission) + '\n' +
                      '费用总计：' + str(transferFee + commission) + '\n')

            # 沪市买入 佣金 + 过户费
            return transferFee + commission

        else:
            if debug:
                print('函数 calExchangeFee：' + '\n' +
                      # '交易stk：'+getNameByStkCode(g_total_stk_info_mysql, stk_code)+'\n'+
                      '所在交易所：' + {'sh': '上交所', 'sz': '深交所'}.get(site) + '\n' +
                      '买入卖出：' + '买入' + '\n' +
                      '印花税：' + '无' + '\n' +
                      '过户费：' + '无' + '\n' +
                      '佣金：' + str(commission) + '\n' +
                      '费用总计：' + str(commission) + '\n')

            # 深市买入 佣金
            return commission

    # ------------------------------ 卖出时 ------------------------------------
    else:

        if site == 'sh':
            if debug:
                print('函数 calExchangeFee：' + '\n' +
                      # '交易stk：' + getNameByStkCode(g_total_stk_info_mysql, stk_code) + '\n' +
                      '所在交易所：' + {'sh': '上交所', 'sz': '深交所'}.get(site) + '\n' +
                      '买入卖出：' + '卖出' + '\n' +
                      '印花税：' + str(stampTax) + '\n' +
                      '过户费：' + str(transferFee) + '\n' +
                      '佣金：' + str(commission) + '\n' +
                      '费用总计：' + str(transferFee + commission + stampTax) + '\n')

            # 沪市卖出 佣金 + 过户费+印花税
            return transferFee + commission

        else:
            if debug:
                print('函数 calExchangeFee：' + '\n' +
                      # '交易stk：' + getNameByStkCode(g_total_stk_info_mysql, stk_code) + '\n' +
                      '所在交易所：' + {'sh': '上交所', 'sz': '深交所'}.get(site) + '\n' +
                      '买入卖出：' + '卖出' + '\n' +
                      '印花税：' + str(stampTax) + '\n' +
                      '过户费：' + '无' + '\n' +
                      '佣金：' + str(commission) + '\n' +
                      '费用总计：' + str(commission + stampTax) + '\n')

            # 深市卖出 佣金+印花税
            return commission + stampTax


def plot_op_result(df):
    """
	打印BS操作效果
	列名字：
		origin_money    ：不使用策略时的效益
		strategy_money  ：使用策略时的效益
		BS              : 记录操作行为的列
		money_remain    : 剩余的资金

	:param df:
	:return:
	"""
    sh_index = df

    fig, ax = plt.subplots(nrows=3, ncols=1)
    ax[0].plot(range(len(sh_index['date'])), sh_index['close'], 'b--')

    # 打印BS操作
    tuple_bs = list(zip(range(len(sh_index['date'])), sh_index['BS'], sh_index['close']))

    tuple_b = list(filter(lambda x: x[1] == 'buy', tuple_bs))
    ax[0].plot(list(map(lambda x: x[0], tuple_b)), list(map(lambda x: x[2], tuple_b)), 'r*', label='buy')

    tuple_s = list(filter(lambda x: x[1] == 'sale', tuple_bs))
    ax[0].plot(list(map(lambda x: x[0], tuple_s)), list(map(lambda x: x[2], tuple_s)), 'g*', label='sale')

    # 打印对比
    ax[1].plot(range(len(sh_index['date'])), sh_index['origin_money'], 'b--', label='no_use_strategy')
    ax[1].plot(range(len(sh_index['date'])), sh_index['strategy_money'], 'r--', label='use_strategy')

    # 打印stk数量和剩余money
    ax[2].plot(range(len(sh_index['date'])), normal01(sh_index['money_remain']), 'b--', label='剩余money')
    # ax[2].plot(range(len(sh_index['date'])), normal01(sh_index['amount_remain']), 'r--', label='剩余stk数量')

    # 整理x轴label
    x_label = sh_index.apply(lambda x: str(x['date'])[2:].replace('-', ''), axis=1)

    ax[0] = add_axis(ax[0], x_label, 40, rotation=45, fontsize=8)
    ax[1] = add_axis(ax[1], x_label, 40, rotation=45, fontsize=8)
    ax[2] = add_axis(ax[2], x_label, 40, rotation=45, fontsize=8)
    # ax[3] = addXticklabel(ax[3], x_label, 40, rotation=45, fontsize=8)

    for ax_sig in ax:
        ax_sig.legend(loc='best')

    plt.show()


class OptRecordRetest:
    """
    用于回测的OptRecord类
    """
    def __init__(self, money, ratio, start_price, money_each):
        """

        :param money:   本次回测初始资金
        :param ratio:   本次回测初始时，现金与股票的比例，比如“初始资金”10万，持仓市值4万，则ratio为4/10=0.4
        """

        # 用来初始化的格式
        self.ratio = ratio
        self.start_price = start_price

        # 至少买1单位（手）
        self.amount = np.max([1, math.floor(money_each/start_price/100)*100])

        self.opt_dict = {
            'b_opt': [],
            'p_last': start_price,
            'total_earn': 0,
        }
        self.init_money = money
        self.money = 0
        self.stk_amount = 0

        self.init_hold()

    def get_last_p(self):
        return self.opt_dict['p_last']

    def get_min_buy_p(self):
        if len(self.opt_dict['b_opt']) == 0:
            return None
        else:
            return np.min(self.opt_dict['b_opt'])

    def init_hold(self):
        """
        对仓位进行初始化
        :return:
        """
        self.stk_amount = math.floor(self.init_money * self.ratio/self.start_price)
        self.money = self.init_money - self.stk_amount*self.start_price

    def opt_b(self, p):
        """
        登记买入操作
        :return:
        """
        if self.money < self.amount*p:
            return False
        else:
            # 修改json记录
            self.opt_dict['b_opt'].append(p)
            self.opt_dict['p_last'] = p

            # 修改持仓和现金
            self.money = self.money - self.amount*p
            self.stk_amount = self.stk_amount + self.amount

            return True

    def opt_s(self, p):
        """
        登记卖出操作
        :param p:
        :return:
        """

        if self.stk_amount < self.amount:
            return False
        else:
            # 修改持仓和现金
            self.stk_amount = self.stk_amount - self.amount
            self.money = self.money + self.amount*p

            # 修改json记录
            self.opt_dict['p_last'] = p

            if len(self.opt_dict['b_opt']) > 0:
                self.opt_dict['total_earn'] = self.opt_dict['total_earn'] + self.amount * (p - np.min(self.opt_dict['b_opt']))
                self.opt_dict['b_opt'].remove(np.min(self.opt_dict['b_opt']))

            return True


class MyPc(ParallelCalculateDf):
    def __init__(self, df, obj):
        super().__init__(df, obj)

    @staticmethod
    def seg_process(df, seg, obj):
        def lmd(x):
            """
            重现此函数实现并行计算
            :param x:
            :return:
            """
            # 获取近日数据并计算网格
            df_day_complete = pd.DataFrame(x['ochl_days'])

            reseau_object = Reseau()
            reseau = reseau_object.get_single_stk_reseau_sub(
                df_=df_day_complete,
                slow=obj[0],
                quick=obj[1])

            print('完成1行：%s' % str(x['close']))

            return reseau

        return df.loc[seg[0]:seg[1], :].apply(lambda x: lmd(x), axis=1)





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
