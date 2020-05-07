# encoding=utf-8
import tushare as ts
import numpy as np
from pylab import *
from sdk.PlotOptSub import add_axis

mpl.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False

"""
用于研究 每日 最高值、最低值、收盘价 与20日均线的关系
"""

stk_code = '000001'
sh_index = ts.get_k_data(code=stk_code,start='2014-01-01')

sh_index['M10'] = sh_index['close'].rolling(window=10, center=False).mean()
sh_index['C-M10'] = sh_index.apply(lambda x: x['close']-x['M10'], axis=1)

sh_index['M20'] = sh_index['close'].rolling(window=20, center=False).mean()
sh_index['C-M20'] = sh_index.apply(lambda x: x['close']-x['M20'], axis=1)

sh_index = sh_index.dropna(how='any')

# 展示C-M20的分布
count, bins = np.histogram(sh_index['C-M20'], 100, normed=True)
plt.bar(range(len(count)), count)

plt.show()
fig, ax = plt.subplots(nrows=2, ncols=1)

ax[0].plot(range(0, len(sh_index['date'])), sh_index['close'], 'r-', label='20日均线', linewidth=1)
ax[1].plot(range(0, len(sh_index['date'])), sh_index['C-M20'], 'g*', label='C-20日均线', linewidth=1)
ax[1].plot(range(0, len(sh_index['date'])), np.zeros(len(sh_index)), 'b', label='零线')

# 准备下标
ax[0] = add_axis(ax[0], sh_index['date'], 40)
ax[1] = add_axis(ax[1], sh_index['date'], 40)

for ax_sig in ax:
    ax_sig.legend(loc='best')

plt.show()
