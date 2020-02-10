# encoding=utf-8

"""
本脚本用于测试代码运行效率

"""
import time

from ReseauTest.Sub import SingleReseauJudge
from ReseauTest.Sub import SingleReseauJudge
import tushare as ts
from pylab import *

from SDK.Normalize import normal01
from SDK.PlotOptSub import add_axis

import profile

if __name__ == '__main__':

    """ ----------------------- 准备训练数据 ------------------------------  """
    stk_code = '300508'
    sh_index = ts.get_k_data(code=stk_code)

    sh_index['M20'] = sh_index['close'].rolling(window=20, center=False).mean()
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

    t_s = time.time()
    r = SingleReseauJudge(
        stk_code=stk_code,
        price_now=sh_index.head(1)['close'].values[0],
        M_now=sh_index.head(1)['M20'].values[0],
        reseau=reseau,
        record_info=record_info,
        amount_unit=amount_unit)

    print('总时间：' + str(time.time() - t_s))
