# encoding = utf-8
from jqdatasdk import query, valuation, income
from Config.GlobalSetting import *
# from JQData_Test.auth_info import *
import jqdatasdk

def get_indus_stk_df(stk_list, year):

    return jqdatasdk.get_fundamentals(query(
              valuation, income
          ).filter(
              # 这里不能使用 in 操作, 要使用in_()函数
              valuation.code.in_(stk_list)
          ), statDate=year)


def plot(indus_name, data_list, year_list):

    fig, ax = plt.subplots()
    ax.plot(year_list,data_list,'g*--')
    ax.set_title(indus_name + ' 行业 年度 总净利润')
    plt.savefig('./indus_pic_dir/'+indus_name+'.png')


def indus300_compare(stk_list):
    """
    函数功能：处理沪深300与行业龙头股的数据
    :param stk_list: 例子['000002.XSHE', '600048.XSHG', '000069.XSHE','000300.XSHG']
    :return:
    """

    stk_all = stk_list + ['000300.XSHG']


    # 获取房地产的三大龙头与沪深300指数的close数据

    df = jqdatasdk.get_price(stk_all, start_date='2010-01-01', end_date='2018-10-01', frequency='daily')
    df_close = df['close']


    # 沪深300年初10年年初买进3000块，其收益走势如下
    df_close['000300.XSHG_std'] = df_close.apply(lambda x:x['000300.XSHG']*(len(stk_list)*1000/df_close.head(1)['000300.XSHG'].values[0]), axis=1)


    # 每支stk起始投资1000块
    for stk in stk_list:
        df_close[stk+'_std'] = df_close.apply(lambda x:x[stk]*(1000/df_close.head(1)[stk].values[0]), axis=1)


    # 求取个股收益情况之和
    df_close['stk_sum'] = df_close.apply(lambda x:np.sum([x[stk_code+'_std'] for stk_code in stk_list]),axis=1)


    return df_close


def indus300_compare_ts(stk_list):
    """
    函数功能：处理沪深300与行业龙头股的数据
    :param stk_list: 例子['000002.XSHE', '600048.XSHG', '000069.XSHE','000300.XSHG']
    :return:
    """

    stk_all = stk_list + ['000300.XSHG']


    # 获取房地产的三大龙头与沪深300指数的close数据
    try:
        df = jqdatasdk.get_price(stk_all, start_date='2010-01-01', end_date='2018-10-01', frequency='daily')
        df_close = df['close']
    except:
        stk_all = stk_list + ['hs300']
        stk_df_list = [ts.get_k_data(stk.split('.')[0]).rename(columns={'close': stk}).loc[:, ['date', stk]].set_index('date') for stk in stk_all]
        df_close = pd.concat(stk_df_list, axis=1).dropna(how='any').rename(columns={'hs300.XSHG': '000300.XSHG'})

    # 沪深300年初10年年初买进3000块，其收益走势如下
    df_close['000300.XSHG_std'] = df_close.apply(lambda x: x['000300.XSHG']*(len(stk_list)*1000/df_close.head(1)['000300.XSHG'].values[0]), axis=1)


    # 每支stk起始投资1000块
    for stk in stk_list:
        df_close[stk+'_std'] = df_close.apply(lambda x:x[stk]*(1000/df_close.head(1)[stk].values[0]), axis=1)


    # 求取个股收益情况之和
    df_close['stk_sum'] = df_close.apply(lambda x:np.sum([x[stk_code+'_std'] for stk_code in stk_list]),axis=1)


    return df_close


def plot_industry(industry_df,industry_name):
    """
    函数功能：展示一个行业的龙头stk与沪深300的对比，起始时都买进3000块
    :param industry_df:   函数indus300_compare(stk_list)的处理结果
    :param data_list:
    :param year_list:
    :return:
    """



    fig, ax = plt.subplots()

    # 画行业龙头
    ax.plot(industry_df.index, industry_df['stk_sum'], 'g--',label=industry_name+' 行业龙头股')

    # 画沪深300
    ax.plot(industry_df.index, industry_df['000300.XSHG_std'], 'r--', label='同时期的沪深300')

    ax.legend(loc='best')
    ax.set_title(industry_name + '行业龙头与沪深300对比')
    plt.savefig('./indus_pic_compare/'+industry_name+'.png')


# --------------------------- 测试 --------------------------------


# df_fdc = indus300_compare(['601607.XSHG','000623.XSHE]'])
# plot_industry(df_fdc,'医药生物')
#
# end = 0