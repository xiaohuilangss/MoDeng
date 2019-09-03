#encoding=utf-8

"""
本脚本用来测试

时间、
连续相同操作次数、
剩余量

约束的方法！
"""
import numpy as np
import math

"""
1、连同次数约束使用log函数实现：
--------------------------------
设 连同次数为x（连同次数最小为1！），则本次网格大小为：

原始网格 * log(x-1) * 调节因子（暂定为1）

2、时间约束方法为：
-------------------
设 距离上次操作的时间为x

则时间约束系数为：
1+(1/x)*time_w

效果，随着时间的推移，时间约束效果逐渐消失！


3、剩余量约束：
----------------

将当前stk换算成当前cap，与剩余cap做和！，求总cap！

a = 当前剩余cap/总cap * 调节系数
remain_w:调节系数

reseau_b = reseau_b*a*remain_w
reseau_s = reseau_b*/a*remain_w

"""


def sigmod(x):
    return 1/(1+math.exp(-x))


def calBSReseau(reseau_origin, m_remain_ratio, time_span,  continus_amount_b, continus_amount_s, m_w, t_w, c_w):
    """

    :param reseau_origin:       初始格子大小
    :param m_remain_ratio:      m剩余比例
    :param m_w:                 剩余m调节系数
    :param time_span:           时间间隔（BS操作通用）
    :param t_w:                 时间间隔调节系数
    :param continus_amount_b:   b 连续次数
    :param continus_amount_s:   s 连续次数
    :param c_w:                 连续次数调节系数
    :return:
    """

    reseau_b = reseau_origin \
               * math.exp(continus_amount_b*c_w) \
               * (0.2+(1/(time_span*t_w))*5) \
               * 0.5/(m_remain_ratio + 0.000001) * m_w

    reseau_s = reseau_origin \
               * math.exp(continus_amount_s*c_w) \
               * (0.2+(1/(time_span*t_w))*5) \
               * m_remain_ratio*2 * m_w

    return reseau_b, reseau_s


if __name__ == '__main__':

    r = calBSReseau(
        reseau_origin=0.5,
        m_remain_ratio=0.5,
        time_span=200,
        continus_amount_b=3,
        continus_amount_s=1,
        m_w=1,
        t_w=1,
        c_w=1)

    end = 0
