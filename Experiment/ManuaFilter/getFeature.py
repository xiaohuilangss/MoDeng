# encoding=utf-8

"""
这个脚本主要用来提取一直stk，包括指数的“天”、“周”和“月”级别的数据，用来取出一支stk的特征。

天的数据不需要进行修改

周和月需要进行处理

这里面有需要考虑的一点，直接使用间隔进行处理，比如7个数据中取一个，还是用实际的数据处理。

第一种方式：如果中间有放假或者停盘，会导致数据错误。

第二种方式：

这就意味着，如果stk有停盘情况时，会导致不准确的情况。
"""
import talib
import tushare as ts

from pylab import *
from sdk.MyTimeOPT import convert_str_to_datetime

single_stk = ts.get_k_data('300508')

# 添加时间列
single_stk['datetime'] = single_stk.apply(lambda x: convert_str_to_datetime(x['date'] + ' 00:00:00'), axis=1)
single_stk = single_stk.set_index(keys='datetime')

# 按周采样并计算MACD
single_stk_W = single_stk.resample('W').bfill()
single_stk_W['MACD'], single_stk_W['MACDsignal'], single_stk_W['MACDhist'] = talib.MACD(single_stk_W.close,
                                fastperiod=12, slowperiod=26, signalperiod=9)

# 按月采样并计算MACD
single_stk_M = single_stk.resample('M').bfill()
single_stk_M['MACD'], single_stk_M['MACDsignal'], single_stk_M['MACDhist'] = talib.MACD(single_stk_M.close,
                                fastperiod=12, slowperiod=26, signalperiod=9)


fig, ax = plt.subplots()
ax.bar(single_stk_W.index, single_stk_W['MACD'])
plt.savefig('./Pic_Temp/test1.png')

end=0