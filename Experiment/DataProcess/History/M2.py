# encoding=utf-8
import matplotlib.pyplot as plt
import tushare as ts

from sdk.SDKHeader import *

money_supply_df = ts.get_money_supply()[0:30]
money_supply_df['month_std'] = money_supply_df.apply(lambda x:stdMonthDate(x['month']),axis=1)
money_supply_df = money_supply_df.sort_values(by='month_std',ascending=True)
sh_index = ts.get_hist_data('sh')


# trick to get the axes
fig, ax = plt.subplots(2,1)

# std month date str
month_date = list(map(lambda x:stdMonthDate(x),money_supply_df['month']))
x = range(0,len(money_supply_df['month']))
# plot data
ax[0].plot(x, list(map(lambda x:float(x),money_supply_df['m2_yoy'])), 'ro--', label='m2_yoy')
ax[0].plot(x, list(map(lambda x:float(x),money_supply_df['m1_yoy'])), 'b*--', label='m1_yoy')
ax[0].plot(x, list(map(lambda x:float(x),money_supply_df['m0_yoy'])), 'g*--', label='m0_yoy')
# ax[1].plot(sh_index.index,sh_index.open,'y*--',label='sh_index')

# make and set ticks and ticklabels
ticklabels_0 = month_date
ax[0].set_xticks(x)
ax[0].set_xticklabels(ticklabels_0,rotation=90)
ax[0].set_title('money_supply')
ax[0].legend(loc='best')
ax[0].grid()
tick1 = range(0,sh_index.index.size,30)
ticklabels_1 = [sh_index.index[n] for n in tick1]

ax[1].set_xticks(tick1)
ax[1].set_xticklabels(ticklabels_1,rotation=90)
# plt.sca(ax[1])
# plt.xticks(ticklabels_1,30)

# show the figure
plt.show()
end = 0