# encoding=utf-8

import tushare as ts

from sdk.BasicAnalysisSub import get_ss_total_basic

"""
测试使用python 下载数据
"""

df = get_ss_total_basic('300508')

end = 0
