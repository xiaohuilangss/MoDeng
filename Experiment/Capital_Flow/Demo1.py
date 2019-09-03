# encoding=utf-8

from jqdatasdk import *

import numpy as np
import tushare as ts

"""
字段名	                含义	                备注

date	                日期	
sec_code	            stk代码	
change_pct	            涨跌幅(%)	
net_amount_main	        主力净额(万)	        主力净额 = 超大单净额 + 大单净额
net_pct_main	        主力净占比(%)	        主力净占比 = 主力净额 / 成交额
net_amount_xl	        超大单净额(万)	        超大单：大于等于50万股或者100万元的成交单
net_pct_xl	            超大单净占比(%)	        超大单净占比 = 超大单净额 / 成交额
net_amount_l	        大单净额(万)	        大单：大于等于10万股或者20万元且小于50万股或者100万元的成交单
net_pct_l	            大单净占比(%)	        大单净占比 = 大单净额 / 成交额
net_amount_m	        中单净额(万)	        中单：大于等于2万股或者4万元且小于10万股或者20万元的成交单
net_pct_m	            中单净占比(%)	        中单净占比 = 中单净额 / 成交额
net_amount_s	        小单净额(万)	        小单：小于2万股或者4万元的成交单
net_pct_s	            小单净占比(%)	        小单净占比 = 小单净额 / 成交额
"""

df_flow = get_money_flow('300508.XSHE', '2018-05-01', '2019-06-10')
df_flow_plot = df_flow.loc[:, [x not in ['sec_code'] for x in df_flow.columns.values]]

df_flow_plot['net_total'] = df_flow.apply(lambda x: np.sum([
    x['net_amount_main'],
    x['net_amount_xl'],
    x['net_amount_l'],
    x['net_amount_m'],
    x['net_amount_s']]), axis=1)

df_flow_plot['net_m'] = df_flow_plot['net_total'].rolling(window=5).sum()
df_flow_plot['date_str'] = df_flow_plot.apply(lambda x: str(x['date'])[:10], axis=1)

df_flow_plot = df_flow_plot.set_index(keys='date_str')


# 下载tushare数据
df_t = ts.get_k_data('300508', start='2018-05-01')
df_t = df_t.set_index(keys='')

end = 0

"""
df_flow_plot.plot('date', list(df_flow.columns.values).remove('date'), subplots=True)
df_flow_plot.plot('date', ['change_pct', 'net_total'], subplots=True)

"""
