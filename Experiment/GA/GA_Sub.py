# encoding=utf-8
import numpy as np
"""

关于遗传算法的子函数
"""


def get_fitness(pred):
    """
    整理适应度，使之最小的值大于0并接近于0，方便于后面的以“适应度”为概率进行无放回的选择
    :param pred:
    :return:
    """
    return np.array(pred) + 1e-3 - np.min(pred)


def translateDNA(pop, DNA_SIZE, X_BOUND):
    """

    :param pop:
    :return:
    """
    return pop.dot(2 ** np.arange(DNA_SIZE)[::-1]) / float(2**DNA_SIZE-1) * X_BOUND[1]


def select(pop, fitness):
    """
    选择适应度最高的个体
    :param pop:         种群
    :param fitness:     适应度
    :return:
    """

    idx = np.random.choice(np.arange(len(pop)), size=len(pop), replace=True,
                           p=fitness/fitness.sum())
    return pop[idx]


def mySelect(pop, fitness):
    """
    选择适应度最高的个体
    :param pop:         种群
    :param fitness:     适应度
    :return:
    """

    idx = np.random.choice(np.arange(len(pop)), size=len(pop), replace=True,
                           p=fitness/fitness.sum())
    return pop[idx]


def crossover(parent, pop, cross_rate, POP_SIZE, DNA_SIZE):
    """
    物种交配
    :param parent:          待交配的父辈基因
    :param pop:             原先的种群
    :param cross_rate:      交配几率
    :param DNA_size:
    :param pop_size:
    :return:
    """

    if np.random.rand() < cross_rate:
        i_ = np.random.randint(0, POP_SIZE, size=1)  # 从种群中选择另一个个体
        cross_points = np.random.randint(0, 2, size=DNA_SIZE).astype(np.bool)  # 选择交叉点
        parent[cross_points] = pop[i_, cross_points]  # 交叉变异并产生下一代
    return parent


def mutate(child, DNA_SIZE, MUTATION_RATE):
    """
    进行变异
    :param child:
    :return:
    """
    for point in range(DNA_SIZE):
        if np.random.rand() < MUTATION_RATE:
            child[point] = 1 if child[point] == 0 else 0
    return child


def C_M(pop, cross_rate, DNA_SIZE, POP_SIZE, MUTATION_RATE):

    """
    对一个种群进行交叉变异,是上述函数的一个更高层的封装
    :param pop:
    :param cross_rate:
    :param DNA_SIZE:
    :param POP_SIZE:
    :return:
    """
    pop_copy = pop
    for parent in pop:
        child = crossover(parent, pop_copy, cross_rate, POP_SIZE, DNA_SIZE)
        child = mutate(child, DNA_SIZE, MUTATION_RATE)
        parent[:] = child                                       # 子孙代替父辈

    return pop


def initPop(POP_SIZE, DNA_SIZE):
    """
    初始化种群
    :param POP_SIZE:
    :param DNA_SIZE:  网格BIT长度* 网格数量
    :return:
    """
    return np.random.randint(2, size=(POP_SIZE, DNA_SIZE))


def convertPOP2Reseau(pop, reseau_BIT_size, reseau_amount, reseau_bound):
    """
    将种群转为网格
    :param POP:
    :param reseau_BIT_size:
    :param reseau_amount:
    :param reseau_bound:        网格的上下边界，使用“相对价格”的上下边界即可
    :return:
    """

    # 按“网格的BIT长度”对种群进行reshape
    pop_reshape = np.reshape(pop, [-1, reseau_BIT_size])

    # 将二进制翻译为数字
    DNA_SIZE = reseau_BIT_size
    pop_int = ((pop_reshape.dot(2 ** np.arange(DNA_SIZE)[::-1]) / float(2**DNA_SIZE-1))*(np.max(reseau_bound)-np.min(reseau_bound)))\
    +np.min(reseau_bound)

    return np.reshape(pop_int, newshape=[len(pop), -1])


""" ----------------------- 测试 ------------------------------- """
if __name__ == '__main__':

    r_bit_len = 7                           # 网格二进制长度
    r_amount = 6                            # 网格数量

    DNA_SIZE = r_bit_len*r_amount           # DNA 长度
    POP_SIZE = 100                          # 种群大小
    CROSS_RATE = 0.8                        # mating probability (DNA crossover)
    MUTATION_RATE = 0.003                   # mutation probability
    N_GENERATIONS = 200                     # 种群代数
    X_BOUND = [-3, 4]                       # 基因的上下限（此处应该设置为“相对price”的上下限）

    pop = initPop(POP_SIZE, r_bit_len*r_amount)

    pop = C_M(pop, CROSS_RATE, DNA_SIZE, POP_SIZE, MUTATION_RATE)
    pop_int = convertPOP2Reseau(pop=pop, reseau_BIT_size=r_bit_len, reseau_amount=r_amount, reseau_bound=X_BOUND)

    end=0

