# encoding=utf-8
import tushare as ts
from ReseauTest.Sub import SingleReseauJudge

"""
本脚本是网格法改进版，鉴于上一版本中，存在高买低买而导致亏钱的情况，本次进行了改进！

方法：

在当前操作与之前相同时，网格随均线进行调整，不同时则使用上次的均线值作为基准进行网格判断！

"""


stk_code = '000001'
sh_index = ts.get_k_data(code=stk_code)

sh_index['M10'] = sh_index['close'].rolling(window=10, center=False).mean()
sh_index['C-M10'] = sh_index.apply(lambda x: x['close']-x['M10'], axis=1)

sh_index['M20'] = sh_index['close'].rolling(window=20, center=False).mean()
sh_index['C-M20'] = sh_index.apply(lambda x: x['close']-x['M20'], axis=1)

sh_index = sh_index.dropna(how='any')

"""========================= 设定网格 =========================="""
reseau = [-3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3]
amount_unit = 500

record_info = {
    'floor_last': 0,
    'money_remain': 20000,
    'amount_remain': 1500,
    'M_last': -1,                   # 用以记录上次的均线值，在反向操作中（本次操作与上次不同的情况）使用上次均值！
    'BS_last': 'init',              # 上次是买还是卖    "buy"   "false"     "init"
    'price_last': -1,               # 上次价格
    'BS_trend_now': 'init'
}


for idx in sh_index.index:
    record_info = SingleReseauJudge(
        stk_code=stk_code,
        price_now=sh_index.loc[idx, 'close'],
        M_now=sh_index.loc[idx, 'M20'],
        reseau=reseau,
        record_info=record_info,
        amount_unit=amount_unit)

    # 更新对比信息
    sh_index.loc[idx, 'amount_remain'] = record_info['amount_remain']
    sh_index.loc[idx, 'money_remain'] = record_info['money_remain']
    sh_index.loc[idx, 'total_money'] = record_info['money_remain'] + record_info['amount_remain']*sh_index.loc[idx, 'close']
    sh_index.loc[idx, 'opt'] = record_info['BS_trend_now'] + ' ' + str(record_info['price_last'])

    print(str(record_info))

end = 0