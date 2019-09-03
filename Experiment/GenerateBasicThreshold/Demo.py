# encoding=utf-8

"""
用来根据stk走势及波动情况，指定基本的操作仓位阈值
"""

import tushare as ts
import numpy as np
stk_code = '300508'
win = 5
# def gen_sig_win_info(stk_code, win):

df = ts.get_k_data(stk_code, start='2010-10-01')

df = df.reset_index()
for idx in df.loc[win:, :].index:
    df_slice = df.loc[idx - win:idx, :]

    df_slice = df_slice.reset_index().loc[:, ['close', 'open', 'high', 'low']]
    df_slice['x'] = df_slice.index

    k = (df_slice.head(1)['open'].values[0] - df_slice.tail(1)['close'].values[0]) / \
        (df_slice.head(1)['x'].values[0] - df_slice.tail(1)['x'].values[0])

    b = df_slice.tail(1)['close'].values[0] - k * df_slice.tail(1)['x'].values[0]

    # 根据拟合的直线，求取每个点到直线的误差
    df_slice['line_fit'] = df_slice.apply(lambda x: x['x'] * k + b, axis=1)

    # 计算每天的高低点与直线的均方差
    df_slice['err2'] = df_slice.apply(lambda x: (x['high'] - x['line_fit']) ** 2 + (x['low'] - x['line_fit']) ** 2,
                                      axis=1)

    # 计算波动量
    err_total = np.sum(df_slice['err2'])

    # 求这段时间的最大最小值之差
    nd_values = df_slice.loc[:, ['close', 'open', 'high', 'low']].values
    p_max = np.max(nd_values)
    p_min = np.min(nd_values)

    diff_p = p_max - p_min

    # 保存波动幅度和波动量
    df.loc[idx, 'std'] = err_total
    df.loc[idx, 'diff_p'] = diff_p

    # return err_total, diff_p


end = 0



