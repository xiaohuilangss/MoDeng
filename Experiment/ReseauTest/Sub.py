# encoding=utf-8
import numpy as np

from HuiCe.Sub import calExchangeFee


def BS_opt(stk_code, price, amount, opt, record_info, debug=False):
    """
    执行买卖操作的函数
    :param price:
    :param opt:
    :param record_info:
    :return:
    """
    if opt == 'buy':

        fee = calExchangeFee(stk_code=stk_code, stk_amount=amount, stk_price=price, buy=True)
        totalcost = price*amount + fee

        if record_info['money_remain'] >= totalcost:
            record_info['amount_remain'] = record_info['amount_remain'] + amount
            record_info['money_remain'] = record_info['money_remain'] - totalcost
            record_info['BS_last'] = 'buy'
            record_info['price_last'] = price
        else:
            if debug:
                print('函数 BS_opt：已无钱加仓了！')

    elif opt == 'sale':

        if record_info['amount_remain'] >= amount:
            record_info['amount_remain'] = record_info['amount_remain'] - amount
            record_info['money_remain'] = record_info['money_remain'] + price*amount - calExchangeFee(stk_code=stk_code, stk_amount=amount, stk_price=price, buy=False)
            record_info['BS_last'] = 'sale'
            record_info['price_last'] = price
        else:
            if debug:
                print('函数 BS_opt：已无stk可卖！')
    else:
        if debug:
            print('函数 BS_opt：error！不识别的操作！')

    return record_info


def SingleReseauJudge(stk_code, price_now, M_now, reseau, record_info, amount_unit, debug=False):

    """
    给定当前价格和均线，以及网格信息，进行动作判断
    :param price_now:
    :param M_now:
    :return:
    """

    """ 1、初始情况！ """
    if record_info['price_last'] == -1:
        record_info['M_last'] = M_now
        record_info['price_last'] = price_now

        return record_info

    """ 2、对比“当前价格”与“上次价格”，判断“买卖倾向” """
    if price_now > record_info['price_last']:
        record_info['BS_trend_now'] = 'sale'
    elif price_now < record_info['price_last']:
        record_info['BS_trend_now'] = 'buy'
    else:
        if debug:
            print('函数 SingleReseauJudge：与上次价格相同！')
        return record_info

    """ 3、计算有无触发网格  """
    price_rela_last = record_info['price_last'] - record_info['M_last']
    if (record_info['BS_trend_now'] == record_info['BS_last']) | (record_info['BS_last'] == 'init'):
        price_rela_now = price_now - M_now
    else:
        price_rela_now = price_now - record_info['M_last']

    # 计算包含的网格 t_3
    if record_info['BS_trend_now'] == 'buy':
        floors = list(filter(lambda x: price_rela_now <= x <= price_rela_last, reseau))

    elif record_info['BS_trend_now'] == 'sale':
        floors = list(filter(lambda x: price_rela_last <= x <= price_rela_now, reseau))

    # 如果包含，删除上次floor t_4
    if record_info['floor_last'] in floors:
        floors.remove(record_info['floor_last'])

    """ 4、判断并进行买卖操作,如果有买卖动作，同时更新“上次均线” t_5 """
    if len(floors) == 0:
        if debug:
            print('函数 SingleReseauJudge：本次未触发网格！')

        # 将本次的实际操作保存
        record_info['BS_real'] = 'NO_OPT'
        return record_info

    else:
        if record_info['BS_trend_now'] == 'buy':
            record_info = BS_opt(stk_code=stk_code, price=price_now, amount=amount_unit, opt='buy',
                                 record_info=record_info)
        else:
            record_info = BS_opt(stk_code=stk_code, price=price_now, amount=amount_unit, opt='sale',
                                 record_info=record_info)

        # 进行了买卖操作，“上次均值”应该更新！
        record_info['M_last'] = M_now

        # 将本次的实际操作保存
        record_info['BS_real'] = record_info['BS_trend_now']

    """ 5、更新floor、均值 """
    if record_info['BS_trend_now'] == 'buy':
        record_info['floor_last'] = np.min(floors)
    else:
        record_info['floor_last'] = np.max(floors)

    return record_info