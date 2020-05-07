# encoding = utf-8

from sdk.SDKHeader import *
import talib


# 获取原始数据
stk_df = get_total_table_data(conn_k,'ksh').loc[0:600,:]

# 计算均值
stk_df['close_5'] = stk_df['close'].rolling(window=5).mean()
stk_df['close_20'] = stk_df['close'].rolling(window=10).mean()

# 求20日均线导数
stk_df["M20_Diff"] = stk_df['close_20'] - stk_df['close_20'].shift(1)
stk_df["M20_Diff2"] = stk_df['M20_Diff'] - stk_df['M20_Diff'].shift(1)


stk_df['close_90'] = stk_df['close'].rolling(window=90).mean()


stk_df['C20-C90'] = stk_df['close_20'] - stk_df['close_90']
stk_df['20-90Diff'] = stk_df['C20-C90'] - stk_df['C20-C90'].shift(1)

stk_df['MACD'],stk_df['MACDsignal'],stk_df['MACDhist'] = talib.MACD(stk_df.close,
                            fastperiod=12, slowperiod=26, signalperiod=9)

stk_df['MACD_M5'],stk_df['MACDsignal_M20'],stk_df['MACDhist_M20'] = talib.MACD(stk_df.close_5,
                            fastperiod=12, slowperiod=26, signalperiod=9)

stk_df['RSI12'] = talib.RSI(stk_df.close, timeperiod=12)



# 将控制填0方便对其
stk_df = stk_df.fillna(0)

fig,ax = subplots(ncols=1,nrows=2)

ax[0].plot(stk_df['close'],'g*--',label='close',linewidth=0.5,markersize=1)
ax[0].plot(stk_df['close_20'],'r*--',label='close_20',linewidth=0.5,markersize=1)
ax[0].plot(stk_df['close_90'],'y*--',label='close_90',linewidth=0.5,markersize=1)
ax[0].grid()


# ax[1].plot(stk_df['MACD'],'r*--',label='MACD',linewidth=0.5,markersize=1)
# ax[1].plot(stk_df['RSI12'],'r*--',label='RSI12',linewidth=0.5,markersize=1)
# ax[1].bar(range(0,len(stk_df['MACD'])),stk_df['MACD_M5'])
# ax[1].plot(stk_df['M20_Diff'],'y*--',label='RSI12',linewidth=0.5,markersize=2)
# ax[1].plot(stk_df['M20_Diff2'],'r*--',label='RSI12',linewidth=0.5,markersize=2)
# ax[1].bar(range(0,len(stk_df['M20_Diff2'])),stk_df['M20_Diff2'])

# ax[1].plot(stk_df['close_20'] - stk_df['close_90'],'y*--',label='RSI12',linewidth=0.5,markersize=2)

# ax[1].plot(stk_df['close'] - stk_df['close_20'],'r*--',label='close_diff',linewidth=0.5,markersize=1)
ax[1].plot(stk_df['C20-C90'],'r*--',label='close_diff',linewidth=0.5,markersize=1)


ax[1].grid()

plt.show()

end = 0
