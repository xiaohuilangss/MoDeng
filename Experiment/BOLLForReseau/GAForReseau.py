# encoding=utf-8

"""

利用遗传算法优化网格
"""
# 定义多线程
import multiprocessing as mp

import talib

from Experiment.Constraint.Constraint import calBSReseau
from Experiment.GA import initPop, C_M, convertPOP2Reseau, get_fitness, select
import tushare as ts
import numpy as np
import os
import time

from SDK.MyTimeOPT import minus_date_str
from SDK.PickleSaveSub import loadP


# 定义适应度函数
from SDK.StkSub import BS_opt


def fitness(w, df):

    stk_code = '300508'
    record_info = {
        'floor_last': 0,
        'money_remain': 20000,
        'amount_remain': 1500,
        'M_last': -1,                                   # 用以记录上次的均线值，在反向操作中（本次操作与上次不同的情况）使用上次均值！
        'BS_last': 'init',                              # 上次是买还是卖    "buy"   "false"     "init"
        'price_last': df.head(1)['close'].values[0],    # 上次价格
        'BS_trend_now': 'init',
        'BS_real': 'NO_OPT',                            # 本次实际操作
        'Price_now': 12,
        'last_opt_date': '2018-12-15',
        'time_span_from_last': 1,                       # 当前距离上次操作的时间间隔
        'B_continue': 1,
        'S_continue': 1,
        'B_Reseau': -1,
        'S_Reseau': -1
    }

    origin_amount = record_info['money_remain'] / df.head(1)['close'].values[0] + record_info['amount_remain']

    # 遍历df
    for idx in df.index:

        # 取出当前date
        date_now = str(df.loc[idx, 'date'])

        df.loc[idx, 'reseau'] = (df.loc[idx, 'upper'] - df.loc[idx, 'middle']) / 5
        df.loc[idx, 'now-last'] = df.loc[idx, 'close'] - record_info['price_last']
        now_last = df.loc[idx, 'close'] - record_info['price_last']

        # 确定网格
        reseau = np.max([(df.loc[idx, 'upper'] - df.loc[idx, 'middle']), 0.5])  # 原始网格
        record_info['time_span_from_last'] = minus_date_str(date_now, record_info['last_opt_date'])

        price_now = df.loc[idx, 'close']  # 获取当前price
        ratio = record_info['money_remain'] / (
                    record_info['money_remain'] + record_info['amount_remain'] * price_now)  # 计算ratio

        # 更新本次网格
        record_info['B_Reseau'], record_info['S_Reseau'] = calBSReseau(
            reseau_origin=reseau,
            m_remain_ratio=ratio,
            time_span=record_info['time_span_from_last'],
            continus_amount_b=record_info['B_continue'],
            continus_amount_s=record_info['S_continue'],
            m_w=w[0],
            t_w=w[1],
            c_w=w[2])

        # 向上运行，触发S操作
        if df.loc[idx, 'close'] - record_info['price_last'] > record_info['S_Reseau']:
            record_info = BS_opt(
                stk_code=stk_code,
                price=df.loc[idx, 'close'],
                amount=300,
                opt='sale',
                record_info=record_info,
                debug=False,
                date=date_now)

        elif df.loc[idx, 'close'] - record_info['price_last'] < -record_info['B_Reseau']:
            record_info = BS_opt(
                stk_code=stk_code,
                price=df.loc[idx, 'close'],
                amount=400,
                opt='buy',
                record_info=record_info,
                debug=False,
                date=date_now)
        else:
            record_info['BS_real'] = 'NO_OPT'

        # 将信息填写到df中去
        df.loc[idx, 'strategy_money'] = record_info['amount_remain'] * df.loc[idx, 'close'] + record_info[
            'money_remain']
        df.loc[idx, 'origin_money'] = origin_amount * df.loc[idx, 'close']
        df.loc[idx, 'BS'] = record_info['BS_real']
        df.loc[idx, 'amount_remain'] = record_info['amount_remain']
        df.loc[idx, 'money_remain'] = record_info['money_remain']
        df.loc[idx, 'last_price'] = record_info['price_last']

        # 将实时的网格信息添加到df中
        df.loc[idx, 'B_Reseau'] = record_info['B_Reseau']
        df.loc[idx, 'S_Reseau'] = record_info['S_Reseau']

        df.loc[idx, 'total_money'] = record_info['money_remain'] + record_info['amount_remain'] * df.loc[
            idx, 'close']

    return df.tail(1)['total_money'].values[0]


if __name__ == '__main__':
    """ ----------------------- 准备训练数据 ------------------------------  """
    stk_code = '300508'
    sh_index = ts.get_k_data(code=stk_code)

    closed = sh_index['close'].values
    sh_index['upper'], sh_index['middle'], sh_index['lower'] = talib.BBANDS(closed, timeperiod=10,
                                                                              # number of non-biased standard deviations from the mean
                                                                              nbdevup=2,
                                                                              nbdevdn=2,
                                                                              # Moving average type: simple moving average here
                                                                              matype=0)

    sh_index = sh_index.dropna(how='any').tail(100)

    """ --------------------- 定义 ------------------------ """
    r_bit_len = 5           # 网格二进制长度
    r_amount = 3            # 网格数量

    DNA_SIZE = r_bit_len*r_amount                                               # DNA 长度
    POP_SIZE = 100                                                              # 种群大小
    CROSS_RATE = 0.8                                                            # mating probability (DNA crossover)
    MUTATION_RATE = 0.03                                                        # mutation probability
    N_GENERATIONS = 200                                                         # 种群代数
    X_BOUND = [0, 20]                                                           # 基因的上下限（此处应该设置为“相对price”的上下限）

    # 初始化种群
    if os.path.exists('./pop_store/pop'+stk_code):
        pop = loadP('./pop_store/', 'pop'+stk_code)
    else:
        pop = initPop(POP_SIZE, r_bit_len*r_amount)
    last_fitness = []
    result_money = []
    pop_int = []

    pool = mp.Pool(processes=3)                    # 默认是有几个核就用几个，可以自己设置processes = ？

    for i in range(200):

        t_s = time.time()

        # 基因转为网格
        pop_int = convertPOP2Reseau(pop=pop, reseau_BIT_size=r_bit_len, reseau_amount=r_amount, reseau_bound=X_BOUND)

        fitness_input = list(map(lambda x: (x, sh_index), pop_int))

        # 计算种群的适应度
        pop_fitness = pool.starmap(fitness, fitness_input)  # 可以放入可迭代对象，自动分配进程
        # pop_fitness = list(map(lambda x: fitness(x, sh_index), pop_int))

        # 调整适应度
        last_fitness = get_fitness(pop_fitness)

        # 根据适应度进行选择
        pop = select(pop, last_fitness)

        # 交叉变异
        pop = C_M(pop, CROSS_RATE, DNA_SIZE, POP_SIZE, MUTATION_RATE)

        print('本次最高的适应度为：' + str(np.max(pop_fitness)) + '   耗时：'+str(round(time.time()-t_s, 1))+'秒！')
        print('最终的网格：' + str(pop_int[list(last_fitness).index(np.max(last_fitness))]))

        result_money.append(np.max(pop_fitness))

    # 训练结束，找出最好的
    print('收益提高情况：'+str(result_money))
    print('最终的网格：' + str(pop_int[list(last_fitness).index(np.max(last_fitness))]))

    shelveP(pop, './pop_store/', 'pop'+stk_code)
    shelveP(pop_int[list(last_fitness).index(np.max(last_fitness))], './pop_store/', 'reseau'+stk_code)


