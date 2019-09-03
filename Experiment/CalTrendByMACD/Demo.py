# encoding=utf-8

"""
本脚本尝试使用在macd中判断答题趋势
"""

import tushare as ts

from CornerDetectAndAutoEmail.Sub import addStkIndexToDf


stk_df = ts.get_k_data('300508', start='2014-01-01')
stk_df = addStkIndexToDf(stk_df).dropna(how='any', axis=0)

"""
画图代码

"""
stk_df.plot('date', ['close', 'MACD'])

end = 0