# encoding = utf-8

from SDK.SDKHeader import *

"""
    画出“最高点”、“最低点”的图像
"""

df = get_total_table_data(conn_k, 'k300508')

fig,ax = plt.subplots()

x_axis = range(0,len(df.close))
ax.plot(x_axis, df.low, 'r--', label='low', linewidth=0.5, markersize=1)
ax.plot(x_axis, df.high, 'b--', label='high', linewidth=0.5, markersize=1)
ax.plot(x_axis, df.close, 'g--', label='close', linewidth=0.5, markersize=1)

ax.set_xticks(x_axis)
xticklabels = list(df['date'].sort_values(ascending=True))
ax.set_xticklabels(xticklabels, rotation=90, fontsize=3)

plt.show()

end = 0