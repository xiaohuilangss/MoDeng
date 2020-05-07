# encoding=utf-8
import tushare as ts
import numpy as np

from sdk.ExchangeFee import calExchangeFee

"""
以均线为基础改进网格

“当前价格”与“10日（可设置）均线价格”作对比，进行网格
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
amount_unit = 200

data_temp = {
    'floor_last': 0,
    'money_remain': 20000,
    'amount_remain': 1500,
    'M_last': -1,                   # 用以记录上次的均线值，在反向操作中（本次操作与上次不同的情况）使用上次均值！
    'BS_last': 'init',              # 上次是买还是卖    "buy"   "false"     "init"
    'price_last': -1                # 上次价格
}


"""
判断
"""

for idx in sh_index.index:

    # 判断是上升还是下降
    if sh_index.loc[idx, 'C-M20'] > data_temp['floor_last']:
        price_asc = True
    elif sh_index.loc[idx, 'C-M20'] < data_temp['floor_last']:
        price_asc = False
    else:
        continue

    # 求取包含的floor
    if price_asc:
        floors = list(filter(lambda x: data_temp['floor_last'] <= x <= sh_index.loc[idx, 'C-M20'], reseau))
    else:
        floors = list(filter(lambda x: sh_index.loc[idx, 'C-M20'] <= x <= data_temp['floor_last'], reseau))

    # 如果有，取出上次floor
    if data_temp['floor_last'] in floors:
        floors.remove(data_temp['floor_last'])

    if len(floors) == 0:
        print('当天当前没有触发网格！')
        continue

    # 将相对价格转换为绝对价格
    floors_abs = floors + sh_index.loc[idx, 'M20']

    if len(floors_abs) > 0:

        # -------------------- 如果是价格下降，则买入相关“floors” ----------------------
        if not price_asc:

            # stk耗费
            stk_pay = np.sum(amount_unit*floors_abs)

            # 手续费
            fee_pay = np.sum(list(map(lambda x: calExchangeFee(stk_code=stk_code, stk_amount=amount_unit, stk_price=x, buy=True), floors_abs)))

            if data_temp['money_remain'] > stk_pay + fee_pay:

                # 更新 stk数量 和 资金剩余量
                data_temp['money_remain'] = data_temp['money_remain'] - stk_pay-fee_pay
                data_temp['amount_remain'] = data_temp['amount_remain'] + len(floors_abs)*amount_unit

                # 更新最后floors
                data_temp['floor_last'] = np.min(floors)
            else:
                print('已无钱可用！')
        # -------------------- 如果是价格上升，则卖出相关“floors” ----------------------
        elif price_asc:

            # stk耗费
            stk_pay = np.sum(amount_unit * floors_abs)

            # 手续费
            fee_pay = np.sum(list(
                map(lambda x: calExchangeFee(stk_code=stk_code, stk_amount=amount_unit, stk_price=x, buy=False), floors_abs)))

            if data_temp['amount_remain'] > len(floors_abs)*amount_unit:

                # 更新 stk数量 和 资金剩余量
                data_temp['money_remain'] = data_temp['money_remain'] + stk_pay - fee_pay
                data_temp['amount_remain'] = data_temp['amount_remain'] - len(floors_abs) * amount_unit

                # 更新最后floors
                data_temp['floor_last'] = np.max(floors)
            else:
                print('已无stk可买！')
        else:
            continue
    else:
        continue

    print(str(data_temp))

    """ 记录数据用于测试 """
    sh_index.loc[idx, 'floors_abs'] = str(floors_abs)
    sh_index.loc[idx, 'floor_last'] = data_temp['floor_last']
    sh_index.loc[idx, 'buyorsale'] = {True: '卖出', False: '买入'}.get(price_asc)
    sh_index.loc[idx, 'stk_opt_amount'] = len(floors_abs)*amount_unit
    sh_index.loc[idx, 'stk_amount'] = data_temp['amount_remain']
    sh_index.loc[idx, 'money_remain'] = data_temp['money_remain']
    sh_index.loc[idx, 'money_total'] = sh_index.loc[idx, 'close']*data_temp['amount_remain']+data_temp['money_remain']

end=0