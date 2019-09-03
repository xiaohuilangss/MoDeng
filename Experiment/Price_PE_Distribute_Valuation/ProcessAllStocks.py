# encoding=utf-8
from CornerDetectAndAutoEmail.TestForDailyInfo import dailyStkInfoEmail, dailyStkInfoEmail_input
# from JQData_Test.auth_info import *
import pandas as pd

from SDK.MyTimeOPT import convert_str_to_date

"""
根据价格pe分数估值法，对所有stk进行估值

"""

stocks = pd.DataFrame({'stk': get_index_stocks('000016.XSHG')}).set_index('stk')


""" ======================= 查询所有stk的市值数据 ========================= """
# 查询300508的市值数据
q = query(valuation.pe_ratio,
              valuation.pb_ratio,
              indicator.eps
            ).filter(valuation.code.in_(stocks))

panel = get_fundamentals_continuously(q, end_date='2019-05-13', count=3000)


""" ============================= 遍历所有stk ============================= """
df_result = pd.DataFrame()

for stk in stocks.index:
    df_close = get_price(stk, start_date='2017-02-13', end_date='2019-05-13', frequency='daily',
                         fields=None, skip_paused=False, fq='pre').tail(300)

    if len(df_close) < 300:
        continue

    # 计算价格分数
    price_now = df_close.tail(1)['close'].values[0]
    price_expensive = list(filter(lambda x: x > price_now, df_close['close']))
    price_scale = len(price_expensive)/len(df_close['close'])*100.0                    # 越高越好

    stocks.loc[stk, 'price_scale'] = price_scale

    # 下载pe数据
    q = query(valuation.pe_ratio,
              valuation.pb_ratio,
              indicator.eps
              ).filter(valuation.code.in_([stk]))

    panel = get_fundamentals_continuously(q, end_date='2019-05-13', count=300)
    try:
        pe_df = panel.minor_xs(stk)
    except:
        continue

    if len(pe_df) < 270:
        continue

    # 计算pe分数
    pe_now = pe_df.tail(1)['pe_ratio'].values[0]
    pe_low = list(filter(lambda x: x < pe_now, pe_df['pe_ratio']))
    pe_scale = len(pe_low) / len(pe_df['pe_ratio']) * 100.0        # 越高越差

    stocks.loc[stk, 'pe_scale'] = pe_scale
    stocks.loc[stk, 'p-pe'] = price_scale - pe_scale

    print('完成 ' + str(stk) + '的计算！')


stocks = stocks.dropna(axis=0)

stk_head = str(list(stocks.sort_values(by='p-pe', ascending=False).head(5).index)).replace('.XSHE', '').replace('.XSHG', '')


print(str(list(stocks.sort_values(by='p-pe', ascending=False).head(20).index)).replace('.XSHE', '').replace('.XSHG', ''))
print(str(list(stocks.sort_values(by='p-pe', ascending=False).head(20)['p-pe'])))

dailyStkInfoEmail_input(stk_head)

"""
['000408', '603858', '600487', '002450', '002352', '601390', '002456', '002044', '300251', '300072', '601618', '601857', '600566', '002024', '601766', '600998', '600023', '300136', '600271', '002415']
[99.66666666666667, 98.33333333333333, 98.33333333333333, 97.66666666666667, 97.33333333333334, 97.0, 95.66666666666666, 93.0, 92.33333333333334, 91.00000000000001, 90.33333333333333, 87.0, 84.33333333333334, 82.33333333333334, 82.00000000000001, 77.0, 74.66666666666666, 73.33333333333333, 72.66666666666667, 72.33333333333334]

"""