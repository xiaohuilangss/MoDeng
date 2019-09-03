# encoding=utf-8

from JQData_Test.JQ_Industry_Analysis_Sub import *

# 年份列表
year_list = list(range(2010,2018))


# 获取申万一级行业分类
indus = jqdatasdk.get_industries(name='sw_l1')

indus_dic = [{'indus_code': x,
              'indus_name': indus.loc[x, 'name'],
              'indus_stk': jqdatasdk.get_industry_stocks(industry_code=x)
              } for x in indus.index]

# 向字典列表中增加各行业所含stk的数据，df格式
for dic in indus_dic:
    dic['stk_df_list'] = [get_indus_stk_df(dic['indus_stk'], x) for x in year_list]
    dic['net_profit_list'] = [x['net_profit'].sum() for x in dic['stk_df_list']]

    # 将增长曲线图打印
    plot(dic['indus_name'], dic['net_profit_list'], year_list)


# 获取行业中的龙头股，以净利润为指标
df_list = get_indus_stk_df(jqdatasdk.get_industry_stocks(industry_code='801180'), 2010)
df_list.sort_values(by='net_profit', ascending=False).head(3).loc[:, 'code'].values

# 获取房地产的三大龙头与沪深300指数的close数据
df = jqdatasdk.get_price(['000002.XSHE', '600048.XSHG', '000069.XSHE', '000300.XSHG'], start_date='2010-01-01', end_date='2018-10-01', frequency='daily')

df_close = df['close']

# 沪深300年初10年年初买进3000块，其收益走势如下
df_close['000300.XSHG_std'] = df_close.apply(lambda x: x['000300.XSHG']*(3000/3535.2290), axis=1)


# 每支stk起始投资1000块
for stk in ['000002.XSHE', '600048.XSHG', '000069.XSHE']:
    df_close[stk+'_std'] = df_close.apply(lambda x: x[stk]*(1000/df_close.head(1)[stk].values[0]), axis=1)


# 求取个股收益情况之和
df_close['stk_sum'] = df_close.apply(lambda x:np.sum([x[stk_code+'_std'] for stk_code in ['000002.XSHE', '600048.XSHG', '000069.XSHE']]),axis=1)


end = 0