# encoding=utf-8

""" 本脚本是用来存储一些与stk息息相关的子函数"""

from pylab import *
from DataSource.Data_Sub import get_k_data_JQ, add_stk_index_to_df
from DataSource.auth_info import jq_login, logout
from Function.GUI.GUI_main.cal_rsv_class import RSV
from Function.GUI.GUI_main.opt_record_class import OptRecord
from Function.GUI.GUI_main.reseau_judge_class import ReseauJudge
from Global_Value.file_dir import opt_record_file_url
from SDK.MyTimeOPT import minus_date_str, get_current_date_str
from SDK.Normalize import normal01
from SDK.PlotOptSub import add_axis
import pandas as pd

mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False

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

        self.amount = math.floor(money_each/start_price/100)*100

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


class RetestReseau:
    """
    与网格策略回测相关子函数的类
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
    def cal_today_ochl(df_m):
        """
    	df_m 应该包含date字段
    	:param df_m:
    	:return:
    	"""
        list_group = list(df_m.groupby('date'))
        list_group_sort = sorted(list_group, key=lambda x: x[0], reverse=False)

        today_df = list_group_sort[-1][1]

        o = today_df.head(1)['open'].values[0]
        c = today_df.tail(1)['close'].values[0]

        array = today_df.loc[:, ['open', 'close', 'high', 'low']].values
        h = np.max(array)
        l = np.min(array)

        return {
            'open': o,
            'close': c,
            'high': h,
            'low': l
        }

    def read_pcr(self):
        reseau_judge = ReseauJudge(stk_code=self.stk_code,
                                   opt_record_=OptRecord(opt_record_file_url_=opt_record_file_url,
                                                         stk_code=self.stk_code),
                                   debug=self.debug)

        reseau_judge.get_pcr()

        return reseau_judge.pcr

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
        df_day = get_k_data_JQ(self.stk_code, start_date=self.start_date, end_date=self.end_date).sort_index(ascending=True)

        if len(df_day) < self.max_days:
            if self.debug:
                print('max_days:%d day_data_length:%d minute_data_length:%d' % (self.max_days, len(df_day), len(df_m)))
            return False

        # 向day data 中 增加必要index
        self.data_day = add_stk_index_to_df(df_day).reset_index().reset_index()

        # 增加必要index
        self.data_minute = add_stk_index_to_df(df_m).reset_index().reset_index()

        logout()
        return True

    def add_reseau(self):
        """
        计算动态网格，并添加到数据当中
        :return:
        """

        if self.debug:
            print('开始增加网格信息...')

        # 想day data 中 增加必要index
        self.data_day = add_stk_index_to_df(self.data_day)

        # 增加必要index
        self.data_minute = add_stk_index_to_df(self.data_minute)

        # 最初的数天数据不进行回测，开始的部分数据因为数据量原因计算不出网格大小
        max_days = self.max_days
        i_start = self.i_start
        i = len(self.data_minute) - i_start

        # 大循环
        for idx in self.data_minute[i_start:].index:

            # 获取当天数据
            df_today = self.cal_today_ochl(self.data_minute.loc[:idx, :].tail(int(60*4/self.retest_span)))

            # 获取时间
            date = self.data_minute.loc[idx, 'date']

            # 获取该日期之前数天的数据
            df_day_data = self.data_day[self.data_day['date'] < date].tail(max_days + 2)

            # 增加今天的数据
            df_day_complete = df_day_data.append(df_today, ignore_index=True)

            # 计算rsv和波动情况
            rsv = RSV.cal_rsv_rank_sub(df_day_complete, self.rsv_span)
            reseau_object = Reseau()
            reseau = reseau_object.get_single_stk_reseau_sub(
                df_=df_day_complete,
                slow=self.reseau_slow,
                quick=self.reseau_quick)

            self.data_minute.loc[idx, 'rsv'] = rsv
            self.data_minute.loc[idx, 'reseau'] = reseau

            # 调节 buy 和 sale 的 threshold
            self.data_minute.loc[idx, 'thh_sale'] = reseau * 2 * rsv
            self.data_minute.loc[idx, 'thh_buy'] = reseau * 2 * (1 - rsv)

            if self.debug:
                i = i - 1
                print('还剩%d行' % i)

    def retest(self):
        """
        最终进行回测的主函数
        :return:
        """

        if self.debug:
            print('开始回测...')

        pcr = self.read_pcr()

        for idx in self.data_minute.loc[self.i_start:, :].index:

            p_now = self.data_minute.loc[idx, 'close']
            thh_sale = self.data_minute.loc[idx, 'thh_sale']
            thh_buy = self.data_minute.loc[idx, 'thh_buy']

            opt_result, money, stk_amount = self.judge_reseau(p_now, thh_sale, thh_buy, pcr)

            self.data_minute.loc[idx, 'opt_result'] = opt_result
            self.data_minute.loc[idx, 'money'] = money
            self.data_minute.loc[idx, 'opt_result'] = opt_result

            self.data_minute.loc[idx, 'money_total'] = money + stk_amount*p_now
            self.data_minute.loc[idx, 'stk_amount'] = stk_amount
            self.data_minute.loc[idx, 'total_earn'] = self.opt_record.opt_dict['total_earn']

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

    r = RetestReseau(stk_code='603421', retest_span=20, start_date='2019-01-01', end_date='2019-03-10', debug=True)

    # 增加动态网格
    r.add_reseau()

    # 进行回测
    r.retest()

    # 保存结果
    r.save_csv()

    # 画图展示
    r.plot()

    end = 0
