# encoding=utf-8
# from JQData_Test.auth_info import *
import pandas as pd

from sdk.MyTimeOPT import convert_str_to_date

from matplotlib import pyplot as plt
import seaborn as sns

"""
使用JQ数据进行研究
"""
stk_code = normalize_code('000001')

# 查询300508的市值数据
q = query(valuation.pe_ratio,
              valuation.pb_ratio,
              indicator.eps,
                indicator.roe,
                indicator.operating_profit,
                  indicator.net_profit_margin,
                  indicator.inc_revenue_annual,
                  indicator.inc_operation_profit_year_on_year,
                  indicator.inc_operation_profit_annual,
                  indicator.inc_net_profit_year_on_year,
                  indicator.inc_net_profit_annual
            ).filter(valuation.code.in_([stk_code]))

panel = get_fundamentals_continuously(q, end_date='2019-05-12', count=1200)
df_basic = panel.minor_xs(stk_code)

df_basic['date_str'] = df_basic.index
df_basic['date'] = df_basic.apply(lambda x: convert_str_to_date(x['date_str']), axis=1)
df_basic = df_basic.set_index('date')

# 查询收盘价
df_close = get_price(stk_code, start_date='2017-01-01', end_date='2019-05-12', frequency='daily', fields=None, skip_paused=False, fq='pre')
df_close = df_close.reset_index()
df_close['date'] = df_close.apply(lambda x: convert_str_to_date(str(x['index'])[:10]), axis=1)
df_close = df_close.set_index('date')

df_concat = pd.concat([df_basic, df_close], axis=1)\
                    .dropna(axis=0)\
                    .loc[:, [
                                            'close',
                                            'eps',
                                            'pb_ratio',
                                            'pe_ratio',
                                            'roe',
                                            'operating_profit',
                                            'net_profit_margin',
                                            'inc_revenue_annual',
                                            'inc_operation_profit_year_on_year',
                                            'inc_operation_profit_annual',
                                            'inc_net_profit_year_on_year',
                                            'inc_net_profit_annual']]

df_corr = df_concat.corr()
# sns.distplot(df_corr['close'])
df_corr['xlabel'] = df_corr.index

# 画条形图
sns.barplot(y='close', x='xlabel', data=df_corr)
plt.xticks(rotation=90)
plt.show()

"""
df_concat.corr()


画图
.corr()
"""

s

"""
#DataFrame的corr和cov方法将以DataFrame的形式返回完整的相关系数或协方差矩阵：
data.corr()
data.cov()
"""

end = 0