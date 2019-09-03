# encoding=utf_8


"""
本脚本用于研究stk价格在一定时期内所处的位置
"""

import tushare as ts

stk = ts.get_k_data('300508', start='2012-01-01').reset_index()


win_size = 180

for idx in stk.index:

    price_now = stk.loc[idx, 'close']

    se = stk.loc[idx-win_size:idx, 'close']
    price_expensive = list(filter(lambda x: x < price_now, se))

    stk.loc[idx, 'price_scale'] = len(price_expensive)/len(se)*100.0        # 越高越好

stk.loc[win_size:, :].plot('date', ['close', 'price_scale'], subplots=True)

end = 0
# stk.rooling()