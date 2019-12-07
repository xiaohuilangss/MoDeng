# encoding=utf-8

"""
本脚本通过根据布林线动态调整网格大小

"""


import tushare as ts
import talib

from Experiment.RelativeRank.Sub import relativeRank

# def calRSVRank(stk_code, Mdays, history_length=20):
#
#     df = get_k_data_JQ(stk_code, count=history_length, end_date=get_current_date_str())
#
#     # 移动平均线+RSV（未成熟随机值）
#     M = Mdays
#     near_days = 9
#
#     df['low_M'+str(M)] = df['low'].rolling(window=M).mean()
#     df['high_M'+str(M)] = df['high'].rolling(window=M).mean()
#     df['close_M'+str(M)] = df['close'].rolling(window=M).mean()
#
#     df['low_M'+str(M)+'_min'] = df['low_M'+str(M)].rolling(window=M).min()
#     df['high_M'+str(M)+'_max'] = df['high_M'+str(M)].rolling(window=M).max()
#
#     df['RSV'] = df.apply(lambda x: (x['close_M'+str(M)] - x['low_M'+str(M)+'_min'])/(x['high_M'+str(M)+'_max'] - x['low_M'+str(M)+'_min']), axis=1)
#
#     df['RSV_abs'] = df.apply(lambda x: (x['close_M'+str(M)] - x['low_M'+str(M)+'_min']), axis=1)
#     df['RSV_Rank'] = df.apply(lambda x: relativeRank(df['RSV_abs'], x['RSV_abs']), axis=1)
#
#     return df.tail(1)['RSV_Rank'].values[0]



"""
df.plot('date', ['close', 'RSV'], subplots=True,style=['*--', '*--'])
"""


if __name__ == '__main__':

    stk_code = '300508'

    df = ts.get_k_data(stk_code, start='2017-01-12', end='2019-05-26')

    closed = df['close'].values
    df['upper'], df['middle'], df['lower'] = talib.BBANDS(closed, timeperiod=10,
                                                          # number of non-biased standard deviations from the mean
                                                          nbdevup=2,
                                                          nbdevdn=2,
                                                          # Moving average type: simple moving average here
                                                          matype=0)

    df = df.dropna(how='any', axis=0)

    """
    画图语句
    df.plot('date', ['upper', 'lower', 'high', 'low'], style=['-', '-', '*', '*'])

    """

    # 计算短期波动率（3天）
    near_days = 3
    df['low_near'] = df['low'].rolling(window=near_days).min()
    df['high_near'] = df['high'].rolling(window=near_days).max()

    df['wave_near'] = df.apply(lambda x: x['high_near'] - x['low_near'], axis=1)

    df['wave_near_rank'] = df.apply(lambda x: 100 - relativeRank(df['wave_near'], x['wave_near']), axis=1)
    """
    df.plot('date', ['close', 'wave_near_rank', 'wave_near'], style=['--*', '--*'], subplots=True)
    """

    """
    如何调节买卖比例：

    用移动均线-未成熟随机值（RSV）来对买卖比例进行分配，
    实现在上涨时，易买难卖，在下跌时，易卖难买，最终能够实现随着趋势线调整仓位重心的目的。
    避免在迅速下跌时爆仓，在迅速上涨时空仓的情况。
    """

    #
    # def updateRSVRecord():
    #     try:
    #         (conn_opt, engine_opt) = genDbConn(localDBInfo,  'stk_opt_info')
    #         df = pd.read_sql(con=conn_opt, sql='select * from now')
    #
    #         # global  RSV_Record
    #         if not df.empty:
    #             for idx in df.index:
    #                 RSV_Record[stk_code] = calRSVRank(df.loc[idx, 'stk_code'], 5)
    #     except:
    #         send_qq('影子2', 'RSV数据更新失败！')

    """
    如何衡量中期波动（一个月）
    用这一个月的收盘价标准差/一个月收盘价的均值
    """

    mid_days = 3
    df['close_mean_mid'] = df['close'].rolling(window=mid_days).mean()
    df['close_std_mid'] = df['close'].rolling(window=mid_days).std()

    df['wave_mid'] = df.apply(lambda x: x['close_std_mid'] / x['close_mean_mid'], axis=1)

    """
    df.plot('date', ['close', 'wave_mid'], subplots=True, style=['*--', '*--'])
    """

    end = 0