# encoding=utf-8
import numpy as np

"""
归一化相关函数

"""

def normal01(input):

    max = np.max(input)
    min = np.min(input)

    return list(map(lambda x: (x - min)/(max - min), input))