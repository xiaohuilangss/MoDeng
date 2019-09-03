# encoding = utf-8
# from JQData_Test.auth_info import *

"""
本脚本测试行业估值方面的内容

"""

"""
接口说明：

1、行业估值：
---------------

字段名称	                    中文名称	    字段类型	    能否为空	注释
date	                        交易日	        date	        N	
code	                        指数编码	    varchar(12)	    N	        对应申万一级行业指数编码
name	                        指数名称	    varchar(20)	    N	
turnover_ratio	                换手率	        decimal(10,4)		        单位：％
pe	                            市盈率	        decimal(20,4)		        单位：倍；PE = 流通市值／最近4个季度的净利润；最近 4 个季度的净利润按如下方法计算: 1-4 月,最近 4 个季度的净利润=上一年度前 3 季度累计净利润+上上一年度的四季度净利润；5-8 月,最近 4 个季度的净利润=当年 1 季度净利润+前 1 年净利润-前 1 年 1 季度净利润；9-10 月,最近 4 个季度的净利润=当年中期净利润+前 1 年净利润-前 1 年中期净利润；11-12 月,最近 4 个季度的净利润=当年前 3 季度累计净利润+上1年年度净利润-上 1 年前 3 季度累计净利润
pb	                            市净率	        decimal(20,4)		        单位：倍；按照自由流通量加权的净资产倍率。 PB = 流通市值／按照流通市值计算的净资产；按照流通市值计算的净资产 ＝ 最新净资产*流通股本／总股本
average_price	                均价	        decimal(20,4)		        单位：元。指数成份股在统计期最后交易日收盘的简单算术平均价
money_ratio	                    成交额占比	    decimal(10,4)		        单位：％；成交额占比＝某个行业成交额／所有行业成交额之和
circulating_market_cap	        流通市值	    decimal(20,4)		        单位：元
average_circulating_market_cap	平均流通市值	decimal(20,4)		        单位：元；平均流通市值＝流通市值／所在行业stk数
dividend_ratio	                股息率	        decimal(10,4)		        单位：％；按照自由流通量加权的现金股息率；dividend_ratio=Df/Vf；Df: 所有stk在截止日的一 个自然年(365日)中所累积派发的税前现金红利之和按照流通股本对应的分红量；Vf: 该行业成分股股的流通市值之和


2、查询stk所属行业
----------------------

#获取贵州茅台("600519.XSHG")的所属行业数据
d = get_industry("600519.XSHG",date="2018-06-01")
print(d)


"""

# 获取贵州茅台("600519.XSHG")的所属行业数据
d = get_industry("300508.XSHE", date="2019-05-01")
print(d)

df = finance.run_query(query(finance.SW1_DAILY_VALUATION).filter(finance.SW1_DAILY_VALUATION.code=='801010').limit(10))
print(df)
