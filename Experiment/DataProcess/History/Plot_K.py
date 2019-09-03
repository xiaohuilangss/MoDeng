# encoding = utf-8

from Config.GlobalSetting import *

k_df = get_total_table_data(conn_k,'k002254')

fig, ax = plt.subplots()
xAxis = k_df['date']

ax.plot(xAxis, k_df['close'], 'go--', label=U'close')

# xticklabels = list(k_df['date'])
# xticklabels.reverse()
# ax.set_xticklabels(xticklabels, rotation=90)

xtick = range(0, xAxis.size, 30)
xticklabels = [xAxis[n] for n in xtick]


ax.set_xticks(xtick)
ax.set_xticklabels(xticklabels, rotation=90)


ax.set_title('Kindex')
ax.legend(loc='best')
plt.show()