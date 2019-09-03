# encoding = utf-8

"""

一些与数据处理相关的子函数
"""


def normalize(value_param):
    """
    使用最大最小值的方式对数据进行归一化
    :param value_param:
    :return:
    """

    # 转成矩阵
    value_array = np.array(value_param)

    return (value_array-np.min(value_array))/(np.max(value_array) - np.min(value_array))
