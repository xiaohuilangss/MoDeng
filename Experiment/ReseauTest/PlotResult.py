# encoding=utf-8
"""
展示Reseau结果
"""
from ReseauTest.Sub import SingleReseauJudge
import tushare as ts
from pylab import *

from SDK.Normalize import normal01
from SDK.PlotOptSub import add_axis

mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False

if __name__ == '__main__':

    """ ----------------------- 准备训练数据 ------------------------------  """
    stk_code = '300508'
    sh_index = ts.get_k_data(code=stk_code, start='2014-01-01')

    sh_index['M20'] = sh_index['close'].rolling(window=5, center=False).mean()
    sh_index['C-M20'] = sh_index.apply(lambda x: x['close']-x['M20'], axis=1)

    sh_index = sh_index.dropna(how='any')

    reseau = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]
    amount_unit = 200
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

    for idx in sh_index.index:
        record_info = SingleReseauJudge(
            stk_code=stk_code,
            price_now=sh_index.loc[idx, 'close'],
            M_now=sh_index.loc[idx, 'M20'],
            reseau=reseau,
            record_info=record_info,
            amount_unit=amount_unit,
            debug=True)

        sh_index.loc[idx, 'strategy_money'] = record_info['money_remain'] + record_info['amount_remain'] * sh_index.loc[
            idx, 'close']
        sh_index.loc[idx, 'money_remain'] = record_info['money_remain']
        sh_index.loc[idx, 'BS_trend_now'] = record_info['BS_trend_now']
        sh_index.loc[idx, 'amount_remain'] = record_info['amount_remain']
        sh_index.loc[idx, 'floor_last'] = record_info['floor_last']

        sh_index.loc[idx, 'BS'] = record_info['BS_real']

        """ sh_index.loc[:, ['close', 'C-M20', 'floor_last', 'BS_trend_now', 'BS']] """

    """ -------------------------------- 图示结果 ------------------------------------ """
    # 对p进行归一化，方便比较
    ratio = sh_index.head(1)['strategy_money'].values[0]/sh_index.head(1)['close'].values[0]
    sh_index['origin_money'] = sh_index.apply(lambda x: x['close']*ratio, axis=1)

    plotOPResult(sh_index)

    fig, ax = plt.subplots(nrows=4, ncols=1)
    ax[0].plot(range(len(sh_index['date'])), sh_index['close'], 'b--')

    # 打印BS操作
    tuple_bs = list(zip(range(len(sh_index['date'])), sh_index['BS'], sh_index['close']))

    tuple_b = list(filter(lambda x: x[1] == 'buy', tuple_bs))
    ax[0].plot(list(map(lambda x: x[0], tuple_b)), list(map(lambda x: x[2], tuple_b)), 'r*', label='buy')

    tuple_s = list(filter(lambda x: x[1] == 'sale', tuple_bs))
    ax[0].plot(list(map(lambda x: x[0], tuple_s)), list(map(lambda x: x[2], tuple_s)), 'g*', label='sale')

    # 打印对比
    ax[3].plot(range(len(sh_index['date'])), sh_index['origin_money'], 'b--', label='no_use_strategy')
    ax[3].plot(range(len(sh_index['date'])), sh_index['strategy_money'], 'r--', label='use_strategy')

    # 打印stk数量和剩余money
    ax[2].plot(range(len(sh_index['date'])), normal01(sh_index['money_remain']), 'b--', label='剩余money')
    # ax[2].plot(range(len(sh_index['date'])), normal01(sh_index['amount_remain']), 'r--', label='剩余stk数量')

    # # 打印stk数量和剩余money
    ax[1].plot(range(len(sh_index['date'])), sh_index['C-M20'], 'g--', label='离心力')
    ax[1].plot(range(len(sh_index['date'])), np.zeros(len(sh_index['date'])), 'b--', label='零线')

    # 整理x轴label
    x_label = sh_index.apply(lambda x: str(x['date'])[2:].replace('-', ''), axis=1)

    ax[0] = add_axis(ax[0], x_label, 40, rotation=45, fontsize=8)
    ax[1] = add_axis(ax[1], x_label, 40, rotation=45, fontsize=8)
    ax[2] = add_axis(ax[2], x_label, 40, rotation=45, fontsize=8)
    ax[3] = add_axis(ax[3], x_label, 40, rotation=45, fontsize=8)

    for ax_sig in ax:
        ax_sig.legend(loc='best')

    plt.show()

end = 0