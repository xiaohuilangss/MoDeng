# encoding=utf-8

# from JQData_Test.auth_info import *
import pandas as pd

from SDK.MyTimeOPT import convert_str_to_date

"""
本脚本用于研究相对估值
"""

"""
接口用法：



字段名	                        含义	                备注
date	                        日期	
sec_code	                    stk代码	
change_pct	                    涨跌幅(%)	
net_amount_main	                主力净额(万)	        主力净额 = 超大单净额 + 大单净额
net_pct_main	                主力净占比(%)	        主力净占比 = 主力净额 / 成交额
net_amount_xl	                超大单净额(万)	        超大单：大于等于50万股或者100万元的成交单
net_pct_xl	                    超大单净占比(%)	        超大单净占比 = 超大单净额 / 成交额
net_amount_l	                大单净额(万)	        大单：大于等于10万股或者20万元且小于50万股或者100万元的成交单
net_pct_l	                    大单净占比(%)	        大单净占比 = 大单净额 / 成交额
net_amount_m	                中单净额(万)	        中单：大于等于2万股或者4万元且小于10万股或者20万元的成交单
net_pct_m	                    中单净占比(%)	        中单净占比 = 中单净额 / 成交额
net_amount_s	                小单净额(万)	        小单：小于2万股或者4万元的成交单
net_pct_s	                    小单净占比(%)	        小单净占比 = 小单净额 / 成交额
"""


# 获取300508所在的通信行业的估值
df = finance.run_query(query(finance.SW1_DAILY_VALUATION).filter(finance.SW1_DAILY_VALUATION.code == '801770'))
df = df.set_index('date').sort_index(ascending=True)

"""
表名: valuation

列名	                                列的含义	                解释	                公式
code	                                stk代码	                带后缀.XSHE/.XSHG	
day	                                    日期	                    取数据的日期	
capitalization	                        总股本(万股)	            公司已发行的普通股股份总数(包含A股，B股和H股的总股本)	
circulating_cap	                        流通股本(万股)	            公司已发行的境内上市流通、以人民币兑换的股份总数(A股市场的流通股本)	
market_cap	                            总市值(亿元)	            A股收盘价*已发行stk总股本（A股+B股+H股）	
circulating_market_cap	                流通市值(亿元)	            流通市值指在某特定时间内当时可交易的流通股股数乘以当时股价得出的流通stk总价值。	A股市场的收盘价*A股市场的流通股数
turnover_ratio	                        换手率(%)	                指在一定时间内市场中stk转手买卖的频率，是反映stk流通性强弱的指标之一。	换手率=[指定交易日成交量(手)100/截至该日stk的自由流通股本(股)]100%
pe_ratio	                            市盈率(PE, TTM)	            每股市价为每股收益的倍数，反映投资人对每元净利润所愿支付的价格，用来估计stk的投资报酬和风险	市盈率（PE，TTM）=（stk在指定交易日期的收盘价 * 当日人民币外汇挂牌价* 截止当日公司总股本）/归属于母公司股东的净利润TTM。
pe_ratio_lyr	                        市盈率(PE)	                以上一年度每股盈利计算的静态市盈率. 股价/最近年度报告EPS	市盈率（PE）=（stk在指定交易日期的收盘价 * 当日人民币外汇牌价 * 截至当日公司总股本）/归属母公司股东的净利润。
pb_ratio	                            市净率(PB)	                每股股价与每股净资产的比率	市净率=（stk在指定交易日期的收盘价 * 当日人民币外汇牌价 * 截至当日公司总股本）/归属母公司股东的权益。
ps_ratio	                            市销率(PS, TTM)	            市销率为stk价格与每股销售收入之比，市销率越小，通常被认为投资价值越高。	市销率TTM=（stk在指定交易日期的收盘价 * 当日人民币外汇牌价 * 截至当日公司总股本）/营业总收入TTM
pcf_ratio	                            市现率(PCF, 现金净流量TTM)	每股市价为每股现金净流量的倍数	市现率=（stk在指定交易日期的收盘价 * 当日人民币外汇牌价 * 截至当日公司总股本）/现金及现金等价物净增加额TTM

"""


# 查询300508的市值数据
q = query(valuation.pe_ratio,
              valuation.pb_ratio,
              indicator.eps
            ).filter(valuation.code.in_(['300508.XSHE']))

panel = get_fundamentals_continuously(q, end_date='2019-05-12', count=1200)
df_basic = panel.minor_xs('300508.XSHE')
df_basic['date_str'] = df_basic.index
df_basic['date'] = df_basic.apply(lambda x: convert_str_to_date(x['date_str']), axis=1)
df_basic = df_basic.set_index('date')

# 查询收盘价
df_close = get_price(normalize_code('300508'), start_date='2017-01-01', end_date='2019-05-12', frequency='daily', fields=None, skip_paused=False, fq='pre')
df_close = df_close.reset_index()
df_close['date'] = df_close.apply(lambda x: convert_str_to_date(str(x['index'])[:10]), axis=1)
df_close = df_close.set_index('date')

df_concat = pd.concat([df, df_basic, df_close], axis=1)\
                    .dropna(axis=0)\
                    .loc[:, ['close', 'pe', 'pb', 'eps', 'pb_ratio', 'pe_ratio']]

df_concat['date'] = df_concat.index

"""
求取相关系数
df_concat.corr()

画图

"""


df_concat['pe_rela'] = df_concat.apply(lambda x: x['pe']-x['pe_ratio'], axis=1)
df_concat['pb_rela'] = df_concat.apply(lambda x: x['pb']-x['pb_ratio'], axis=1)

df_concat['close_pre'] = df_concat.apply(lambda x: x['close']/x['pb_ratio']*x['pb'], axis=1)



"""
画图


"""

end = 0