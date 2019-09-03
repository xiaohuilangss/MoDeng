# encoding=utf-8

"""

利用遗传算法优化网格
"""
# 定义多线程
import multiprocessing as mp
from Experiment.GA import initPop, C_M, convertPOP2Reseau, get_fitness, select
from ReseauTest.Sub import SingleReseauJudge
import tushare as ts
import numpy as np
import os
import time
from SDK.PickleSaveSub import loadP


# 定义适应度函数
def fitness(reseau, df):

    amount_unit = 500
    sh_index = df
    stk_code = '300508'
    record_info = {
        'floor_last': 0,
        'money_remain': 20000,
        'amount_remain': 1500,
        'M_last': -1,               # 用以记录上次的均线值，在反向操作中（本次操作与上次不同的情况）使用上次均值！
        'BS_last': 'init',          # 上次是买还是卖    "buy"   "false"     "init"
        'price_last': -1,           # 上次价格
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
        sh_index.loc[idx, 'total_money'] = record_info['money_remain'] + record_info['amount_remain'] * sh_index.loc[
            idx, 'close']

    return sh_index.tail(1)['total_money'].values[0]


if __name__ == '__main__':
    """ ----------------------- 准备训练数据 ------------------------------  """
    stk_code = '300508'
    sh_index = ts.get_k_data(code=stk_code)

    sh_index['M20'] = sh_index['close'].rolling(window=20, center=False).mean()
    sh_index['C-M20'] = sh_index.apply(lambda x: x['close']-x['M20'], axis=1)

    sh_index = sh_index.dropna(how='any').tail(100)

    """ --------------------- 定义 ------------------------ """
    r_bit_len = 5           # 网格二进制长度
    r_amount = 6            # 网格数量

    DNA_SIZE = r_bit_len*r_amount                                               # DNA 长度
    POP_SIZE = 100                                                              # 种群大小
    CROSS_RATE = 0.8                                                            # mating probability (DNA crossover)
    MUTATION_RATE = 0.003                                                       # mutation probability
    N_GENERATIONS = 200                                                         # 种群代数
    X_BOUND = [np.min(sh_index['C-M20'])-2, np.max(sh_index['C-M20'])+2]        # 基因的上下限（此处应该设置为“相对price”的上下限）

    # 初始化种群
    if os.path.exists('./pop_store/pop'+stk_code):
        pop = loadP('./pop_store/', 'pop'+stk_code)
    else:
        pop = initPop(POP_SIZE, r_bit_len*r_amount)
    last_fitness = []
    result_money = []
    pop_int = []

    pool = mp.Pool(processes=7)                    # 默认是有几个核就用几个，可以自己设置processes = ？

    for i in range(2000):

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

        result_money.append(np.max(pop_fitness))

    # 训练结束，找出最好的
    print('收益提高情况：'+str(result_money))
    print('最终的网格：' + str(pop_int[list(last_fitness).index(np.max(last_fitness))]))

    shelveP(pop, './pop_store/', 'pop'+stk_code)
    shelveP(pop_int[list(last_fitness).index(np.max(last_fitness))], './pop_store/', 'reseau'+stk_code)


