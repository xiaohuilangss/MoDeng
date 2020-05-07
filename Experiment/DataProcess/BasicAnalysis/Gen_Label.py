# encoding = utf-8
from sdk.SDKHeader import *


# 本文件用于计算“基本面分析中的label”

# 基本面分析的label，取决于该季度的“价格增长率”减去“其所属类型（上证、深证、创业板）的板块增长率”，
# 再进行分类处理（“大跌”，“中跌”，“微跌”，“微涨”，“中涨”，“大涨”）


#  （一） 计算出各个指数的季度增长率

basic_Q = []

for b_ele in ['sh','sz','cyb','zxb']:

    # 从数据库获取上证数据
    df_b = get_total_table_data(conn_k,'k' + b_ele)

    # 增加季度
    df_b_with_quarter = add_quarter_to_df(df_b)

    # 增加季度增长率
    df_b_Q = get_quarter_growth_ratio_df(df_b_with_quarter)

    basic_Q.append({'b_ele':b_ele,
                    'b_Q':df_b_Q})


# （二）对stk按所在板块进行分类
code_belongto_info = []
for code in g_total_stk_code:
    if str(code)[0] == '6':
        belongto = 'sh'
    elif str(code)[0:2] == '300':
        belongto = 'cyb'
    elif str(code)[0:2] == '002':
        belongto = 'zxb'
    elif str(code)[0] == '0':
        belongto = 'sz'
    else:
        print('遇到不知所属的stk代码，其代码为：'+str(code))
        belongto = ''

    code_belongto_info.append({'code':code,
                               'belongto':belongto})

code_belongto_df = pd.DataFrame(code_belongto_info)

