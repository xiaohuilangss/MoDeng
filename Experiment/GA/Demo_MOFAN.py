# encoding=utf-8

"""
莫烦的遗传算法案例代码

Visualize Genetic Algorithm to find a maximum point in a function.
Visit my tutorial website for more: https://morvanzhou.github.io/tutorials/

"""

import numpy as np
import matplotlib.pyplot as plt

from Experiment.GA import C_M, translateDNA, get_fitness, select

DNA_SIZE = 10            # DNA 长度
POP_SIZE = 100           # 种群大小
CROSS_RATE = 0.8         # mating probability (DNA crossover)
MUTATION_RATE = 0.003    # mutation probability
N_GENERATIONS = 200      # 种群代数
X_BOUND = [0, 5]         # 基因的上下限（此处应该设置为“相对price”的上下限）


def F(x): return np.sin(10*x)*x + np.cos(2*x)*x     # 本案例用遗传算法来寻找该函数的最大值


# def get_fitness(pred):
#     """
#     整理适应度，使之最小的值大于0并接近于0，方便于后面的以“适应度”为概率进行无放回的选择
#     :param pred:
#     :return:
#     """
#     return pred + 1e-3 - np.min(pred)


# # 将二进制DNA转换为小数，并约束在（0,5）之间！
# def translateDNA(pop):
#     return pop.dot(2 ** np.arange(DNA_SIZE)[::-1]) / float(2**DNA_SIZE-1) * X_BOUND[1]
#
#
# def select(pop, fitness):
#     """
#     选择适应度最高的个体
#     :param pop:         种群
#     :param fitness:     适应度
#     :return:
#     """
#
#     idx = np.random.choice(np.arange(POP_SIZE), size=POP_SIZE, replace=True,
#                            p=fitness/fitness.sum())
#     return pop[idx]


# def crossover(parent, pop, cross_rate, DNA_SIZE, POP_SIZE):
#
#     """
#     物种交配
#     :param parent:          待交配的父辈基因
#     :param pop:             原先的种群
#     :param cross_rate:      交配几率
#     :param DNA_size:
#     :param pop_size:
#     :return:
#     """
#
#     if np.random.rand() < cross_rate:
#         i_ = np.random.randint(0, POP_SIZE, size=1)                             # 从种群中选择另一个个体
#         cross_points = np.random.randint(0, 2, size=DNA_SIZE).astype(np.bool)   # 选择交叉点
#         parent[cross_points] = pop[i_, cross_points]                            # 交叉变异并产生下一代
#     return parent
#
#
# def mutate(child):
#     """
#     进行变异
#     :param child:
#     :return:
#     """
#     for point in range(DNA_SIZE):
#         if np.random.rand() < MUTATION_RATE:
#             child[point] = 1 if child[point] == 0 else 0
#     return child


pop = np.random.randint(2, size=(POP_SIZE, DNA_SIZE))   # 初始化种群的DNA

plt.ion()                                               # 画图展示
x = np.linspace(*X_BOUND, 200)
plt.plot(x, F(x))

for _ in range(N_GENERATIONS):
    F_values = F(translateDNA(pop, DNA_SIZE, X_BOUND))                     # 计算适应度的值？ compute function value by extracting DNA

    # 画图相关
    if 'sca' in globals(): sca.remove()
    sca = plt.scatter(translateDNA(pop, DNA_SIZE, X_BOUND), F_values, s=200, lw=0, c='red', alpha=0.5);  plt.pause(0.05)

    # 进行进化
    fitness = get_fitness(F_values)
    print("Most fitted DNA: ", pop[np.argmax(fitness), :])
    pop = select(pop, fitness, len(pop))
    # pop_copy = pop.copy()

    pop = C_M(pop, CROSS_RATE, DNA_SIZE, POP_SIZE, MUTATION_RATE)

    # for parent in pop:
    #     child = crossover(parent, pop_copy)
    #     child = mutate(child)
    #     parent[:] = child       # 子孙代替父辈

plt.ioff()
plt.show()