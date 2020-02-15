# encoding = utf-8
import pandas as pd
import numpy as np

"""
一些与数据处理相关的子函数
"""


def relative_rank(v_total, v_now):
    """
    计算相对排名子函数
    :param v_now:
    :param v_total:
    :param list:
    :return:
    """
    if isinstance(v_total, pd.Series):
        v_total = list(v_total.values)
    else:
        v_total = list(v_total)

    # 去除空值
    v_total = list(filter(lambda x: not pd.isnull(x), v_total))

    if pd.isnull(v_now) | (len(v_total) == 0):
        return np.nan

    # 计算排名
    v_bigger_amount = len(list(filter(lambda x: x < v_now, v_total)))

    return v_bigger_amount/(len(v_total)+0.000001)*100


def normalize(value_param):
    """
    使用最大最小值的方式对数据进行归一化
    :param value_param:
    :return:
    """

    # 转成矩阵
    value_array = np.array(value_param)

    return (value_array-np.min(value_array))/(np.max(value_array) - np.min(value_array))
