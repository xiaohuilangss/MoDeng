# encoding=utf-8

""" 本脚本是用来存储一些与stk息息相关的子函数"""
from pylab import *
# from Config.GlobalSetting import g_total_stk_info_mysql
from DataSource.Data_Sub import get_k_data_JQ
from SDK.Normalize import normal01
from SDK.PlotOptSub import addXticklabel
import tushare as ts


def code2name_dict():
    """
	获取stk的code转name字典
	:return:
	"""
    df = ts.get_stock_basics().reset_index()
    return dict(df.loc[:, ['code', 'name']].to_dict(orient='split')['data'])


def get_name_by_stk_code(stk_info_df, stk_code):
    """
	g_total_stk_info_mysql[g_total_stk_info_mysql['code']=='300508']['name'].values[0]
	根据代码获取名字
	:return:
	"""
    if stk_code in ['sh', 'sz', 'cyb', 'zxb']:
        return {
            'sh': '上证指数',
            'sz': '深成指',
            'cyb': '创业板',
            'zxb': '中小板'
        }.get(stk_code)
    else:
        try:
            return stk_info_df[stk_info_df['code'] == stk_code]['name'].values[0]
        except:
            return stk_code


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

    ax[0] = addXticklabel(ax[0], x_label, 40, rotation=45, fontsize=8)
    ax[1] = addXticklabel(ax[1], x_label, 40, rotation=45, fontsize=8)
    ax[2] = addXticklabel(ax[2], x_label, 40, rotation=45, fontsize=8)
    # ax[3] = addXticklabel(ax[3], x_label, 40, rotation=45, fontsize=8)

    for ax_sig in ax:
        ax_sig.legend(loc='best')

    plt.show()


def cal_today_ochl(df_m):
    """
	df_m 应该包含date字段
	:param df_m:
	:return:
	"""
    list_group = list(df_m.groupby('date'))
    list_group_sort = sorted(list_group, key=lambda x: x[0], reverse=False)

    today_df = list_group_sort[-1][1]

    o = today_df.head(1)['open'][0]
    c = today_df.tail(1)['close'][0]

    array = today_df.loc[:, ['open', 'close', 'high', 'low']].values
    h = np.max(array)
    l = np.min(array)

    return {
        'open': o,
        'close': c,
        'high': h,
        'low': l
    }


if __name__ == '__main__':
    end = 0
