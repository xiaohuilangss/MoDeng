# encoding=utf-8

"""
本脚本用于存放测试用函数，主要是debug日志打印函数
"""
from Config.AutoGenerateConfigFile import data_dir
from SDK.MyTimeOPT import get_current_date_str
import os


def debug_print_txt(file_name, stk, value):
    """

    :param file_name:
    :param stk:
    :param value:
    :return:
    """
    file_dir = data_dir + 'Debug_log/' + get_current_date_str()
    file_url = file_dir + '/' + file_name + '_' + stk + '.txt'

    # 如果文件夹不存在，创建
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(file_url, 'a+') as f:
        f.write(value + '\n')




