# encoding=utf-8

"""
本脚本用来分析一个行业中龙头股与非龙头股的走势区别
"""

# from JQData_Test.JQ_Industry_Analysis_Sub import plt,jqdatasdk,np
# from JQData_Test.auth_info import *
import jqdatasdk
import numpy as np
from pylab import *


# 下载医药板块的所有stk
stk_list_yiyao = jqdatasdk.get_industry_stocks(industry_code='801150')

# 下载该板块所有stk的close数据
df_yiyao = jqdatasdk.get_price(stk_list_yiyao, start_date='2010-01-01', end_date='2018-10-01', frequency='daily')
df_yiyao_close = df_yiyao['close']

# 龙头股与非龙头股
longtou = ['601607.XSHG','000623.XSHE']
nolongtou = [x for x in stk_list_yiyao if x not in longtou]

# 非龙头每支stk起始投资1000块
for stk in nolongtou:
    df_yiyao_close[stk + '_std'] = df_yiyao_close.apply(lambda x: x[stk] * (1000 / df_yiyao_close.head(1)[stk].values[0]), axis=1)

# 龙头股进行投资
for stk in longtou:
    df_yiyao_close[stk + '_std'] = df_yiyao_close.apply(
        lambda x: x[stk] * (1000*(len(nolongtou)/len(longtou)) / df_yiyao_close.head(1)[stk].values[0]), axis=1)


# 求取非龙头的效益和龙头的效益
df_yiyao_close['nolongtou'] = df_yiyao_close.apply(lambda x:np.sum(x[m] for m in nolongtou),axis=1)
df_yiyao_close['longtou'] = df_yiyao_close.apply(lambda x:np.sum(x[m] for m in longtou),axis=1)

# 生成图片
fig, ax = plt.subplots()
industry_name = '医药'
# 画行业龙头
ax.plot(df_yiyao_close.index, df_yiyao_close['longtou'], 'g--', label='龙头股')

# 画沪深300
ax.plot(df_yiyao_close.index, df_yiyao_close['nolongtou'], 'r--', label='其他')

ax.legend(loc='best')
ax.set_title(industry_name + '行业龙头与非龙头股对比')
plt.savefig('./longtou_pic_compare/' + industry_name + '.png')