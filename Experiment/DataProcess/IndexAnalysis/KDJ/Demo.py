# encoding = utf-8

from SDK.SDKHeader import *

import talib


# ----------------------------- 准备测试数据 ---------------------------------------------------------------------

df = get_total_table_data(conn_k,'k300508').sort_values(by='date',ascending=False).head(100).sort_values(by='date',ascending=True)

# ----------------------------- MACD ---------------------------------------------------------------------
# df['MACD'],df['MACDsignal'],df['MACDhist'] = talib.MACD(df.close,
#                             fastperiod=12, slowperiod=26, signalperiod=9)
#
# fig,ax = plt.subplots(nrows=2)
#
# x = range(0,len(df.close))
#
# ax[0].plot(x,df.close,'y*--',label='close')
# ax[1].plot(x,df.MACD,'g--',label='macd')
# ax[1].plot(x,df.MACDsignal,'r--',label='macd-signal')
# ax[1].bar(x,df.MACDhist)
#
# for a in ax:
#     a.legend(loc='best')
#     a.set_xticks(x)
#     a.set_xticklabels(list(df.date), rotation=90)
#
# plt.show()


# ------------------------------------------- RSI ------------------------------------------------------

# df['RSI12']=talib.RSI(df.close, timeperiod=12)
#
#
# fig,ax = plt.subplots(nrows=2)
#
# x = range(0,len(df.close))
#
# ax[0].plot(x,df.close,'go--',label='close')
# ax[1].plot(x,df.RSI12,'r*-',label='RSI12')
#
#
# for a in ax:
#     a.legend(loc='best')
#     a.set_xticks(x)
#     a.set_xticklabels(list(df.date), rotation=90)
#     a.grid(b=True, which='major', axis='x')
# plt.show()

# ------------------------------------------- KDJ ------------------------------------------------------


# df['slowk'], df['slowd'] = talib.STOCH(df.high,
#                                         df.low,
#                                         df.close,
#                                         fastk_period=9,
#                                         slowk_period=3,
#                                         slowk_matype=0,
#                                         slowd_period=3,
#                                         slowd_matype=0)
#
# fig,ax = plt.subplots(nrows=2)
#
# x = range(0,len(df.close))
#
# ax[0].plot(x,df.close,'go--',label='close')
# ax[1].plot(x,df.slowk,'r*-',label='slowk')
# ax[1].plot(x,df.slowd,'y*-',label='slowd')
#
# for a in ax:
#     a.legend(loc='best')
#     a.set_xticks(x)
#     a.set_xticklabels(list(df.date), rotation=90)
#     a.grid(b=True, which='major', axis='x')
# plt.show()


# ------------------------------------------- 布林线 ------------------------------------------------------
upper, middle, lower = talib.BBANDS(
    df.close,
    timeperiod=20,
    # number of non-biased standard deviations from the mean
    nbdevup=2,
    nbdevdn=2,
    # Moving average type: simple moving average here
    matype=0)


fig,ax = plt.subplots(nrows=2)

x = range(0,len(df.close))

ax[0].plot(x,df.close,'go--',label='close')
ax[1].plot(x,upper,'b*--',label='upper')
ax[1].plot(x,middle,'r*-',label='middle')
ax[1].plot(x,lower,'y*-',label='lower')

for a in ax:
    a.legend(loc='best')
    a.set_xticks(x)
    a.set_xticklabels(list(df.date), rotation=90)
    a.grid(b=True, which='major', axis='y')

plt.show()

end = 0

